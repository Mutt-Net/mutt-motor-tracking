from flask import Blueprint, request, jsonify, send_from_directory, send_file, current_app
from backend.extensions import db
from backend.models import Vehicle, Maintenance, Mod, Cost, Note, VCDSFault, Guide, VehiclePhoto, FuelEntry, Reminder, Setting, Receipt, ServiceDocument
from datetime import datetime, timezone, timedelta
from dateutil.relativedelta import relativedelta
import json
import os
import uuid
import csv
import io
from datetime import datetime

routes = Blueprint('routes', __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads')
UPLOAD_FOLDER = os.path.normpath(UPLOAD_FOLDER)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'pdf'}

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

def get_setting_value(key, default=False):
    setting = Setting.query.filter_by(key=key).first()
    if setting and setting.value:
        return setting.value.lower() == 'true'
    return default

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

def get_service_intervals():
    setting = Setting.query.filter_by(key='service_intervals').first()
    if setting and setting.value:
        try:
            return json.loads(setting.value)
        except (json.JSONDecodeError, TypeError):
            pass
    return SERVICE_INTERVALS


def calculate_service_status(next_due_date, next_due_mileage, current_mileage):
    today = datetime.now(timezone.utc).date()
    
    if next_due_date and (next_due_date < today):
        return 'overdue'
    if next_due_mileage and current_mileage and (next_due_mileage < current_mileage):
        return 'overdue'
    
    if next_due_date and next_due_date <= today + timedelta(days=30):
        return 'upcoming'
    if next_due_mileage and current_mileage and (next_due_mileage <= current_mileage + 1000):
        return 'upcoming'
    
    return 'ok'


def calculate_maintenance_timeline(vehicle_id, current_mileage):
    service_intervals = get_service_intervals()
    timeline = []
    today = datetime.now(timezone.utc).date()
    
    for service_type, intervals in service_intervals.items():
        interval_months = intervals.get('months', 0)
        interval_miles = intervals.get('miles', 0)
        
        rec = Maintenance.query.filter_by(
            vehicle_id=vehicle_id, 
            category=service_type
        ).order_by(Maintenance.date.desc()).first()
        
        last_service_date = rec.date if rec and rec.date else None
        last_service_mileage = rec.mileage if rec and rec.mileage else None
        
        next_due_date = None
        if last_service_date and interval_months:
            next_due_date = last_service_date + relativedelta(months=interval_months)
        
        next_due_mileage = None
        if last_service_mileage and interval_miles:
            next_due_mileage = last_service_mileage + interval_miles
        
        days_until_due = None
        if next_due_date:
            days_until_due = (next_due_date - today).days
        
        miles_until_due = None
        if next_due_mileage and current_mileage:
            miles_until_due = next_due_mileage - current_mileage
        
        status = calculate_service_status(next_due_date, next_due_mileage, current_mileage)
        
        timeline.append({
            'service_type': service_type,
            'last_service_date': last_service_date.isoformat() if last_service_date else None,
            'last_service_mileage': last_service_mileage,
            'next_due_date': next_due_date.isoformat() if next_due_date else None,
            'next_due_mileage': next_due_mileage,
            'status': status,
            'days_until_due': days_until_due,
            'miles_until_due': miles_until_due,
            'interval_months': interval_months,
            'interval_miles': interval_miles
        })
    
    return timeline

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


@routes.route('/maintenance/timeline', methods=['GET'])
def get_maintenance_timeline():
    vehicle_id = request.args.get('vehicle_id')
    if not vehicle_id:
        return jsonify({'error': 'vehicle_id required'}), 400
    
    try:
        vehicle_id = int(vehicle_id)
    except ValueError:
        return jsonify({'error': 'Invalid vehicle_id'}), 400
    
    vehicle = db.session.get(Vehicle, vehicle_id)
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404
    
    current_mileage = vehicle.mileage or 0
    timeline = calculate_maintenance_timeline(vehicle_id, current_mileage)
    
    return jsonify(timeline)


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
    import re
    
    content = request.json.get('content', '')
    faults = []
    
    address_pattern = re.compile(r'^Address\s+(\d+):\s*(.+)$', re.MULTILINE | re.IGNORECASE)
    fault_code_pattern = re.compile(r'^(\d{5})\s*-\s*(.+?)$', re.MULTILINE)
    description_pattern = re.compile(r'^\s*(\d+)\s*-\s*(.+)$', re.MULTILINE)
    no_fault_pattern = re.compile(r'No fault code found', re.IGNORECASE)
    cannot_reach_pattern = re.compile(r'Cannot be reached', re.IGNORECASE)
    
    blocks = re.split(r'(?=^Address\s+\d+:)', content, flags=re.MULTILINE)
    
    has_address_block = False
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        if address_pattern.match(block):
            has_address_block = True
            break
    
    if not has_address_block:
        simple_address_pattern = re.compile(r'^(\d+)\s+(.+)$', re.MULTILINE)
        simple_fault_pattern = re.compile(r'^(\d{5})\s+(.+)$', re.MULTILINE)
        
        lines = content.strip().split('\n')
        address = ''
        module = ''
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            addr_match = simple_address_pattern.match(line)
            if addr_match and not simple_fault_pattern.match(line):
                address = addr_match.group(1)
                module = addr_match.group(2).strip()
                continue
            
            fault_match = simple_fault_pattern.match(line)
            if fault_match and address:
                faults.append({
                    'address': address,
                    'module': module,
                    'fault_code': fault_match.group(1),
                    'description': fault_match.group(2).strip(),
                    'status': 'Fault'
                })
        
        return jsonify(faults)
    
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        
        addr_match = address_pattern.match(block)
        if not addr_match:
            continue
        
        address = addr_match.group(1)
        module_name = re.sub(r'\s+Labels?[:\.].*$', '', addr_match.group(2)).strip()
        
        block_lines = block.split('\n')
        body = '\n'.join(block_lines[1:]).strip()
        
        if cannot_reach_pattern.search(body):
            faults.append({
                'address': address,
                'module': module_name,
                'fault_code': '',
                'description': '',
                'status': 'Unreachable'
            })
        elif no_fault_pattern.search(body):
            faults.append({
                'address': address,
                'module': module_name,
                'fault_code': '',
                'description': '',
                'status': 'OK'
            })
        else:
            fault_matches = fault_code_pattern.findall(body)
            if fault_matches:
                for fault_code, fault_desc in fault_matches:
                    desc_lines = []
                    for line in body.split('\n'):
                        if fault_code in line:
                            continue
                        if fault_desc.lower() in line.lower():
                            parts = line.strip().split(None, 1)
                            if len(parts) > 1:
                                desc_lines.append(parts[1])
                    
                    description = fault_desc
                    if not desc_lines:
                        desc_match = description_pattern.search(body)
                        if desc_match:
                            description = desc_match.group(2).strip()
                    
                    faults.append({
                        'address': address,
                        'module': module_name,
                        'fault_code': fault_code,
                        'description': description,
                        'status': 'Fault'
                    })
            else:
                faults.append({
                    'address': address,
                    'module': module_name,
                    'fault_code': '',
                    'description': '',
                    'status': 'Unknown'
                })
    
    return jsonify(faults)

@routes.route('/dashboard', methods=['GET'])
def dashboard():
    vehicle_id = request.args.get('vehicle_id')
    if not vehicle_id:
        return jsonify({'error': 'vehicle_id required'}), 400
    
    include_maintenance = get_setting_value('total_spend_include_maintenance', True)
    include_mods = get_setting_value('total_spend_include_mods', True)
    include_costs = get_setting_value('total_spend_include_costs', True)
    include_fuel = get_setting_value('total_spend_include_fuel', False)
    
    total_maintenance = 0
    total_mods = 0
    total_costs = 0
    total_fuel = 0
    
    if include_maintenance:
        total_maintenance = db.session.query(db.func.sum(Maintenance.cost)).filter(Maintenance.vehicle_id == vehicle_id).scalar() or 0
    if include_mods:
        total_mods = db.session.query(db.func.sum(Mod.cost)).filter(
            Mod.vehicle_id == vehicle_id,
            Mod.status != 'planned'
        ).scalar() or 0
    if include_costs:
        total_costs = db.session.query(db.func.sum(Cost.amount)).filter(Cost.vehicle_id == vehicle_id).scalar() or 0
    if include_fuel:
        total_fuel = db.session.query(db.func.sum(FuelEntry.cost)).filter(FuelEntry.vehicle_id == vehicle_id).scalar() or 0
    
    recent_maintenance = Maintenance.query.filter_by(vehicle_id=vehicle_id).order_by(Maintenance.date.desc()).limit(5).all()
    active_faults = VCDSFault.query.filter_by(vehicle_id=vehicle_id, status='active').count()
    
    return jsonify({
        'total_spent': total_maintenance + total_mods + total_costs + total_fuel,
        'maintenance_cost': total_maintenance,
        'mods_cost': total_mods,
        'other_costs': total_costs,
        'fuel_cost': total_fuel,
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
    category = request.args.get('category')
    
    if not vehicle_id:
        return jsonify({'error': 'vehicle_id required'}), 400
    
    include_maintenance = get_setting_value('total_spend_include_maintenance', True)
    include_mods = get_setting_value('total_spend_include_mods', True)
    include_costs = get_setting_value('total_spend_include_costs', True)
    include_fuel = get_setting_value('total_spend_include_fuel', False)
    
    maintenance = Maintenance.query.filter_by(vehicle_id=vehicle_id)
    mods = Mod.query.filter_by(vehicle_id=vehicle_id).filter(Mod.status != 'planned')
    costs = Cost.query.filter_by(vehicle_id=vehicle_id)
    fuel_entries = FuelEntry.query.filter_by(vehicle_id=vehicle_id)
    
    if start_date:
        start = parse_date(start_date)
        if start:
            maintenance = maintenance.filter(Maintenance.date >= start)
            mods = mods.filter(Mod.date >= start)
            costs = costs.filter(Cost.date >= start)
            fuel_entries = fuel_entries.filter(FuelEntry.date >= start)
    
    if end_date:
        end = parse_date(end_date)
        if end:
            maintenance = maintenance.filter(Maintenance.date <= end)
            mods = mods.filter(Mod.date <= end)
            costs = costs.filter(Cost.date <= end)
            fuel_entries = fuel_entries.filter(FuelEntry.date <= end)
    
    maintenance = maintenance.order_by(Maintenance.date).all()
    mods = mods.order_by(Mod.date).all()
    costs = costs.order_by(Cost.date).all()
    fuel_entries = fuel_entries.order_by(FuelEntry.date).all()
    
    monthly_spending = {}
    category_spending = {}
    yearly_spending = {}
    
    if include_maintenance:
        for m in maintenance:
            if category and m.category != category:
                continue
            if m.date and m.cost:
                key = m.date.strftime('%Y-%m')
                monthly_spending[key] = monthly_spending.get(key, 0) + m.cost
                year = m.date.strftime('%Y')
                yearly_spending[year] = yearly_spending.get(year, 0) + m.cost
                cat = m.category or 'other'
                category_spending[cat] = category_spending.get(cat, 0) + m.cost
    
    if include_costs:
        for c in costs:
            if category and c.category != category:
                continue
            if c.date and c.amount:
                key = c.date.strftime('%Y-%m')
                monthly_spending[key] = monthly_spending.get(key, 0) + c.amount
                year = c.date.strftime('%Y')
                yearly_spending[year] = yearly_spending.get(year, 0) + c.amount
                cat = c.category or 'other'
                category_spending[cat] = category_spending.get(cat, 0) + c.amount
    
    if include_mods:
        for mod in mods:
            if category and mod.category != category:
                continue
            if mod.date and mod.cost:
                key = mod.date.strftime('%Y-%m')
                monthly_spending[key] = monthly_spending.get(key, 0) + mod.cost
                year = mod.date.strftime('%Y')
                yearly_spending[year] = yearly_spending.get(year, 0) + mod.cost
    
    if include_fuel:
        for f in fuel_entries:
            if category and category != 'fuel':
                continue
            if f.date and f.cost:
                key = f.date.strftime('%Y-%m')
                monthly_spending[key] = monthly_spending.get(key, 0) + f.cost
                year = f.date.strftime('%Y')
                yearly_spending[year] = yearly_spending.get(year, 0) + f.cost
                cat = 'fuel'
                category_spending[cat] = category_spending.get(cat, 0) + f.cost
    
    total_spent = sum(monthly_spending.values())
    
    last_service = {}
    service_intervals = get_service_intervals()
    for cat in service_intervals:
        rec = Maintenance.query.filter_by(vehicle_id=vehicle_id, category=cat).order_by(Maintenance.date.desc()).first()
        if rec and rec.mileage:
            last_service[cat] = {'date': rec.date.isoformat() if rec.date else None, 'mileage': rec.mileage}
    
    vehicle = db.session.get(Vehicle, vehicle_id)
    current_mileage = vehicle.mileage if vehicle else 0
    
    timeline = calculate_maintenance_timeline(vehicle_id, current_mileage)
    
    return jsonify({
        'monthly_spending': monthly_spending,
        'yearly_spending': yearly_spending,
        'category_spending': category_spending,
        'total_spent': total_spent,
        'service_intervals': service_intervals,
        'last_service': last_service,
        'current_mileage': current_mileage,
        'timeline': timeline
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

@routes.route('/receipts', methods=['GET'])
def get_receipts():
    vehicle_id = request.args.get('vehicle_id')
    maintenance_id = request.args.get('maintenance_id')
    query = Receipt.query
    if vehicle_id:
        query = query.filter_by(vehicle_id=vehicle_id)
    if maintenance_id:
        query = query.filter_by(maintenance_id=maintenance_id)
    receipts = query.order_by(Receipt.date.desc()).all()
    return jsonify([{
        'id': r.id, 'vehicle_id': r.vehicle_id, 'maintenance_id': r.maintenance_id,
        'date': r.date.isoformat() if r.date else None, 'vendor': r.vendor,
        'amount': r.amount, 'category': r.category, 'notes': r.notes,
        'filename': r.filename, 'uploaded_at': r.uploaded_at.isoformat() if r.uploaded_at else None
    } for r in receipts])

@routes.route('/receipts', methods=['POST'])
def add_receipt():
    data = request.json or {}
    error = validate_required(data, ['vehicle_id'])
    if error:
        return jsonify({'error': error}), 400
    
    receipt = Receipt(
        vehicle_id=data.get('vehicle_id'), maintenance_id=data.get('maintenance_id'),
        date=parse_date(data.get('date')), vendor=data.get('vendor'),
        amount=data.get('amount'), category=data.get('category'),
        notes=data.get('notes'), filename=data.get('filename')
    )
    db.session.add(receipt)
    db.session.commit()
    return jsonify({'id': receipt.id}), 201

@routes.route('/receipts/<int:id>', methods=['PUT'])
def update_receipt(id):
    receipt = db.session.get(Receipt, id)
    if not receipt:
        return jsonify({'error': 'Receipt not found'}), 404
    
    data = request.json or {}
    for key in ['vehicle_id', 'maintenance_id', 'vendor', 'amount', 'category', 'notes', 'filename']:
        if key in data:
            setattr(receipt, key, data[key])
    if 'date' in data:
        receipt.date = parse_date(data['date'])
    db.session.commit()
    return jsonify({'success': True})

@routes.route('/receipts/<int:id>', methods=['DELETE'])
def delete_receipt(id):
    receipt = db.session.get(Receipt, id)
    if not receipt:
        return jsonify({'error': 'Receipt not found'}), 404
    db.session.delete(receipt)
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

# Service Document Routes
@routes.route('/documents', methods=['GET'])
def get_documents():
    vehicle_id = request.args.get('vehicle_id')
    query = ServiceDocument.query
    if vehicle_id:
        query = query.filter_by(vehicle_id=vehicle_id)
    documents = query.order_by(ServiceDocument.uploaded_at.desc()).all()
    return jsonify([{
        'id': d.id, 'vehicle_id': d.vehicle_id, 'maintenance_id': d.maintenance_id,
        'title': d.title, 'description': d.description, 'document_type': d.document_type,
        'filename': d.filename, 'uploaded_at': d.uploaded_at.isoformat() if d.uploaded_at else None
    } for d in documents])

@routes.route('/documents', methods=['POST'])
def upload_document():
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
    
    vehicle_id = request.form.get('vehicle_id')
    if not vehicle_id:
        return jsonify({'error': 'vehicle_id is required'}), 400
    
    try:
        vehicle_id = int(vehicle_id)
    except ValueError:
        return jsonify({'error': 'Invalid vehicle_id'}), 400
    
    vehicle = db.session.get(Vehicle, vehicle_id)
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404
    
    maintenance_id = request.form.get('maintenance_id')
    if maintenance_id:
        try:
            maintenance_id = int(maintenance_id)
        except ValueError:
            maintenance_id = None
    
    title = request.form.get('title')
    if not title:
        title = original_filename
    
    description = request.form.get('description')
    document_type = request.form.get('document_type')
    
    filename = secure_filename_with_ext(original_filename)
    
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    document = ServiceDocument(
        vehicle_id=vehicle_id,
        maintenance_id=maintenance_id,
        title=title,
        description=description,
        document_type=document_type,
        filename=filename
    )
    db.session.add(document)
    db.session.commit()
    
    return jsonify({
        'id': document.id,
        'filename': filename,
        'url': f'/uploads/{filename}'
    }), 201

@routes.route('/documents/<int:id>', methods=['DELETE'])
def delete_document(id):
    document = db.session.get(ServiceDocument, id)
    if not document:
        return jsonify({'error': 'Document not found'}), 404
    
    if document.filename:
        filepath = os.path.join(UPLOAD_FOLDER, document.filename)
        if os.path.exists(filepath):
            os.remove(filepath)
    
    db.session.delete(document)
    db.session.commit()
    return jsonify({'success': True})

# Settings Routes
@routes.route('/settings', methods=['GET'])
def get_settings():
    try:
        settings = Setting.query.all()
        result = {}
        for s in settings:
            if s.value_type == 'json':
                result[s.key] = json.loads(s.value) if s.value else None
            elif s.value_type == 'number':
                result[s.key] = float(s.value) if s.value else None
            elif s.value_type == 'boolean':
                result[s.key] = s.value.lower() == 'true' if s.value else False
            else:
                result[s.key] = s.value
        return jsonify(result)
    except Exception as e:
        current_app.logger.error(f'Error loading settings: {e}')
        return jsonify({'error': 'Failed to load settings'}), 500

@routes.route('/settings', methods=['PUT'])
def update_setting():
    data = request.json or {}
    key = data.get('key')
    if not key:
        return jsonify({'error': 'Key is required'}), 400
    
    value = data.get('value')
    value_type = data.get('value_type', 'string')
    description = data.get('description')
    
    if value_type == 'json':
        serialized_value = json.dumps(value) if value is not None else None
    else:
        serialized_value = str(value) if value is not None else None
    
    setting = Setting.query.filter_by(key=key).first()
    if setting:
        setting.value = serialized_value
        setting.value_type = value_type
        if description:
            setting.description = description
    else:
        setting = Setting(
            key=key,
            value=serialized_value,
            value_type=value_type,
            description=description
        )
        db.session.add(setting)
    
    db.session.commit()
    
    # Backup settings to JSON file
    backup_settings_to_file()
    
    return jsonify({'success': True, 'key': key})

@routes.route('/settings/<key>', methods=['PUT'])
def update_setting_by_key(key):
    data = request.json or {}
    value = data.get('value')
    value_type = data.get('value_type')
    
    setting = Setting.query.filter_by(key=key).first()
    if not setting:
        setting = Setting(
            key=key,
            value=str(value) if value is not None else None,
            value_type=value_type or 'string',
            description=data.get('description')
        )
        db.session.add(setting)
    else:
        if value is not None:
            if setting.value_type == 'json':
                setting.value = json.dumps(value)
            else:
                setting.value = str(value)
        if value_type:
            setting.value_type = value_type
    
    db.session.commit()
    backup_settings_to_file()
    return jsonify({'success': True})

@routes.route('/settings/<key>', methods=['DELETE'])
def delete_setting(key):
    setting = Setting.query.filter_by(key=key).first()
    if not setting:
        return jsonify({'error': 'Setting not found'}), 404
    db.session.delete(setting)
    db.session.commit()
    backup_settings_to_file()
    return jsonify({'success': True})

@routes.route('/settings/export', methods=['GET'])
def export_all_data():
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['MuttLogbook Export', datetime.now(timezone.utc).isoformat()])
    writer.writerow([])
    
    # Vehicles
    writer.writerow(['=== VEHICLES ==='])
    writer.writerow(['id', 'name', 'reg', 'vin', 'year', 'make', 'model', 'engine', 'transmission', 'mileage'])
    vehicles = Vehicle.query.all()
    for v in vehicles:
        writer.writerow([v.id, v.name, v.reg, v.vin, v.year, v.make, v.model, v.engine, v.transmission, v.mileage])
    writer.writerow([])
    
    # Maintenance
    writer.writerow(['=== MAINTENANCE ==='])
    writer.writerow(['id', 'vehicle_id', 'date', 'mileage', 'category', 'description', 'parts_used', 'labor_hours', 'cost', 'shop_name', 'notes'])
    maintenance = Maintenance.query.all()
    for m in maintenance:
        writer.writerow([m.id, m.vehicle_id, m.date, m.mileage, m.category, m.description, m.parts_used, m.labor_hours, m.cost, m.shop_name, m.notes])
    writer.writerow([])
    
    # Mods
    writer.writerow(['=== MODS ==='])
    writer.writerow(['id', 'vehicle_id', 'date', 'mileage', 'category', 'description', 'parts', 'cost', 'status', 'notes'])
    mods = Mod.query.all()
    for m in mods:
        writer.writerow([m.id, m.vehicle_id, m.date, m.mileage, m.category, m.description, m.parts, m.cost, m.status, m.notes])
    writer.writerow([])
    
    # Costs
    writer.writerow(['=== COSTS ==='])
    writer.writerow(['id', 'vehicle_id', 'date', 'category', 'amount', 'description'])
    costs = Cost.query.all()
    for c in costs:
        writer.writerow([c.id, c.vehicle_id, c.date, c.category, c.amount, c.description])
    writer.writerow([])
    
    # Notes
    writer.writerow(['=== NOTES ==='])
    writer.writerow(['id', 'vehicle_id', 'date', 'title', 'content', 'tags'])
    notes = Note.query.all()
    for n in notes:
        writer.writerow([n.id, n.vehicle_id, n.date, n.title, n.content, n.tags])
    writer.writerow([])
    
    # Guides
    writer.writerow(['=== GUIDES ==='])
    writer.writerow(['id', 'vehicle_id', 'title', 'category', 'content', 'interval_miles', 'interval_months', 'is_template'])
    guides = Guide.query.all()
    for g in guides:
        writer.writerow([g.id, g.vehicle_id, g.title, g.category, g.content, g.interval_miles, g.interval_months, g.is_template])
    writer.writerow([])
    
    # Fuel Entries
    writer.writerow(['=== FUEL ENTRIES ==='])
    writer.writerow(['id', 'vehicle_id', 'date', 'mileage', 'gallons', 'price_per_gallon', 'total_cost', 'station', 'notes'])
    fuel_entries = FuelEntry.query.all()
    for f in fuel_entries:
        writer.writerow([f.id, f.vehicle_id, f.date, f.mileage, f.gallons, f.price_per_gallon, f.total_cost, f.station, f.notes])
    writer.writerow([])
    
    # VCDS Faults
    writer.writerow(['=== VCDS FAULTS ==='])
    writer.writerow(['id', 'vehicle_id', 'address', 'component', 'fault_code', 'description', 'status', 'detected_date', 'cleared_date', 'notes'])
    faults = VCDSFault.query.all()
    for f in faults:
        writer.writerow([f.id, f.vehicle_id, f.address, f.component, f.fault_code, f.description, f.status, f.detected_date, f.cleared_date, f.notes])
    writer.writerow([])
    
    # Reminders
    writer.writerow(['=== REMINDERS ==='])
    writer.writerow(['id', 'vehicle_id', 'type', 'interval_miles', 'interval_months', 'last_service_date', 'last_service_mileage', 'next_due_date', 'next_due_mileage', 'notes'])
    reminders = Reminder.query.all()
    for r in reminders:
        writer.writerow([r.id, r.vehicle_id, r.type, r.interval_miles, r.interval_months, r.last_service_date, r.last_service_mileage, r.next_due_date, r.next_due_mileage, r.notes])
    writer.writerow([])
    
    # Service Documents
    writer.writerow(['=== SERVICE DOCUMENTS ==='])
    writer.writerow(['id', 'vehicle_id', 'maintenance_id', 'title', 'description', 'document_type', 'filename', 'uploaded_at'])
    service_docs = ServiceDocument.query.all()
    for sd in service_docs:
        writer.writerow([sd.id, sd.vehicle_id, sd.maintenance_id, sd.title, sd.description, sd.document_type, sd.filename, sd.uploaded_at])
    writer.writerow([])
    
    # Receipts
    writer.writerow(['=== RECEIPTS ==='])
    writer.writerow(['id', 'vehicle_id', 'maintenance_id', 'date', 'vendor', 'amount', 'category', 'notes', 'filename', 'uploaded_at'])
    receipts = Receipt.query.all()
    for r in receipts:
        writer.writerow([r.id, r.vehicle_id, r.maintenance_id, r.date, r.vendor, r.amount, r.category, r.notes, r.filename, r.uploaded_at])
    writer.writerow([])
    
    # Settings
    writer.writerow(['=== SETTINGS ==='])
    writer.writerow(['key', 'value', 'value_type', 'description'])
    settings = Setting.query.all()
    for s in settings:
        writer.writerow([s.key, s.value, s.value_type, s.description])
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'muttlogbook_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@routes.route('/settings/backup', methods=['GET'])
def backup_settings():
    settings = Setting.query.all()
    result = {}
    for s in settings:
        if s.value_type == 'json':
            result[s.key] = json.loads(s.value) if s.value else None
        elif s.value_type == 'number':
            result[s.key] = float(s.value) if s.value else None
        elif s.value_type == 'boolean':
            result[s.key] = s.value.lower() == 'true' if s.value else False
        else:
            result[s.key] = s.value
    
    backup = {
        'version': '1.0',
        'exported_at': datetime.now(timezone.utc).isoformat(),
        'settings': result
    }
    
    return jsonify(backup)

def backup_settings_to_file():
    try:
        settings = Setting.query.all()
        result = {}
        for s in settings:
            if s.value_type == 'json':
                result[s.key] = json.loads(s.value) if s.value else None
            elif s.value_type == 'number':
                result[s.key] = float(s.value) if s.value else None
            elif s.value_type == 'boolean':
                result[s.key] = s.value.lower() == 'true' if s.value else False
            else:
                result[s.key] = s.value
        
        backup = {
            'version': '1.0',
            'exported_at': datetime.now(timezone.utc).isoformat(),
            'settings': result
        }
        
        backup_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'instance', 'settings.json')
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        
        with open(backup_path, 'w') as f:
            json.dump(backup, f, indent=2)
    except Exception as e:
        print(f"Failed to backup settings: {e}")


@routes.route('/settings/test-mode', methods=['PUT'])
def update_test_mode():
    """Enable or disable test mode and manage test keys."""
    data = request.json or {}
    enabled = data.get('enabled')
    include_data = data.get('include_test_data', False)
    
    if enabled is not None:
        setting = Setting.query.filter_by(key='test_mode_enabled').first()
        if setting:
            setting.value = 'true' if enabled else 'false'
        else:
            setting = Setting(
                key='test_mode_enabled',
                value='true' if enabled else 'false',
                value_type='boolean',
                description='Enable test mode to filter test data'
            )
            db.session.add(setting)
        db.session.commit()
    
    if include_data is not None:
        setting = Setting.query.filter_by(key='include_test_data').first()
        if setting:
            setting.value = 'true' if include_data else 'false'
        else:
            setting = Setting(
                key='include_test_data',
                value='true' if include_data else 'false',
                value_type='boolean',
                description='Include test data in analytics and reports'
            )
            db.session.add(setting)
        db.session.commit()
    
    backup_settings_to_file()
    return jsonify({'success': True})


@routes.route('/settings/test-mode', methods=['GET'])
def get_test_mode():
    """Get current test mode settings."""
    enabled = get_setting_value('test_mode_enabled', False)
    include_data = get_setting_value('include_test_data', False)
    
    test_key_setting = Setting.query.filter_by(key='test_key').first()
    test_key = test_key_setting.value if test_key_setting else None
    
    return jsonify({
        'enabled': enabled,
        'include_test_data': include_data,
        'test_key': test_key
    })


@routes.route('/settings/test-key', methods=['POST'])
def generate_test_key():
    """Generate a new test key for data isolation."""
    import uuid
    new_key = f'test_{uuid.uuid4().hex[:12]}'
    
    setting = Setting.query.filter_by(key='test_key').first()
    if setting:
        setting.value = new_key
    else:
        setting = Setting(
            key='test_key',
            value=new_key,
            value_type='string',
            description='Test data isolation key'
        )
        db.session.add(setting)
    
    db.session.commit()
    backup_settings_to_file()
    return jsonify({'test_key': new_key})


@routes.route('/settings/test-data/count', methods=['GET'])
def get_test_data_count():
    """Get count of records marked as test data."""
    from backend.models import Vehicle, Maintenance, Mod, Cost, Note, VCDSFault, FuelEntry, Reminder, Receipt, ServiceDocument
    
    counts = {
        'vehicles': Vehicle.query.filter(Vehicle.test_key.isnot(None)).count(),
        'maintenance': Maintenance.query.filter(Maintenance.test_key.isnot(None)).count(),
        'mods': Mod.query.filter(Mod.test_key.isnot(None)).count(),
        'costs': Cost.query.filter(Cost.test_key.isnot(None)).count(),
        'notes': Note.query.filter(Note.test_key.isnot(None)).count(),
        'vcds_faults': VCDSFault.query.filter(VCDSFault.test_key.isnot(None)).count(),
        'fuel_entries': FuelEntry.query.filter(FuelEntry.test_key.isnot(None)).count(),
        'reminders': Reminder.query.filter(Reminder.test_key.isnot(None)).count(),
        'receipts': Receipt.query.filter(Receipt.test_key.isnot(None)).count(),
        'documents': ServiceDocument.query.filter(ServiceDocument.test_key.isnot(None)).count()
    }
    counts['total'] = sum(counts.values())
    
    return jsonify(counts)


@routes.route('/settings/test-data', methods=['DELETE'])
def clear_test_data():
    """Delete all records marked as test data."""
    from backend.models import Vehicle, Maintenance, Mod, Cost, Note, VCDSFault, FuelEntry, Reminder, Receipt, ServiceDocument
    
    deleted = {
        'vehicles': Vehicle.query.filter(Vehicle.test_key.isnot(None)).delete(),
        'maintenance': Maintenance.query.filter(Maintenance.test_key.isnot(None)).delete(),
        'mods': Mod.query.filter(Mod.test_key.isnot(None)).delete(),
        'costs': Cost.query.filter(Cost.test_key.isnot(None)).delete(),
        'notes': Note.query.filter(Note.test_key.isnot(None)).delete(),
        'vcds_faults': VCDSFault.query.filter(VCDSFault.test_key.isnot(None)).delete(),
        'fuel_entries': FuelEntry.query.filter(FuelEntry.test_key.isnot(None)).delete(),
        'reminders': Reminder.query.filter(Reminder.test_key.isnot(None)).delete(),
        'receipts': Receipt.query.filter(Receipt.test_key.isnot(None)).delete(),
        'documents': ServiceDocument.query.filter(ServiceDocument.test_key.isnot(None)).delete()
    }
    deleted['total'] = sum(deleted.values())
    
    db.session.commit()
    
    return jsonify({'deleted': deleted})
