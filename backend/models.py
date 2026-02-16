from datetime import datetime, timezone
import json
from backend.extensions import db

def utc_now():
    return datetime.now(timezone.utc)

class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    reg = db.Column(db.String(20), unique=True)
    vin = db.Column(db.String(17), unique=True)
    year = db.Column(db.Integer)
    make = db.Column(db.String(50))
    model = db.Column(db.String(50))
    engine = db.Column(db.String(100))
    transmission = db.Column(db.String(50))
    mileage = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=utc_now)
    
    maintenance = db.relationship('Maintenance', backref='vehicle', lazy=True, cascade='all, delete-orphan')
    mods = db.relationship('Mod', backref='vehicle', lazy=True, cascade='all, delete-orphan')
    costs = db.relationship('Cost', backref='vehicle', lazy=True, cascade='all, delete-orphan')
    notes = db.relationship('Note', backref='vehicle', lazy=True, cascade='all, delete-orphan')
    vcds_faults = db.relationship('VCDSFault', backref='vehicle', lazy=True, cascade='all, delete-orphan')
    guides = db.relationship('Guide', backref='vehicle', lazy=True, cascade='all, delete-orphan')
    photos = db.relationship('VehiclePhoto', backref='vehicle', lazy=True, cascade='all, delete-orphan')
    fuel_entries = db.relationship('FuelEntry', backref='vehicle', lazy=True, cascade='all, delete-orphan')
    reminders = db.relationship('Reminder', backref='vehicle', lazy=True, cascade='all, delete-orphan')

class Maintenance(db.Model):
    __tablename__ = 'maintenance'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    mileage = db.Column(db.Integer)
    category = db.Column(db.String(50))
    description = db.Column(db.Text)
    parts_used = db.Column(db.Text)
    labor_hours = db.Column(db.Float)
    cost = db.Column(db.Float)
    shop_name = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utc_now)

class Mod(db.Model):
    __tablename__ = 'mods'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date)
    mileage = db.Column(db.Integer)
    category = db.Column(db.String(50))
    description = db.Column(db.Text)
    parts = db.Column(db.Text)
    cost = db.Column(db.Float)
    status = db.Column(db.String(20), default='planned')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utc_now)

class Cost(db.Model):
    __tablename__ = 'costs'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date)
    category = db.Column(db.String(50))
    amount = db.Column(db.Float)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utc_now)

class Note(db.Model):
    __tablename__ = 'notes'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    tags = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utc_now)

class VCDSFault(db.Model):
    __tablename__ = 'vcds_faults'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id', ondelete='CASCADE'), nullable=False)
    address = db.Column(db.String(50))
    component = db.Column(db.String(200))
    fault_code = db.Column(db.String(20))
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')
    detected_date = db.Column(db.Date)
    cleared_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utc_now)

class Guide(db.Model):
    __tablename__ = 'guides'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id', ondelete='CASCADE'), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50))
    content = db.Column(db.Text)
    interval_miles = db.Column(db.Integer)
    interval_months = db.Column(db.Integer)
    is_template = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=utc_now)

class VehiclePhoto(db.Model):
    __tablename__ = 'vehicle_photos'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id', ondelete='CASCADE'), nullable=False)
    filename = db.Column(db.String(200))
    caption = db.Column(db.String(500))
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=utc_now)

class FuelEntry(db.Model):
    __tablename__ = 'fuel_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date)
    mileage = db.Column(db.Integer)
    gallons = db.Column(db.Float)
    price_per_gallon = db.Column(db.Float)
    total_cost = db.Column(db.Float)
    station = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utc_now)

class Reminder(db.Model):
    __tablename__ = 'reminders'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id', ondelete='CASCADE'), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    interval_miles = db.Column(db.Integer)
    interval_months = db.Column(db.Integer)
    last_service_date = db.Column(db.Date)
    last_service_mileage = db.Column(db.Integer)
    next_due_date = db.Column(db.Date)
    next_due_mileage = db.Column(db.Integer)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utc_now)

class Setting(db.Model):
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    value_type = db.Column(db.String(20), default='string')
    description = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
