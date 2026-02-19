"""
Test Data Factories for MuttLogbook

Provides factory functions to generate test data for all models.
Each factory creates valid, minimally-populated model instances.
"""
import uuid
from datetime import datetime, date, timedelta
import random


class VehicleFactory:
    """Factory for creating Vehicle test instances."""
    
    DEFAULT_VIN = 'WVWZZZ1FZ7V033393'
    
    @staticmethod
    def create(db_session=None, **kwargs):
        """Create a Vehicle instance with optional overrides."""
        from backend.models import Vehicle
        
        defaults = {
            'name': 'Test Vehicle',
            'vin': VehicleFactory.DEFAULT_VIN,
            'year': 2020,
            'make': 'VW',
            'model': 'Golf',
            'engine': '2.0 TFSI',
            'transmission': '6-speed Manual',
            'mileage': 50000
        }
        defaults.update(kwargs)
        
        vehicle = Vehicle(**defaults)
        if db_session:
            db_session.add(vehicle)
            db_session.commit()
            db_session.refresh(vehicle)
        return vehicle


class MaintenanceFactory:
    """Factory for creating Maintenance test instances."""
    
    CATEGORIES = [
        'oil_change', 'brakes', 'tire_rotation', 'inspection',
        'transmission', 'coolant', 'spark_plugs', 'air_filter', 'fuel_filter'
    ]
    
    @staticmethod
    def create(db_session=None, vehicle_id=None, **kwargs):
        """Create a Maintenance instance with optional overrides."""
        from backend.models import Maintenance
        
        defaults = {
            'vehicle_id': vehicle_id or 1,
            'date': date.today(),
            'category': random.choice(MaintenanceFactory.CATEGORIES),
            'description': 'Test maintenance',
            'mileage': 50000,
            'cost': 50.0,
            'parts_used': 'Oil filter, 5W-30 oil',
            'labor_hours': 0.5,
            'shop_name': 'Local Garage'
        }
        defaults.update(kwargs)
        
        maintenance = Maintenance(**defaults)
        if db_session:
            db_session.add(maintenance)
            db_session.commit()
            db_session.refresh(maintenance)
        return maintenance


class ModFactory:
    """Factory for creating Mod test instances."""
    
    CATEGORIES = ['engine', 'exhaust', 'suspension', 'interior', 'exterior', 'audio', 'other']
    STATUSES = ['planned', 'in_progress', 'completed']
    
    @staticmethod
    def create(db_session=None, vehicle_id=None, **kwargs):
        """Create a Mod instance with optional overrides."""
        from backend.models import Mod
        
        defaults = {
            'vehicle_id': vehicle_id or 1,
            'date': date.today(),
            'category': random.choice(ModFactory.CATEGORIES),
            'description': 'Test modification',
            'mileage': 50000,
            'parts': 'Test parts',
            'cost': 100.0,
            'status': random.choice(ModFactory.STATUSES)
        }
        defaults.update(kwargs)
        
        mod = Mod(**defaults)
        if db_session:
            db_session.add(mod)
            db_session.commit()
            db_session.refresh(mod)
        return mod


class CostFactory:
    """Factory for creating Cost test instances."""
    
    CATEGORIES = ['fuel', 'insurance', 'tax', 'maintenance', 'mods', 'other']
    
    @staticmethod
    def create(db_session=None, vehicle_id=None, **kwargs):
        """Create a Cost instance with optional overrides."""
        from backend.models import Cost
        
        defaults = {
            'vehicle_id': vehicle_id or 1,
            'date': date.today(),
            'category': random.choice(CostFactory.CATEGORIES),
            'amount': 50.0,
            'description': 'Test expense'
        }
        defaults.update(kwargs)
        
        cost = Cost(**defaults)
        if db_session:
            db_session.add(cost)
            db_session.commit()
            db_session.refresh(cost)
        return cost


class NoteFactory:
    """Factory for creating Note test instances."""
    
    @staticmethod
    def create(db_session=None, vehicle_id=None, **kwargs):
        """Create a Note instance with optional overrides."""
        from backend.models import Note
        
        defaults = {
            'vehicle_id': vehicle_id or 1,
            'date': date.today(),
            'title': 'Test Note',
            'content': 'This is test note content.',
            'tags': 'test,important'
        }
        defaults.update(kwargs)
        
        note = Note(**defaults)
        if db_session:
            db_session.add(note)
            db_session.commit()
            db_session.refresh(note)
        return note


class VCDSFaultFactory:
    """Factory for creating VCDSFault test instances."""
    
    FAULT_CODES = ['P0300', 'P0171', 'P0420', 'P0442', 'P0128', 'P0301']
    ADDRESSES = ['01 Engine', '02 Transmission', '03 Brakes', '17 Instruments', '19 CAN Bus']
    STATUSES = ['active', 'cleared']
    
    @staticmethod
    def create(db_session=None, vehicle_id=None, **kwargs):
        """Create a VCDSFault instance with optional overrides."""
        from backend.models import VCDSFault
        
        defaults = {
            'vehicle_id': vehicle_id or 1,
            'address': random.choice(VCDSFaultFactory.ADDRESSES),
            'fault_code': random.choice(VCDSFaultFactory.FAULT_CODES),
            'description': 'Test fault description',
            'status': random.choice(VCDSFaultFactory.STATUSES),
            'component': 'Test Component',
            'detected_date': date.today()
        }
        defaults.update(kwargs)
        
        fault = VCDSFault(**defaults)
        if db_session:
            db_session.add(fault)
            db_session.commit()
            db_session.refresh(fault)
        return fault


class GuideFactory:
    """Factory for creating Guide test instances."""
    
    CATEGORIES = ['maintenance', 'howto', 'repair', 'modification']
    
    @staticmethod
    def create(db_session=None, vehicle_id=None, **kwargs):
        """Create a Guide instance with optional overrides."""
        from backend.models import Guide
        
        defaults = {
            'vehicle_id': vehicle_id,
            'title': 'Test Guide',
            'category': random.choice(GuideFactory.CATEGORIES),
            'content': 'Step 1: Do something\nStep 2: Do something else',
            'interval_miles': 5000,
            'interval_months': 6,
            'is_template': False
        }
        defaults.update(kwargs)
        
        guide = Guide(**defaults)
        if db_session:
            db_session.add(guide)
            db_session.commit()
            db_session.refresh(guide)
        return guide


class VehiclePhotoFactory:
    """Factory for creating VehiclePhoto test instances."""
    
    @staticmethod
    def create(db_session=None, vehicle_id=None, **kwargs):
        """Create a VehiclePhoto instance with optional overrides."""
        from backend.models import VehiclePhoto
        
        defaults = {
            'vehicle_id': vehicle_id or 1,
            'filename': f'test_{uuid.uuid4().hex[:8]}.jpg',
            'caption': 'Test photo',
            'is_primary': False
        }
        defaults.update(kwargs)
        
        photo = VehiclePhoto(**defaults)
        if db_session:
            db_session.add(photo)
            db_session.commit()
            db_session.refresh(photo)
        return photo


class FuelEntryFactory:
    """Factory for creating FuelEntry test instances."""
    
    @staticmethod
    def create(db_session=None, vehicle_id=None, **kwargs):
        """Create a FuelEntry instance with optional overrides."""
        from backend.models import FuelEntry
        
        defaults = {
            'vehicle_id': vehicle_id or 1,
            'date': date.today(),
            'mileage': 50000,
            'gallons': 12.5,
            'price_per_gallon': 3.50,
            'total_cost': 43.75,
            'station': 'Shell',
            'notes': 'Test fuel entry'
        }
        defaults.update(kwargs)
        
        fuel = FuelEntry(**defaults)
        if db_session:
            db_session.add(fuel)
            db_session.commit()
            db_session.refresh(fuel)
        return fuel


class ReminderFactory:
    """Factory for creating Reminder test instances."""
    
    TYPES = [
        'oil_change', 'brakes', 'tire_rotation', 'inspection',
        'transmission', 'coolant', 'spark_plugs', 'air_filter', 'fuel_filter', 'custom'
    ]
    
    @staticmethod
    def create(db_session=None, vehicle_id=None, **kwargs):
        """Create a Reminder instance with optional overrides."""
        from backend.models import Reminder
        
        defaults = {
            'vehicle_id': vehicle_id or 1,
            'type': random.choice(ReminderFactory.TYPES),
            'interval_miles': 5000,
            'interval_months': 6,
            'last_service_date': date.today() - timedelta(days=90),
            'last_service_mileage': 50000,
            'notes': 'Test reminder'
        }
        defaults.update(kwargs)
        
        reminder = Reminder(**defaults)
        if db_session:
            db_session.add(reminder)
            db_session.commit()
            db_session.refresh(reminder)
        return reminder


class SettingFactory:
    """Factory for creating Setting test instances."""
    
    VALUE_TYPES = ['string', 'number', 'boolean', 'json']
    
    @staticmethod
    def create(db_session=None, **kwargs):
        """Create a Setting instance with optional overrides."""
        from backend.models import Setting
        
        key = kwargs.get('key', f'test_setting_{uuid.uuid4().hex[:6]}')
        value_type = kwargs.get('value_type', 'string')
        
        if value_type == 'boolean':
            value = 'true'
        elif value_type == 'number':
            value = '42.5'
        elif value_type == 'json':
            value = '{"key": "value"}'
        else:
            value = 'test_value'
        
        defaults = {
            'key': key,
            'value': value,
            'value_type': value_type,
            'description': 'Test setting'
        }
        defaults.update(kwargs)
        
        setting = Setting(**defaults)
        if db_session:
            db_session.add(setting)
            db_session.commit()
            db_session.refresh(setting)
        return setting


class ReceiptFactory:
    """Factory for creating Receipt test instances."""
    
    CATEGORIES = ['parts', 'labor', 'fuel', 'other']
    
    @staticmethod
    def create(db_session=None, vehicle_id=None, maintenance_id=None, **kwargs):
        """Create a Receipt instance with optional overrides."""
        from backend.models import Receipt
        
        defaults = {
            'vehicle_id': vehicle_id or 1,
            'maintenance_id': maintenance_id,
            'date': date.today(),
            'vendor': 'Test Vendor',
            'amount': 50.0,
            'category': random.choice(ReceiptFactory.CATEGORIES),
            'notes': 'Test receipt'
        }
        defaults.update(kwargs)
        
        receipt = Receipt(**defaults)
        if db_session:
            db_session.add(receipt)
            db_session.commit()
            db_session.refresh(receipt)
        return receipt


class ServiceDocumentFactory:
    """Factory for creating ServiceDocument test instances."""
    
    TYPES = ['manual', 'invoice', 'receipt', 'warranty', 'other']
    
    @staticmethod
    def create(db_session=None, vehicle_id=None, maintenance_id=None, **kwargs):
        """Create a ServiceDocument instance with optional overrides."""
        from backend.models import ServiceDocument
        
        defaults = {
            'vehicle_id': vehicle_id or 1,
            'maintenance_id': maintenance_id,
            'title': 'Test Document',
            'description': 'Test document description',
            'document_type': random.choice(ServiceDocumentFactory.TYPES),
            'filename': f'test_{uuid.uuid4().hex[:8]}.pdf'
        }
        defaults.update(kwargs)
        
        document = ServiceDocument(**defaults)
        if db_session:
            db_session.add(document)
            db_session.commit()
            db_session.refresh(document)
        return document


def create_vehicle_with_relationships(db_session, **kwargs):
    """Create a vehicle with all related data for comprehensive testing."""
    from backend.models import Vehicle, Maintenance, Mod, Cost, Note, FuelEntry, Reminder
    
    vehicle = VehicleFactory.create(db_session=db_session, **kwargs)
    vehicle_id = vehicle.id
    
    MaintenanceFactory.create(db_session=db_session, vehicle_id=vehicle_id)
    MaintenanceFactory.create(db_session=db_session, vehicle_id=vehicle_id, category='brakes')
    
    ModFactory.create(db_session=db_session, vehicle_id=vehicle_id, status='completed')
    ModFactory.create(db_session=db_session, vehicle_id=vehicle_id, status='planned')
    
    CostFactory.create(db_session=db_session, vehicle_id=vehicle_id, category='fuel')
    CostFactory.create(db_session=db_session, vehicle_id=vehicle_id, category='insurance')
    
    NoteFactory.create(db_session=db_session, vehicle_id=vehicle_id)
    
    FuelEntryFactory.create(db_session=db_session, vehicle_id=vehicle_id)
    
    ReminderFactory.create(db_session=db_session, vehicle_id=vehicle_id)
    
    return vehicle
