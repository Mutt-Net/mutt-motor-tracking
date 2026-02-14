import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, jsonify, Blueprint
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

app = Flask(__name__)
basedir = os.path.join(os.path.dirname(os.path.dirname(__file__)))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "database", "logbook.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    vin = db.Column(db.String(17), unique=True)
    year = db.Column(db.Integer)
    engine = db.Column(db.String(100))
    transmission = db.Column(db.String(50))
    mileage = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    maintenance = db.relationship('Maintenance', backref='vehicle', lazy=True)
    mods = db.relationship('Mod', backref='vehicle', lazy=True)
    costs = db.relationship('Cost', backref='vehicle', lazy=True)
    notes = db.relationship('Note', backref='vehicle', lazy=True)
    vcds_faults = db.relationship('VCDSFault', backref='vehicle', lazy=True)

class Maintenance(db.Model):
    __tablename__ = 'maintenance'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    mileage = db.Column(db.Integer)
    category = db.Column(db.String(50))
    description = db.Column(db.Text)
    parts_used = db.Column(db.Text)
    labor_hours = db.Column(db.Float)
    cost = db.Column(db.Float)
    shop_name = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Mod(db.Model):
    __tablename__ = 'mods'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    date = db.Column(db.Date)
    mileage = db.Column(db.Integer)
    category = db.Column(db.String(50))
    description = db.Column(db.Text)
    parts = db.Column(db.Text)
    cost = db.Column(db.Float)
    status = db.Column(db.String(20), default='planned')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Cost(db.Model):
    __tablename__ = 'costs'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    date = db.Column(db.Date)
    category = db.Column(db.String(50))
    amount = db.Column(db.Float)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Note(db.Model):
    __tablename__ = 'notes'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    date = db.Column(db.Date)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    tags = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class VCDSFault(db.Model):
    __tablename__ = 'vcds_faults'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    address = db.Column(db.String(50))
    component = db.Column(db.String(200))
    fault_code = db.Column(db.String(20))
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')
    detected_date = db.Column(db.Date)
    cleared_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Guide(db.Model):
    __tablename__ = 'guides'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50))
    content = db.Column(db.Text)
    interval_miles = db.Column(db.Integer)
    interval_months = db.Column(db.Integer)
    is_template = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class VehiclePhoto(db.Model):
    __tablename__ = 'vehicle_photos'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    filename = db.Column(db.String(200))
    caption = db.Column(db.String(500))
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

routes = Blueprint('routes', __name__)

@routes.route('/')
def index():
    with open(os.path.join(basedir, 'frontend', 'index.html'), 'r') as f:
        return f.read()

@routes.route('/css/<path:filename>')
def serve_css(filename):
    with open(os.path.join(basedir, 'frontend', 'css', filename), 'r') as f:
        return f.read(), 200, {'Content-Type': 'text/css'}

@routes.route('/js/<path:filename>')
def serve_js(filename):
    with open(os.path.join(basedir, 'frontend', 'js', filename), 'r') as f:
        return f.read(), 200, {'Content-Type': 'application/javascript'}

@routes.route('/api/vehicles', methods=['GET'])
def get_vehicles():
    vehicles = Vehicle.query.all()
    return jsonify([{
        'id': v.id, 'name': v.name, 'vin': v.vin, 'year': v.year,
        'engine': v.engine, 'transmission': v.transmission, 'mileage': v.mileage
    } for v in vehicles])

@routes.route('/api/vehicles', methods=['POST'])
def add_vehicle():
    data = request.json
    vehicle = Vehicle(
        name=data.get('name'), vin=data.get('vin'), year=data.get('year'),
        engine=data.get('engine'), transmission=data.get('transmission'),
        mileage=data.get('mileage', 0)
    )
    db.session.add(vehicle)
    db.session.commit()
    return jsonify({'id': vehicle.id})

@routes.route('/api/vehicles/<int:id>', methods=['GET'])
def get_vehicle(id):
    vehicle = Vehicle.query.get_or_404(id)
    return jsonify({
        'id': vehicle.id, 'name': vehicle.name, 'vin': vehicle.vin, 'year': vehicle.year,
        'engine': vehicle.engine, 'transmission': vehicle.transmission, 'mileage': vehicle.mileage
    })

@routes.route('/api/vehicles/<int:id>', methods=['PUT'])
def update_vehicle(id):
    vehicle = Vehicle.query.get_or_404(id)
    data = request.json
    for key in ['name', 'vin', 'year', 'engine', 'transmission', 'mileage']:
        if key in data:
            setattr(vehicle, key, data[key])
    db.session.commit()
    return jsonify({'success': True})

@routes.route('/api/vehicles/<int:id>', methods=['DELETE'])
def delete_vehicle(id):
    vehicle = Vehicle.query.get_or_404(id)
    Maintenance.query.filter_by(vehicle_id=id).delete()
    Mod.query.filter_by(vehicle_id=id).delete()
    Cost.query.filter_by(vehicle_id=id).delete()
    Note.query.filter_by(vehicle_id=id).delete()
    VCDSFault.query.filter_by(vehicle_id=id).delete()
    db.session.delete(vehicle)
    db.session.commit()
    return jsonify({'success': True})

@routes.route('/api/maintenance', methods=['GET'])
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

@routes.route('/api/maintenance', methods=['POST'])
def add_maintenance():
    data = request.json
    record = Maintenance(
        vehicle_id=data.get('vehicle_id'), 
        date=datetime.strptime(data.get('date'), '%Y-%m-%d').date() if data.get('date') else None,
        mileage=data.get('mileage'), category=data.get('category'), description=data.get('description'),
        parts_used=json.dumps(data.get('parts_used', [])) if data.get('parts_used') else None,
        labor_hours=data.get('labor_hours'), cost=data.get('cost'), shop_name=data.get('shop_name'),
        notes=data.get('notes')
    )
    db.session.add(record)
    db.session.commit()
    return jsonify({'id': record.id})

@routes.route('/api/maintenance/<int:id>', methods=['DELETE'])
def delete_maintenance(id):
    record = Maintenance.query.get_or_404(id)
    db.session.delete(record)
    db.session.commit()
    return jsonify({'success': True})

@routes.route('/api/maintenance/<int:id>', methods=['PUT'])
def update_maintenance(id):
    record = Maintenance.query.get_or_404(id)
    data = request.json
    for key in ['mileage', 'description', 'parts_used', 'labor_hours', 'cost', 'shop_name', 'notes']:
        if key in data:
            if key == 'parts_used' and data[key]:
                setattr(record, key, json.dumps(data[key]))
            elif key in data and data[key] is not None:
                setattr(record, key, data[key])
    db.session.commit()
    return jsonify({'success': True})

@routes.route('/api/mods', methods=['GET'])
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

@routes.route('/api/mods', methods=['POST'])
def add_mod():
    data = request.json
    mod = Mod(
        vehicle_id=data.get('vehicle_id'),
        date=datetime.strptime(data.get('date'), '%Y-%m-%d').date() if data.get('date') else None,
        mileage=data.get('mileage'), category=data.get('category'), description=data.get('description'),
        parts=json.dumps(data.get('parts', [])) if data.get('parts') else None,
        cost=data.get('cost'), status=data.get('status', 'planned'), notes=data.get('notes')
    )
    db.session.add(mod)
    db.session.commit()
    return jsonify({'id': mod.id})

@routes.route('/api/mods/<int:id>', methods=['PUT'])
def update_mod(id):
    mod = Mod.query.get_or_404(id)
    data = request.json
    for key in ['date', 'mileage', 'category', 'description', 'parts', 'cost', 'status', 'notes']:
        if key in data:
            if key == 'date' and data[key]:
                setattr(mod, key, datetime.strptime(data[key], '%Y-%m-%d').date())
            elif key == 'parts':
                setattr(mod, key, json.dumps(data[key]) if data[key] else None)
            else:
                setattr(mod, key, data[key])
    db.session.commit()
    return jsonify({'success': True})

@routes.route('/api/mods/<int:id>', methods=['DELETE'])
def delete_mod(id):
    mod = Mod.query.get_or_404(id)
    db.session.delete(mod)
    db.session.commit()
    return jsonify({'success': True})

@routes.route('/api/costs', methods=['GET'])
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

@routes.route('/api/costs', methods=['POST'])
def add_cost():
    data = request.json
    cost = Cost(
        vehicle_id=data.get('vehicle_id'),
        date=datetime.strptime(data.get('date'), '%Y-%m-%d').date() if data.get('date') else None,
        category=data.get('category'), amount=data.get('amount'), description=data.get('description')
    )
    db.session.add(cost)
    db.session.commit()
    return jsonify({'id': cost.id})

@routes.route('/api/costs/summary', methods=['GET'])
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

@routes.route('/api/notes', methods=['GET'])
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

@routes.route('/api/notes', methods=['POST'])
def add_note():
    data = request.json
    note = Note(
        vehicle_id=data.get('vehicle_id'),
        date=datetime.strptime(data.get('date'), '%Y-%m-%d').date() if data.get('date') else None,
        title=data.get('title'), content=data.get('content'),
        tags=json.dumps(data.get('tags', [])) if data.get('tags') else None
    )
    db.session.add(note)
    db.session.commit()
    return jsonify({'id': note.id})

@routes.route('/api/notes/<int:id>', methods=['DELETE'])
def delete_note(id):
    note = Note.query.get_or_404(id)
    db.session.delete(note)
    db.session.commit()
    return jsonify({'success': True})

@routes.route('/api/vcds', methods=['GET'])
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

@routes.route('/api/vcds', methods=['POST'])
def add_vcds_fault():
    data = request.json
    fault = VCDSFault(
        vehicle_id=data.get('vehicle_id'), address=data.get('address'), component=data.get('component'),
        fault_code=data.get('fault_code'), description=data.get('description'), status=data.get('status', 'active'),
        detected_date=datetime.strptime(data.get('detected_date'), '%Y-%m-%d').date() if data.get('detected_date') else None,
        cleared_date=datetime.strptime(data.get('cleared_date'), '%Y-%m-%d').date() if data.get('cleared_date') else None,
        notes=data.get('notes')
    )
    db.session.add(fault)
    db.session.commit()
    return jsonify({'id': fault.id})

@routes.route('/api/vcds/<int:id>', methods=['PUT'])
def update_vcds_fault(id):
    fault = VCDSFault.query.get_or_404(id)
    data = request.json
    for key in ['address', 'component', 'fault_code', 'description', 'status', 'notes']:
        if key in data:
            setattr(fault, key, data[key])
    if 'cleared_date' in data:
        fault.cleared_date = datetime.strptime(data['cleared_date'], '%Y-%m-%d').date() if data['cleared_date'] else None
    db.session.commit()
    return jsonify({'success': True})

@routes.route('/api/vcds/import', methods=['POST'])
def import_vcds():
    vehicle_id = request.json.get('vehicle_id')
    faults_data = request.json.get('faults', [])
    imported = 0
    for f in faults_data:
        fault = VCDSFault(
            vehicle_id=vehicle_id, address=f.get('address'), component=f.get('component'),
            fault_code=f.get('fault_code'), description=f.get('description'),
            status='active', detected_date=datetime.now().date()
        )
        db.session.add(fault)
        imported += 1
    db.session.commit()
    return jsonify({'imported': imported})

@routes.route('/api/vcds/parse', methods=['POST'])
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

@routes.route('/api/dashboard', methods=['GET'])
def dashboard():
    vehicle_id = request.args.get('vehicle_id')
    
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

@routes.route('/api/analytics', methods=['GET'])
def analytics():
    vehicle_id = request.args.get('vehicle_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not vehicle_id:
        return jsonify({'error': 'vehicle_id required'}), 400
    
    query = Maintenance.query.filter_by(vehicle_id=vehicle_id)
    if start_date:
        query = query.filter(Maintenance.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date:
        query = query.filter(Maintenance.date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    maintenance = query.order_by(Maintenance.date).all()
    
    query = Mod.query.filter_by(vehicle_id=vehicle_id)
    if start_date:
        query = query.filter(Mod.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date:
        query = query.filter(Mod.date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    mods = query.order_by(Mod.date).all()
    
    query = Cost.query.filter_by(vehicle_id=vehicle_id)
    if start_date:
        query = query.filter(Cost.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date:
        query = query.filter(Cost.date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    costs = query.order_by(Cost.date).all()
    
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
    
    service_intervals = {
        'oil_change': {'miles': 5000, 'months': 6},
        'brakes': {'miles': 20000, 'months': 24},
        'tire_rotation': {'miles': 7500, 'months': 6},
        'inspection': {'miles': 15000, 'months': 12}
    }
    
    last_service = {}
    for cat in service_intervals:
        rec = Maintenance.query.filter_by(vehicle_id=vehicle_id, category=cat).order_by(Maintenance.date.desc()).first()
        if rec and rec.mileage:
            last_service[cat] = {'date': rec.date.isoformat() if rec.date else None, 'mileage': rec.mileage}
    
    vehicle = Vehicle.query.get(vehicle_id)
    current_mileage = vehicle.mileage if vehicle else 0
    
    return jsonify({
        'monthly_spending': monthly_spending,
        'yearly_spending': yearly_spending,
        'category_spending': category_spending,
        'total_spent': total_spent,
        'service_intervals': service_intervals,
        'last_service': last_service,
        'current_mileage': current_mileage
    })

@routes.route('/api/guides', methods=['GET'])
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

@routes.route('/api/guides', methods=['POST'])
def add_guide():
    data = request.json
    guide = Guide(
        vehicle_id=data.get('vehicle_id'), title=data.get('title'), category=data.get('category'),
        content=data.get('content'), interval_miles=data.get('interval_miles'),
        interval_months=data.get('interval_months'), is_template=data.get('is_template', False)
    )
    db.session.add(guide)
    db.session.commit()
    return jsonify({'id': guide.id})

@routes.route('/api/guides/<int:id>', methods=['DELETE'])
def delete_guide(id):
    guide = Guide.query.get_or_404(id)
    db.session.delete(guide)
    db.session.commit()
    return jsonify({'success': True})

@routes.route('/api/guides/<int:id>', methods=['PUT'])
def update_guide(id):
    guide = Guide.query.get_or_404(id)
    data = request.json
    for key in ['title', 'content', 'interval_miles', 'interval_months']:
        if key in data and data[key] is not None:
            setattr(guide, key, data[key])
    db.session.commit()
    return jsonify({'success': True})

@routes.route('/api/guides/templates', methods=['GET'])
def get_guide_templates():
    templates = Guide.query.filter_by(is_template=True).all()
    return jsonify([{
        'id': g.id, 'title': g.title, 'category': g.category, 'content': g.content,
        'interval_miles': g.interval_miles, 'interval_months': g.interval_months
    } for g in templates])

@routes.route('/api/guides/templates', methods=['POST'])
def create_guide_templates():
    templates = [
        {'title': 'Oil Change', 'category': 'maintenance', 'content': '1. Warm up engine\n2. Drain old oil\n3. Replace filter\n4. Add new oil (5W-30)', 'interval_miles': 5000, 'interval_months': 6, 'is_template': True},
        {'title': 'Tire Rotation', 'category': 'maintenance', 'content': '1. Loosen lug nuts\n2. Lift vehicle\n3. Rotate tires (F-to-F, R-to-R or cross)\n4. Torque to spec', 'interval_miles': 7500, 'interval_months': 6, 'is_template': True},
        {'title': 'Brake Inspection', 'category': 'maintenance', 'content': '1. Remove wheels\n2. Measure pad thickness\n3. Check rotors for wear\n4. Inspect calipers', 'interval_miles': 15000, 'interval_months': 12, 'is_template': True},
        {'title': 'Air Filter Replacement', 'category': 'maintenance', 'content': '1. Locate air box\n2. Release clamps\n3. Replace filter\n4. Reassemble', 'interval_miles': 15000, 'interval_months': 12, 'is_template': True},
        {'title': 'VCDS Scan Guide', 'category': 'howto', 'content': '1. Connect VCDS cable to OBD port\n2. Open VCDS software\n3. Select Auto-Scan\n4. Note fault codes\n5. Clear if needed', 'interval_miles': None, 'interval_months': None, 'is_template': True},
        {'title': 'Spark Plug Replacement', 'category': 'maintenance', 'content': '1. Remove engine cover\n2. Disconnect ignition coils\n3. Remove old plugs\n4. Gap new plugs\n5. Install and reassemble', 'interval_miles': 30000, 'interval_months': 36, 'is_template': True},
    ]
    for t in templates:
        existing = Guide.query.filter_by(title=t['title'], is_template=True).first()
        if not existing:
            guide = Guide(**t)
            db.session.add(guide)
    db.session.commit()
    return jsonify({'created': len(templates)})

@routes.route('/api/vehicles/<int:id>/export', methods=['GET'])
def export_vehicle(id):
    vehicle = Vehicle.query.get_or_404(id)
    maintenance = Maintenance.query.filter_by(vehicle_id=id).all()
    mods = Mod.query.filter_by(vehicle_id=id).all()
    costs = Cost.query.filter_by(vehicle_id=id).all()
    notes = Note.query.filter_by(vehicle_id=id).all()
    faults = VCDSFault.query.filter_by(vehicle_id=id).all()
    
    data = {
        'vehicle': {
            'name': vehicle.name, 'vin': vehicle.vin, 'year': vehicle.year,
            'engine': vehicle.engine, 'transmission': vehicle.transmission, 'mileage': vehicle.mileage
        },
        'maintenance': [{'date': m.date.isoformat() if m.date else None, 'mileage': m.mileage, 'category': m.category, 'description': m.description, 'cost': m.cost, 'notes': m.notes} for m in maintenance],
        'mods': [{'date': m.date.isoformat() if m.date else None, 'mileage': m.mileage, 'category': m.category, 'description': m.description, 'cost': m.cost, 'status': m.status, 'notes': m.notes} for m in mods],
        'costs': [{'date': c.date.isoformat() if c.date else None, 'category': c.category, 'amount': c.amount, 'description': c.description} for c in costs],
        'notes': [{'date': n.date.isoformat() if n.date else None, 'title': n.title, 'content': n.content, 'tags': n.tags} for n in notes],
        'vcds_faults': [{'address': f.address, 'fault_code': f.fault_code, 'component': f.component, 'status': f.status, 'detected_date': f.detected_date.isoformat() if f.detected_date else None, 'notes': f.notes} for f in faults]
    }
    return jsonify(data)

@routes.route('/api/vehicles/import', methods=['POST'])
def import_vehicle():
    data = request.json
    vehicle = Vehicle(
        name=data.get('name'), vin=data.get('vin'), year=data.get('year'),
        engine=data.get('engine'), transmission=data.get('transmission'),
        mileage=data.get('mileage', 0)
    )
    db.session.add(vehicle)
    db.session.commit()
    
    vehicle_id = vehicle.id
    
    for m in data.get('maintenance', []):
        rec = Maintenance(
            vehicle_id=vehicle_id,
            date=datetime.strptime(m['date'], '%Y-%m-%d').date() if m.get('date') else None,
            mileage=m.get('mileage'), category=m.get('category'), description=m.get('description'),
            cost=m.get('cost'), notes=m.get('notes')
        )
        db.session.add(rec)
    
    for m in data.get('mods', []):
        mod = Mod(
            vehicle_id=vehicle_id,
            date=datetime.strptime(m['date'], '%Y-%m-%d').date() if m.get('date') else None,
            mileage=m.get('mileage'), category=m.get('category'), description=m.get('description'),
            cost=m.get('cost'), status=m.get('status', 'completed'), notes=m.get('notes')
        )
        db.session.add(mod)
    
    for c in data.get('costs', []):
        cost = Cost(
            vehicle_id=vehicle_id,
            date=datetime.strptime(c['date'], '%Y-%m-%d').date() if c.get('date') else None,
            category=c.get('category'), amount=c.get('amount'), description=c.get('description')
        )
        db.session.add(cost)
    
    for n in data.get('notes', []):
        note = Note(
            vehicle_id=vehicle_id,
            date=datetime.strptime(n['date'], '%Y-%m-%d').date() if n.get('date') else None,
            title=n.get('title'), content=n.get('content'), tags=n.get('tags')
        )
        db.session.add(note)
    
    db.session.commit()
    return jsonify({'id': vehicle_id})

app.register_blueprint(routes)

with app.app_context():
    db.create_all()
    
    if not Vehicle.query.first():
        default_vehicle = Vehicle(
            name='VW EOS',
            vin='WVWZZZ1FZ7V033393',
            year=2007,
            engine='2.0 R4/4V TFSI (AXX)',
            transmission='6-speed Manual',
            mileage=116000
        )
        db.session.add(default_vehicle)
        db.session.commit()
        print("Created default vehicle: VW EOS")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
