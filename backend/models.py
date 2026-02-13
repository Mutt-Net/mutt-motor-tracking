from datetime import datetime
import json

db = None

def init_db(app):
    global db
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy(app)
    return db

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
