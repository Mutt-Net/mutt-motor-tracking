from flask import Blueprint, request, jsonify, send_from_directory
from backend.extensions import db
from backend.models import Vehicle, Maintenance, Mod, Cost, Note, VCDSFault, Guide, VehiclePhoto, FuelEntry, Reminder
from datetime import datetime, timezone
import json
import os
import uuid

routes = Blueprint('routes', __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads')
UPLOAD_FOLDER = os.path.normpath(UPLOAD_FOLDER)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'}

def allowed_file(filename):
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    return ext in ALLOWED_EXTENSIONS

def secure_filename_with_ext(filename):
    if not filename or '.' not in filename:
        ext = ''
    else:
        ext = filename.rsplit('.', 1)[1].lower()
    return f"{uuid.uuid4().hex}.{ext}" if ext else f"{uuid.uuid4().hex}"

def validate_filename(filename):
    if not filename:
        return False
    filename = os.path.basename(filename)
    if '..' in filename or filename.startswith('/') or filename.startswith('\\'):
        return False
    if any(c in filename for c in ['\x00', '\n', '\r']):
        return False
    return True

SERVICE_INTERVALS = {
    'oil_change': {'miles': 5000, 'months': 6},
    'brakes': {'miles': 20000, 'months': 24},
    'tire_rotation': {'miles': 7500, 'months': 6},
    'inspection': {'miles': 15000, 'months': 12},
    'transmission': {'miles': 30000, 'months': 24},
    'coolant': {'miles': 30000, 'months': 24},
    'spark_plugs': {'miles': 30000, 'months': 36},
    'air_filter': {'miles': 15000, 'months': 12},
    'fuel_filter': {'miles': 30000, 'months': 24}
}

def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None

def validate_required(data, required_fields):
    missing = [f for f in required_fields if not data.get(f)]
    if missing:
        return f"Missing required fields: {', '.join(missing)}"
    return None

def validate_positive_integer(value, field_name):
    if value is None:
        return None
    try:
        int_val = int(value)
        if int_val < 0:
            return f"{field_name} must be a positive integer"
        return None
    except (ValueError, TypeError):
        return f"{field_name} must be a valid integer"

def validate_year(value):
    if value is None:
        return None
    try:
        year = int(value)
        if year < 1900 or year > 2100:
            return "Year must be between 1900 and 2100"
        return None
    except (ValueError, TypeError):
        return "Year must be a valid integer"

def validate_id(value, field_name='ID'):
    if value is None:
        return f"{field_name} is required"
    try:
        int_val = int(value)
        if int_val <= 0:
            return f"{field_name} must be a positive integer"
        return None
    except (ValueError, TypeError):
        return f"{field_name} must be a valid integer"

def serialize_vehicle(v):
    return {
        'id': v.id, 'name': v.name, 'reg': v.reg, 'vin': v.vin, 'year': v.year,
        'make': v.make, 'model': v.model, 'engine': v.engine, 
        'transmission': v.transmission, 'mileage': v.mileage
    }

@routes.route('/vehicles', methods=['GET'])
def get_vehicles():
    vehicles = Vehicle.query.all()
    return jsonify([serialize_vehicle(v) for v in vehicles])

@routes.route('/vehicles', methods=['POST'])
def add_vehicle():
    data = request.json or {}
    error = validate_required(data, [])
    if error:
        return jsonify({'error': error}), 400
    
    year_error = validate_year(data.get('year'))
    if year_error:
        return jsonify({'error': year_error}), 400
    
    mileage_error = validate_positive_integer(data.get('mileage'), 'mileage')
    if mileage_error:
        return jsonify({'error': mileage_error}), 400
    
    vehicle = Vehicle(
        name=data.get('name'), reg=data.get('reg'), vin=data.get('vin'), year=data.get('year'),
        make=data.get('make'), model=data.get('model'),
        engine=data.get('engine'), transmission=data.get('transmission'),
        mileage=data.get('mileage', 0)
    )
    db.session.add(vehicle)
    db.session.commit()
    return jsonify({'id': vehicle.id}), 201

@routes.route('/vehicles/<int:id>', methods=['GET'])
def get_vehicle(id):
    vehicle = db.session.get(Vehicle, id)
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404
    return jsonify(serialize_vehicle(vehicle))

@routes.route('/vehicles/<int:id>', methods=['PUT'])
def update_vehicle(id):
    vehicle = db.session.get(Vehicle, id)
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404
    
    data = request.json or {}
    
    if 'year' in data:
        year_error = validate_year(data.get('year'))
        if year_error:
            return jsonify({'error': year_error}), 400
    
    if 'mileage' in data:
        mileage_error = validate_positive_integer(data.get('mileage'), 'mileage')
        if mileage_error:
            return jsonify({'error': mileage_error}), 400
    
    for key in ['name', 'reg', 'vin', 'year', 'make', 'model', 'engine', 'transmission', 'mileage']:
        if key in data:
            setattr(vehicle, key, data[key])
    db.session.commit()
    return jsonify({'success': True})

@routes.route('/vehicles/<int:id>', methods=['DELETE'])
def delete_vehicle(id):
    vehicle = db.session.get(Vehicle, id)
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404
    db.session.delete(vehicle)
    db.session.commit()
    return jsonify({'success': True})

@routes.route('/vehicles/<int:id>/export', methods=['GET'])
def export_vehicle(id):
    vehicle = db.session.get(Vehicle, id)
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404
    
    maintenance = Maintenance.query.filter_by(vehicle_id=id).all()
    mods = Mod.query.filter_by(vehicle_id=id).all()
    costs = Cost.query.filter_by(vehicle_id=id).all()
    notes = Note.query.filter_by(vehicle_id=id).all()
    faults = VCDSFault.query.filter_by(vehicle_id=id).all()
    fuel_entries = FuelEntry.query.filter_by(vehicle_id=id).all()
    reminders = Reminder.query.filter_by(vehicle_id=id).all()
    
    return jsonify({
        'vehicle': serialize_vehicle(vehicle),
        'maintenance': [{'date': m.date.isoformat() if m.date else None, 'mileage': m.mileage, 'category': m.category, 'description': m.description, 'cost': m.cost, 'notes': m.notes} for m in maintenance],
        'mods': [{'date': m.date.isoformat() if m.date else None, 'mileage': m.mileage, 'category': m.category, 'description': m.description, 'cost': m.cost, 'status': m.status, 'notes': m.notes} for m in mods],
        'costs': [{'date': c.date.isoformat() if c.date else None, 'category': c.category, 'amount': c.amount, 'description': c.description} for c in costs],
        'notes': [{'date': n.date.isoformat() if n.date else None, 'title': n.title, 'content': n.content, 'tags': n.tags} for n in notes],
        'vcds_faults': [{'address': f.address, 'fault_code': f.fault_code, 'component': f.component, 'status': f.status, 'detected_date': f.detected_date.isoformat() if f.detected_date else None, 'notes': f.notes} for f in faults],
        'fuel_entries': [{'date': f.date.isoformat() if f.date else None, 'mileage': f.mileage, 'gallons': f.gallons, 'price_per_gallon': f.price_per_gallon, 'total_cost': f.total_cost} for f in fuel_entries],
        'reminders': [{'type': r.type, 'interval_miles': r.interval_miles, 'interval_months': r.interval_months, 'next_due_date': r.next_due_date.isoformat() if r.next_due_date else None, 'next_due_mileage': r.next_due_mileage} for r in reminders]
    })

@routes.route('/vehicles/import', methods=['POST'])
def import_vehicle():
    data = request.json or {}
    error = validate_required(data, [])
    if error:
        return jsonify({'error': error}), 400
    
    vehicle = Vehicle(
        name=data.get('name'), reg=data.get('reg'), vin=data.get('vin'), year=data.get('year'),
        make=data.get('make'), model=data.get('model'),
        engine=data.get('engine'), transmission=data.get('transmission'),
        mileage=data.get('mileage', 0)
    )
    db.session.add(vehicle)
    db.session.commit()
    vehicle_id = vehicle.id
    
    for m in data.get('maintenance', []):
        rec = Maintenance(
            vehicle_id=vehicle_id, date=parse_date(m.get('date')),
            mileage=m.get('mileage'), category=m.get('category'), description=m.get('description'),
            cost=m.get('cost'), notes=m.get('notes')
        )
        db.session.add(rec)
    
    for m in data.get('mods', []):
        mod = Mod(
            vehicle_id=vehicle_id, date=parse_date(m.get('date')),
            mileage=m.get('mileage'), category=m.get('category'), description=m.get('description'),
            cost=m.get('cost'), status=m.get('status', 'completed'), notes=m.get('notes')
        )
        db.session.add(mod)
    
    for c in data.get('costs', []):
        cost = Cost(
            vehicle_id=vehicle_id, date=parse_date(c.get('date')),
            category=c.get('category'), amount=c.get('amount'), description=c.get('description')
        )
        db.session.add(cost)
    
    for n in data.get('notes', []):
        note = Note(
            vehicle_id=vehicle_id, date=parse_date(n.get('date')),
            title=n.get('title'), content=n.get('content'), tags=n.get('tags')
        )
        db.session.add(note)
    
    db.session.commit()
    return jsonify({'id': vehicle_id}), 201

@routes.route('/maintenance', methods=['GET'])
def get_maintenance():
    vehicle_id = request.args.get('vehicle_id')
    query = Maintenance.query
    if vehicle_id:
        query = query.filter_by(vehicle_id=vehicle_id)
    records = query.order_by(Maintenance.date.desc()).all()
    return jsonify([{
        'id': m.id, 'vehicle_id': m.vehicle_id, 'date': m.date.isoformat() if m.date else None,
        'mileage': m.mileage, 'category': m.category, 'description': m.description,
        'parts_used': m.parts_used, 'labor_hours': m.labor_hours, 'cost': m.cost,
        'shop_name': m.shop_name, 'notes': m.notes
    } for m in records])

@routes.route('/maintenance', methods=['POST'])
def add_maintenance():
    data = request.json or {}
    error = validate_required(data, ['vehicle_id', 'date'])
    if error:
        return jsonify({'error': error}), 400
    
    record = Maintenance(
        vehicle_id=data.get('vehicle_id'), date=parse_date(data.get('date')),
        mileage=data.get('mileage'), category=data.get('category'), description=data.get('description'),
        parts_used=json.dumps(data.get('parts_used', [])) if data.get('parts_used') else None,
        labor_hours=data.get('labor_hours'), cost=data.get('cost'), shop_name=data.get('shop_name'),
        notes=data.get('notes')
    )
    db.session.add(record)
    db.session.commit()
    return jsonify({'id': record.id}), 201

@routes.route('/maintenance/<int:id>', methods=['PUT'])
def update_maintenance(id):
    record = db.session.get(Maintenance, id)
    if not record:
        return jsonify({'error': 'Maintenance record not found'}), 404
    
    data = request.json or {}
    for key in ['date', 'mileage', 'category', 'description', 'parts_used', 'labor_hours', 'cost', 'shop_name', 'notes']:
        if key in data:
            if key == 'date':
                setattr(record, key, parse_date(data[key]))
            elif key == 'parts_used':
                setattr(record, key, json.dumps(data[key]) if data[key] else None)
            else:
                setattr(record, key, data[key])
    db.session.commit()
    return jsonify({'success': True})

@routes.route('/maintenance/<int:id>', methods=['DELETE'])
def delete_maintenance(id):
    record = db.session.get(Maintenance, id)
    if not record:
        return jsonify({'error': 'Maintenance record not found'}), 404
    db.session.delete(record)
    db.session.commit()
    return jsonify({'success': True})

@routes.route('/mods', methods=['GET'])
def get_mods():
    vehicle_id = request.args.get('vehicle_id')
    query = Mod.query
    if vehicle_id:
        query = query.filter_by(vehicle_id=vehicle_id)
    mods = query.order_by(Mod.date.desc()).all()
    return jsonify([{
        'id': m.id, 'vehicle_id': m.vehicle_id, 'date': m.date.isoformat() if m.date else None,
        'mileage': m.mileage, 'category': m.category, 'description': m.description,
        'parts': m.parts, 'cost': m.cost, 'status': m.status, 'notes': m.notes
    } for m in mods])

@routes.route('/mods', methods=['POST'])
def add_mod():
    data = request.json or {}
    error = validate_required(data, ['vehicle_id'])
    if error:
        return jsonify({'error': error}), 400
    
    mod = Mod(
        vehicle_id=data.get('vehicle_id'), date=parse_date(data.get('date')),
        mileage=data.get('mileage'), category=data.get('category'), description=data.get('description'),
        parts=json.dumps(data.get('parts', [])) if data.get('parts') else None,
        cost=data.get('cost'), status=data.get('status', 'planned'), notes=data.get('notes')
    )
    db.session.add(mod)
    db.session.commit()
    return jsonify({'id': mod.id}), 201

@routes.route('/mods/<int:id>', methods=['PUT'])
def update_mod(id):
    mod = db.session.get(Mod, id)
    if not mod:
        return jsonify({'error': 'Mod not found'}), 404
    
    data = request.json or {}
    for key in ['date', 'mileage', 'category', 'description', 'parts', 'cost', 'status', 'notes']:
        if key in data:
            if key == 'date':
                setattr(mod, key, parse_date(data[key]))
            elif key == 'parts':
                setattr(mod, key, json.dumps(data[key]) if data[key] else None)
            else:
                setattr(mod, key, data[key])
    db.session.commit()
    return jsonify({'success': True})

@routes.route('/mods/<int:id>', methods=['DELETE'])
def delete_mod(id):
    mod = db.session.get(Mod, id)
    if not mod:
        return jsonify({'error': 'Mod not found'}), 404
    db.session.delete(mod)
    db.session.commit()
    return jsonify({'success': True})

@routes.route('/costs', methods=['GET'])
def get_costs():
    vehicle_id = request.args.get('vehicle_id')
    query = Cost.query
    if vehicle_id:
        query = query.filter_by(vehicle_id=vehicle_id)
    costs = query.order_by(Cost.date.desc()).all()
    return jsonify([{
        'id': c.id, 'vehicle_id': c.vehicle_id, 'date': c.date.isoformat() if c.date else None,
        'category': c.category, 'amount': c.amount, 'description': c.description
    } for c in costs])

@routes.route('/costs', methods=['POST'])
def add_cost():
    data = request.json or {}
    error = validate_required(data, ['vehicle_id'])
    if error:
        return jsonify({'error': error}), 400
    
    cost = Cost(
        vehicle_id=data.get('vehicle_id'), date=parse_date(data.get('date')),
        category=data.get('category'), amount=data.get('amount'), description=data.get('description')
    )
    db.session.add(cost)
    db.session.commit()
    return jsonify({'id': cost.id}), 201

@routes.route('/costs/summary', methods=['GET'])
def cost_summary():
    vehicle_id = request.args.get('vehicle_id')
    query = Cost.query
    if vehicle_id:
        query = query.filter_by(vehicle_id=vehicle_id)
    costs = query.all()
    summary = {}
    for c in costs:
        cat = c.category or 'Uncategorized'
        summary[cat] = summary.get(cat, 0) + (c.amount or 0)
    return jsonify(summary)

@routes.route('/notes', methods=['GET'])
def get_notes():
    vehicle_id = request.args.get('vehicle_id')
    query = Note.query
    if vehicle_id:
        query = query.filter_by(vehicle_id=vehicle_id)
    notes = query.order_by(Note.date.desc()).all()
    return jsonify([{
        'id': n.id, 'vehicle_id': n.vehicle_id, 'date': n.date.isoformat() if n.date else None,
        'title': n.title, 'content': n.content, 'tags': n.tags
    } for n in notes])

@routes.route('/notes', methods=['POST'])
def add_note():
    data = request.json or {}
    error = validate_required(data, ['vehicle_id'])
    if error:
        return jsonify({'error': error}), 400
    
    note = Note(
        vehicle_id=data.get('vehicle_id'), date=parse_date(data.get('date')),
        title=data.get('title'), content=data.get('content'),
        tags=json.dumps(data.get('tags', [])) if data.get('tags') else None
    )
    db.session.add(note)
    db.session.commit()
    return jsonify({'id': note.id}), 201

@routes.route('/notes/<int:id>', methods=['DELETE'])
def delete_note(id):
    note = db.session.get(Note, id)
    if not note:
        return jsonify({'error': 'Note not found'}), 404
    db.session.delete(note)
    db.session.commit()
    return jsonify({'success': True})

@routes.route('/vcds', methods=['GET'])
def get_vcds_faults():
    vehicle_id = request.args.get('vehicle_id')
    query = VCDSFault.query
    if vehicle_id:
        query = query.filter_by(vehicle_id=vehicle_id)
    faults = query.order_by(VCDSFault.detected_date.desc()).all()
    return jsonify([{
        'id': f.id, 'vehicle_id': f.vehicle_id, 'address': f.address, 'component': f.component,
        'fault_code': f.fault_code, 'description': f.description, 'status': f.status,
        'detected_date': f.detected_date.isoformat() if f.detected_date else None,
        'cleared_date': f.cleared_date.isoformat() if f.cleared_date else None, 'notes': f.notes
    } for f in faults])

@routes.route('/vcds', methods=['POST'])
def add_vcds_fault():
    data = request.json or {}
    error = validate_required(data, ['vehicle_id'])
    if error:
        return jsonify({'error': error}), 400
    
    fault = VCDSFault(
        vehicle_id=data.get('vehicle_id'), address=data.get('address'), component=data.get('component'),
        fault_code=data.get('fault_code'), description=data.get('description'), status=data.get('status', 'active'),
        detected_date=parse_date(data.get('detected_date')),
        cleared_date=parse_date(data.get('cleared_date')),
        notes=data.get('notes')
    )
    db.session.add(fault)
    db.session.commit()
    return jsonify({'id': fault.id}), 201

@routes.route('/vcds/<int:id>', methods=['PUT'])
def update_vcds_fault(id):
    fault = db.session.get(VCDSFault, id)
    if not fault:
        return jsonify({'error': 'VCDS fault not found'}), 404
    
    data = request.json or {}
    for key in ['address', 'component', 'fault_code', 'description', 'status', 'notes']:
        if key in data:
            setattr(fault, key, data[key])
    if 'cleared_date' in data:
        fault.cleared_date = parse_date(data['cleared_date'])
    db.session.commit()
    return jsonify({'success': True})

@routes.route('/vcds/import', methods=['POST'])
def import_vcds():
    vehicle_id = request.json.get('vehicle_id')
    faults_data = request.json.get('faults', [])
    if not vehicle_id:
        return jsonify({'error': 'vehicle_id required'}), 400
    
    imported = 0
    for f in faults_data:
        fault = VCDSFault(
            vehicle_id=vehicle_id, address=f.get('address'), component=f.get('component'),
            fault_code=f.get('fault_code'), description=f.get('description'),
            status='active', detected_date=datetime.now(timezone.utc).date()
        )
        db.session.add(fault)
        imported += 1
    db.session.commit()
    return jsonify({'imported': imported})

@routes.route('/vcds/parse', methods=['POST'])
def parse_vcds():
    content = request.json.get('content', '')
    faults = []
    
    lines = content.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line or line.startswith('---') or 'Address' in line or 'Component' in line:
            continue
        
        parts = line.split()
        if len(parts) >= 2:
            address = parts[0] if parts[0][0].isdigit() else None
            fault_code = None
            component = None
            
            for i, p in enumerate(parts):
                if len(p) == 5 and p.isdigit():
                    fault_code = p
                    component = ' '.join(parts[i+1:]) if i+1 < len(parts) else ''
                    break
            
            if address or fault_code:
                faults.append({
                    'address': address or '',
                    'fault_code': fault_code or '',
                    'component': component,
                    'description': ''
                })
    
    return jsonify(faults)

@routes.route('/dashboard', methods=['GET'])
def dashboard():
    vehicle_id = request.args.get('vehicle_id')
    if not vehicle_id:
        return jsonify({'error': 'vehicle_id required'}), 400
    
    total_maintenance = db.session.query(db.func.sum(Maintenance.cost)).filter(Maintenance.vehicle_id == vehicle_id).scalar() or 0
    total_mods = db.session.query(db.func.sum(Mod.cost)).filter(Mod.vehicle_id == vehicle_id).scalar() or 0
    total_costs = db.session.query(db.func.sum(Cost.amount)).filter(Cost.vehicle_id == vehicle_id).scalar() or 0
    
    recent_maintenance = Maintenance.query.filter_by(vehicle_id=vehicle_id).order_by(Maintenance.date.desc()).limit(5).all()
    active_faults = VCDSFault.query.filter_by(vehicle_id=vehicle_id, status='active').count()
    
    return jsonify({
        'total_spent': total_maintenance + total_mods + total_costs,
        'maintenance_cost': total_maintenance,
        'mods_cost': total_mods,
        'other_costs': total_costs,
        'recent_maintenance': [{
            'date': m.date.isoformat() if m.date else None, 'category': m.category, 'description': m.description
        } for m in recent_maintenance],
        'active_faults': active_faults
    })

@routes.route('/analytics', methods=['GET'])
def analytics():
    vehicle_id = request.args.get('vehicle_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not vehicle_id:
        return jsonify({'error': 'vehicle_id required'}), 400
    
    maintenance = Maintenance.query.filter_by(vehicle_id=vehicle_id)
    mods = Mod.query.filter_by(vehicle_id=vehicle_id)
    costs = Cost.query.filter_by(vehicle_id=vehicle_id)
    
    if start_date:
        start = parse_date(start_date)
        if start:
            maintenance = maintenance.filter(Maintenance.date >= start)
            mods = mods.filter(Mod.date >= start)
            costs = costs.filter(Cost.date >= start)
    
    if end_date:
        end = parse_date(end_date)
        if end:
            maintenance = maintenance.filter(Maintenance.date <= end)
            mods = mods.filter(Mod.date <= end)
            costs = costs.filter(Cost.date <= end)
    
    maintenance = maintenance.order_by(Maintenance.date).all()
    mods = mods.order_by(Mod.date).all()
    costs = costs.order_by(Cost.date).all()
    
    monthly_spending = {}
    category_spending = {}
    yearly_spending = {}
    
    for m in maintenance:
        if m.date and m.cost:
            key = m.date.strftime('%Y-%m')
            monthly_spending[key] = monthly_spending.get(key, 0) + m.cost
            year = m.date.strftime('%Y')
            yearly_spending[year] = yearly_spending.get(year, 0) + m.cost
            cat = m.category or 'other'
            category_spending[cat] = category_spending.get(cat, 0) + m.cost
    
    for c in costs:
        if c.date and c.amount:
            key = c.date.strftime('%Y-%m')
            monthly_spending[key] = monthly_spending.get(key, 0) + c.amount
            year = c.date.strftime('%Y')
            yearly_spending[year] = yearly_spending.get(year, 0) + c.amount
            cat = c.category or 'other'
            category_spending[cat] = category_spending.get(cat, 0) + c.amount
    
    for mod in mods:
        if mod.date and mod.cost:
            key = mod.date.strftime('%Y-%m')
            monthly_spending[key] = monthly_spending.get(key, 0) + mod.cost
            year = mod.date.strftime('%Y')
            yearly_spending[year] = yearly_spending.get(year, 0) + mod.cost
    
    total_spent = sum(monthly_spending.values())
    
    last_service = {}
    for cat in SERVICE_INTERVALS:
        rec = Maintenance.query.filter_by(vehicle_id=vehicle_id, category=cat).order_by(Maintenance.date.desc()).first()
        if rec and rec.mileage:
            last_service[cat] = {'date': rec.date.isoformat() if rec.date else None, 'mileage': rec.mileage}
    
    vehicle = db.session.get(Vehicle, vehicle_id)
    current_mileage = vehicle.mileage if vehicle else 0
    
    return jsonify({
        'monthly_spending': monthly_spending,
        'yearly_spending': yearly_spending,
        'category_spending': category_spending,
        'total_spent': total_spent,
        'service_intervals': SERVICE_INTERVALS,
        'last_service': last_service,
        'current_mileage': current_mileage
    })

@routes.route('/guides', methods=['GET'])
def get_guides():
    vehicle_id = request.args.get('vehicle_id')
    category = request.args.get('category')
    
    query = Guide.query
    if vehicle_id:
        query = query.filter((Guide.vehicle_id == vehicle_id) | (Guide.is_template == True))
    if category:
        query = query.filter_by(category=category)
    
    guides = query.order_by(Guide.category, Guide.title).all()
    return jsonify([{
        'id': g.id, 'vehicle_id': g.vehicle_id, 'title': g.title, 'category': g.category,
        'content': g.content, 'interval_miles': g.interval_miles, 'interval_months': g.interval_months,
        'is_template': g.is_template
    } for g in guides])

@routes.route('/guides', methods=['POST'])
def add_guide():
    data = request.json or {}
    error = validate_required(data, ['title'])
    if error:
        return jsonify({'error': error}), 400
    
    guide = Guide(
        vehicle_id=data.get('vehicle_id'), title=data.get('title'), category=data.get('category'),
        content=data.get('content'), interval_miles=data.get('interval_miles'),
        interval_months=data.get('interval_months'), is_template=data.get('is_template', False)
    )
    db.session.add(guide)
    db.session.commit()
    return jsonify({'id': guide.id}), 201

@routes.route('/guides/<int:id>', methods=['PUT'])
def update_guide(id):
    guide = db.session.get(Guide, id)
    if not guide:
        return jsonify({'error': 'Guide not found'}), 404
    
    data = request.json or {}
    for key in ['vehicle_id', 'title', 'category', 'content', 'interval_miles', 'interval_months', 'is_template']:
        if key in data:
            setattr(guide, key, data[key])
    db.session.commit()
    return jsonify({'success': True})

@routes.route('/guides/<int:id>', methods=['DELETE'])
def delete_guide(id):
    guide = db.session.get(Guide, id)
    if not guide:
        return jsonify({'error': 'Guide not found'}), 404
    db.session.delete(guide)
    db.session.commit()
    return jsonify({'success': True})

@routes.route('/guides/templates', methods=['GET'])
def get_guide_templates():
    templates = Guide.query.filter_by(is_template=True).all()
    return jsonify([{
        'id': g.id, 'title': g.title, 'category': g.category, 'content': g.content,
        'interval_miles': g.interval_miles, 'interval_months': g.interval_months
    } for g in templates])

@routes.route('/guides/templates', methods=['POST'])
def create_guide_templates():
    templates = [
        {'title': 'Oil Change', 'category': 'maintenance', 'content': '1. Warm up engine\n2. Drain old oil\n3. Replace filter\n4. Add new oil (5W-30)', 'interval_miles': 5000, 'interval_months': 6, 'is_template': True},
        {'title': 'Tire Rotation', 'category': 'maintenance', 'content': '1. Loosen lug nuts\n2. Lift vehicle\n3. Rotate tires (F-to-F, R-to-R or cross)\n4. Torque to spec', 'interval_miles': 7500, 'interval_months': 6, 'is_template': True},
        {'title': 'Brake Inspection', 'category': 'maintenance', 'content': '1. Remove wheels\n2. Measure pad thickness\n3. Check rotors for wear\n4. Inspect calipers', 'interval_miles': 15000, 'interval_months': 12, 'is_template': True},
        {'title': 'Air Filter Replacement', 'category': 'maintenance', 'content': '1. Locate air box\n2. Release clamps\n3. Replace filter\n4. Reassemble', 'interval_miles': 15000, 'interval_months': 12, 'is_template': True},
        {'title': 'VCDS Scan Guide', 'category': 'howto', 'content': '1. Connect VCDS cable to OBD port\n2. Open VCDS software\n3. Select Auto-Scan\n4. Note fault codes\n5. Clear if needed', 'interval_miles': None, 'interval_months': None, 'is_template': True},
        {'title': 'Spark Plug Replacement', 'category': 'maintenance', 'content': '1. Remove engine cover\n2. Disconnect ignition coils\n3. Remove old plugs\n4. Gap new plugs\n5. Install and reassemble', 'interval_miles': 30000, 'interval_months': 36, 'is_template': True},
    ]
    created = 0
    for t in templates:
        existing = Guide.query.filter_by(title=t['title'], is_template=True).first()
        if not existing:
            guide = Guide(**t)
            db.session.add(guide)
            created += 1
    db.session.commit()
    return jsonify({'created': created})

@routes.route('/vehicle-photos', methods=['GET'])
def get_vehicle_photos():
    vehicle_id = request.args.get('vehicle_id')
    photos = VehiclePhoto.query.filter_by(vehicle_id=vehicle_id).all() if vehicle_id else []
    return jsonify([{
        'id': p.id, 'vehicle_id': p.vehicle_id, 'filename': p.filename,
        'caption': p.caption, 'is_primary': p.is_primary
    } for p in photos])

@routes.route('/vehicle-photos', methods=['POST'])
def add_vehicle_photo():
    data = request.json or {}
    error = validate_required(data, ['vehicle_id', 'filename'])
    if error:
        return jsonify({'error': error}), 400
    
    photo = VehiclePhoto(
        vehicle_id=data.get('vehicle_id'), filename=data.get('filename'),
        caption=data.get('caption'), is_primary=data.get('is_primary', False)
    )
    if photo.is_primary:
        VehiclePhoto.query.filter_by(vehicle_id=photo.vehicle_id, is_primary=True).update({'is_primary': False})
    db.session.add(photo)
    db.session.commit()
    return jsonify({'id': photo.id}), 201

@routes.route('/fuel', methods=['GET'])
def get_fuel_entries():
    vehicle_id = request.args.get('vehicle_id')
    query = FuelEntry.query
    if vehicle_id:
        query = query.filter_by(vehicle_id=vehicle_id)
    entries = query.order_by(FuelEntry.date.desc()).all()
    return jsonify([{
        'id': f.id, 'vehicle_id': f.vehicle_id, 'date': f.date.isoformat() if f.date else None,
        'mileage': f.mileage, 'gallons': f.gallons, 'price_per_gallon': f.price_per_gallon,
        'total_cost': f.total_cost, 'station': f.station, 'notes': f.notes
    } for f in entries])

@routes.route('/fuel', methods=['POST'])
def add_fuel_entry():
    data = request.json or {}
    error = validate_required(data, ['vehicle_id'])
    if error:
        return jsonify({'error': error}), 400
    
    entry = FuelEntry(
        vehicle_id=data.get('vehicle_id'), date=parse_date(data.get('date')),
        mileage=data.get('mileage'), gallons=data.get('gallons'),
        price_per_gallon=data.get('price_per_gallon'), total_cost=data.get('total_cost'),
        station=data.get('station'), notes=data.get('notes')
    )
    db.session.add(entry)
    db.session.commit()
    return jsonify({'id': entry.id}), 201

@routes.route('/fuel/<int:id>', methods=['PUT'])
def update_fuel_entry(id):
    entry = db.session.get(FuelEntry, id)
    if not entry:
        return jsonify({'error': 'Fuel entry not found'}), 404
    
    data = request.json or {}
    for key in ['date', 'mileage', 'gallons', 'price_per_gallon', 'total_cost', 'station', 'notes']:
        if key in data:
            if key == 'date':
                setattr(entry, key, parse_date(data[key]))
            else:
                setattr(entry, key, data[key])
    db.session.commit()
    return jsonify({'success': True})

@routes.route('/fuel/<int:id>', methods=['DELETE'])
def delete_fuel_entry(id):
    entry = db.session.get(FuelEntry, id)
    if not entry:
        return jsonify({'error': 'Fuel entry not found'}), 404
    db.session.delete(entry)
    db.session.commit()
    return jsonify({'success': True})

@routes.route('/reminders', methods=['GET'])
def get_reminders():
    vehicle_id = request.args.get('vehicle_id')
    query = Reminder.query
    if vehicle_id:
        query = query.filter_by(vehicle_id=vehicle_id)
    reminders = query.all()
    return jsonify([{
        'id': r.id, 'vehicle_id': r.vehicle_id, 'type': r.type,
        'interval_miles': r.interval_miles, 'interval_months': r.interval_months,
        'last_service_date': r.last_service_date.isoformat() if r.last_service_date else None,
        'last_service_mileage': r.last_service_mileage,
        'next_due_date': r.next_due_date.isoformat() if r.next_due_date else None,
        'next_due_mileage': r.next_due_mileage, 'notes': r.notes
    } for r in reminders])

@routes.route('/reminders', methods=['POST'])
def add_reminder():
    data = request.json or {}
    error = validate_required(data, ['vehicle_id', 'type'])
    if error:
        return jsonify({'error': error}), 400
    
    reminder = Reminder(
        vehicle_id=data.get('vehicle_id'), type=data.get('type'),
        interval_miles=data.get('interval_miles'), interval_months=data.get('interval_months'),
        last_service_date=parse_date(data.get('last_service_date')),
        last_service_mileage=data.get('last_service_mileage'),
        next_due_date=parse_date(data.get('next_due_date')),
        next_due_mileage=data.get('next_due_mileage'), notes=data.get('notes')
    )
    db.session.add(reminder)
    db.session.commit()
    return jsonify({'id': reminder.id}), 201

@routes.route('/reminders/<int:id>', methods=['PUT'])
def update_reminder(id):
    reminder = db.session.get(Reminder, id)
    if not reminder:
        return jsonify({'error': 'Reminder not found'}), 404
    
    data = request.json or {}
    for key in ['type', 'interval_miles', 'interval_months', 'last_service_date', 'last_service_mileage', 'next_due_date', 'next_due_mileage', 'notes']:
        if key in data:
            if 'date' in key:
                setattr(reminder, key, parse_date(data[key]))
            else:
                setattr(reminder, key, data[key])
    db.session.commit()
    return jsonify({'success': True})

@routes.route('/reminders/<int:id>', methods=['DELETE'])
def delete_reminder(id):
    reminder = db.session.get(Reminder, id)
    if not reminder:
        return jsonify({'error': 'Reminder not found'}), 404
    db.session.delete(reminder)
    db.session.commit()
    return jsonify({'success': True})

@routes.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if not file.filename or file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    original_filename = file.filename
    if not validate_filename(original_filename):
        return jsonify({'error': 'Invalid filename'}), 400
    
    filename = secure_filename_with_ext(original_filename)
    
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    return jsonify({'filename': filename, 'url': f'/uploads/{filename}'}), 201

@routes.route('/uploads/<filename>', methods=['GET'])
def serve_upload(filename):
    if not validate_filename(filename):
        return jsonify({'error': 'Invalid filename'}), 400
    return send_from_directory(UPLOAD_FOLDER, filename)

@routes.route('/upload/<filename>', methods=['DELETE'])
def delete_upload(filename):
    if not validate_filename(filename):
        return jsonify({'error': 'Invalid filename'}), 400
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return jsonify({'success': True})
    return jsonify({'error': 'File not found'}), 404
