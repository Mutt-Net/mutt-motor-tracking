import pytest
import sys
import os
import uuid
from datetime import date, datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from flask import Flask
from backend.extensions import db
from backend.models import (
    Vehicle, Maintenance, Mod, Cost, Note, VCDSFault, Guide,
    VehiclePhoto, FuelEntry, Reminder, Setting, Receipt, ServiceDocument
)


@pytest.fixture(scope='function')
def app():
    """Create and configure a fresh Flask application for each test."""
    test_app = Flask(__name__)
    test_app.config['TESTING'] = True
    test_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    test_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    test_app.config['WTF_CSRF_ENABLED'] = False
    
    db.init_app(test_app)
    
    with test_app.app_context():
        db.create_all()
    
    from backend.routes import routes
    test_app.register_blueprint(routes, url_prefix='/api')
    
    yield test_app
    
    with test_app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create a test client for making HTTP requests."""
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture(scope='function')
def db_session(app):
    """Provide a database session for direct queries."""
    with app.app_context():
        yield db.session


@pytest.fixture(scope='function')
def test_vehicle(app):
    """Create a test vehicle in the database."""
    with app.app_context():
        vehicle = Vehicle(
            name='Test Vehicle',
            vin='WVWZZZ1FZ7V033393',
            year=2020,
            make='VW',
            model='Golf',
            engine='2.0 TFSI',
            transmission='6-speed Manual',
            mileage=50000
        )
        db.session.add(vehicle)
        db.session.commit()
        vehicle_id = vehicle.id
        
    yield vehicle_id


@pytest.fixture(scope='function')
def test_vehicle_id(test_vehicle):
    """Return the test vehicle ID (convenience fixture)."""
    return test_vehicle


@pytest.fixture(scope='function')
def test_vehicle_2(app):
    """Create a second test vehicle for relationship tests."""
    with app.app_context():
        vehicle = Vehicle(
            name='Second Test Vehicle',
            vin='WVWZZZ1JZ8U044504',
            year=2022,
            make='Toyota',
            model='Corolla',
            engine='1.8L',
            transmission='CVT',
            mileage=15000
        )
        db.session.add(vehicle)
        db.session.commit()
        vehicle_id = vehicle.id
        
    yield vehicle_id


@pytest.fixture(scope='function')
def sample_maintenance(app, test_vehicle):
    """Create a sample maintenance record."""
    with app.app_context():
        maintenance = Maintenance(
            vehicle_id=test_vehicle,
            date=date(2024, 1, 15),
            category='oil_change',
            description='Regular oil change',
            cost=50.0,
            mileage=50000
        )
        db.session.add(maintenance)
        db.session.commit()
        maintenance_id = maintenance.id
        
    yield maintenance_id


@pytest.fixture(scope='function')
def sample_mod(app, test_vehicle):
    """Create a sample mod."""
    with app.app_context():
        mod = Mod(
            vehicle_id=test_vehicle,
            date=date(2024, 1, 1),
            category='engine',
            description='Performance tune',
            cost=500.0,
            status='completed',
            mileage=48000
        )
        db.session.add(mod)
        db.session.commit()
        mod_id = mod.id
        
    yield mod_id


@pytest.fixture(scope='function')
def sample_cost(app, test_vehicle):
    """Create a sample cost."""
    with app.app_context():
        cost = Cost(
            vehicle_id=test_vehicle,
            date=date(2024, 1, 10),
            category='insurance',
            amount=500.0,
            description='Annual insurance'
        )
        db.session.add(cost)
        db.session.commit()
        cost_id = cost.id
        
    yield cost_id


@pytest.fixture(scope='function')
def sample_note(app, test_vehicle):
    """Create a sample note."""
    with app.app_context():
        note = Note(
            vehicle_id=test_vehicle,
            date=date(2024, 1, 5),
            title='Test Note',
            content='This is a test note content',
            tags='test,important'
        )
        db.session.add(note)
        db.session.commit()
        note_id = note.id
        
    yield note_id


@pytest.fixture(scope='function')
def sample_reminder(app, test_vehicle):
    """Create a sample reminder."""
    with app.app_context():
        reminder = Reminder(
            vehicle_id=test_vehicle,
            type='oil_change',
            interval_miles=5000,
            interval_months=6,
            last_service_date=date(2024, 1, 15),
            last_service_mileage=50000
        )
        db.session.add(reminder)
        db.session.commit()
        reminder_id = reminder.id
        
    yield reminder_id


@pytest.fixture(scope='function')
def sample_fuel_entry(app, test_vehicle):
    """Create a sample fuel entry."""
    with app.app_context():
        fuel = FuelEntry(
            vehicle_id=test_vehicle,
            date=date(2024, 1, 20),
            mileage=50500,
            gallons=12.5,
            price_per_gallon=3.50,
            total_cost=43.75,
            station='Shell'
        )
        db.session.add(fuel)
        db.session.commit()
        fuel_id = fuel.id
        
    yield fuel_id


@pytest.fixture(scope='function')
def sample_vcds_fault(app, test_vehicle):
    """Create a sample VCDS fault."""
    with app.app_context():
        fault = VCDSFault(
            vehicle_id=test_vehicle,
            address='01 Engine',
            fault_code='P0300',
            description='Random/Multiple Cylinder Misfire Detected',
            status='active'
        )
        db.session.add(fault)
        db.session.commit()
        fault_id = fault.id
        
    yield fault_id


@pytest.fixture(scope='function')
def sample_guide(app):
    """Create a sample guide."""
    with app.app_context():
        guide = Guide(
            title='Oil Change Guide',
            category='maintenance',
            content='Step 1: Warm up engine\nStep 2: Drain oil',
            interval_miles=5000,
            interval_months=6,
            is_template=True
        )
        db.session.add(guide)
        db.session.commit()
        guide_id = guide.id
        
    yield guide_id


@pytest.fixture(scope='function')
def sample_photo(app, test_vehicle):
    """Create a sample vehicle photo."""
    with app.app_context():
        photo = VehiclePhoto(
            vehicle_id=test_vehicle,
            filename='test_photo.jpg',
            caption='Test vehicle photo',
            is_primary=True
        )
        db.session.add(photo)
        db.session.commit()
        photo_id = photo.id
        
    yield photo_id


@pytest.fixture(scope='function')
def sample_setting(app):
    """Create a sample setting with unique key."""
    unique_key = f'test_setting_{uuid.uuid4().hex[:8]}'
    with app.app_context():
        setting = Setting(
            key=unique_key,
            value='test_value',
            value_type='string',
            description='A test setting'
        )
        db.session.add(setting)
        db.session.commit()
        
    yield unique_key


@pytest.fixture(scope='function')
def sample_receipt(app, test_vehicle, sample_maintenance):
    """Create a sample receipt."""
    with app.app_context():
        receipt = Receipt(
            vehicle_id=test_vehicle,
            maintenance_id=sample_maintenance,
            date=date(2024, 1, 15),
            vendor='AutoZone',
            amount=50.0,
            category='parts',
            notes='Oil filter and oil'
        )
        db.session.add(receipt)
        db.session.commit()
        receipt_id = receipt.id
        
    yield receipt_id


@pytest.fixture(scope='function')
def sample_document(app, test_vehicle):
    """Create a sample service document."""
    with app.app_context():
        document = ServiceDocument(
            vehicle_id=test_vehicle,
            title='Service Manual',
            description='Vehicle service manual',
            document_type='manual',
            filename='service_manual.pdf'
        )
        db.session.add(document)
        db.session.commit()
        document_id = document.id
        
    yield document_id


@pytest.fixture(scope='function')
def test_key():
    """Generate a unique test key for test data isolation."""
    return f'test_{uuid.uuid4().hex[:12]}'


@pytest.fixture(scope='function')
def multiple_maintenance_records(app, test_vehicle):
    """Create multiple maintenance records for timeline testing."""
    with app.app_context():
        records = [
            Maintenance(vehicle_id=test_vehicle, date=date(2023, 1, 1), category='oil_change', cost=50.0, mileage=40000),
            Maintenance(vehicle_id=test_vehicle, date=date(2023, 7, 1), category='oil_change', cost=55.0, mileage=45000),
            Maintenance(vehicle_id=test_vehicle, date=date(2024, 1, 1), category='oil_change', cost=60.0, mileage=50000),
            Maintenance(vehicle_id=test_vehicle, date=date(2023, 6, 1), category='brakes', cost=200.0, mileage=42000),
            Maintenance(vehicle_id=test_vehicle, date=date(2024, 1, 15), category='tire_rotation', cost=40.0, mileage=51000),
        ]
        db.session.add_all(records)
        db.session.commit()
        
    yield test_vehicle


@pytest.fixture(scope='function')
def multiple_mods(app, test_vehicle):
    """Create multiple mods in different states."""
    with app.app_context():
        mods = [
            Mod(vehicle_id=test_vehicle, date=date(2023, 1, 1), category='engine', description='ECU Tune', cost=500.0, status='completed'),
            Mod(vehicle_id=test_vehicle, date=date(2023, 6, 1), category='suspension', description='Coilovers', cost=1200.0, status='completed'),
            Mod(vehicle_id=test_vehicle, date=date(2024, 1, 1), category='exhaust', description='Cat-back exhaust', cost=800.0, status='in_progress'),
            Mod(vehicle_id=test_vehicle, date=date(2024, 2, 1), category='interior', description='New steering wheel', cost=300.0, status='planned'),
        ]
        db.session.add_all(mods)
        db.session.commit()
        
    yield test_vehicle


@pytest.fixture(scope='function')
def multiple_costs(app, test_vehicle):
    """Create multiple costs in different categories."""
    with app.app_context():
        costs = [
            Cost(vehicle_id=test_vehicle, date=date(2024, 1, 1), category='fuel', amount=50.0),
            Cost(vehicle_id=test_vehicle, date=date(2024, 1, 15), category='fuel', amount=55.0),
            Cost(vehicle_id=test_vehicle, date=date(2024, 1, 10), category='insurance', amount=500.0),
            Cost(vehicle_id=test_vehicle, date=date(2024, 1, 20), category='tax', amount=200.0),
            Cost(vehicle_id=test_vehicle, date=date(2024, 2, 1), category='maintenance', amount=100.0),
        ]
        db.session.add_all(costs)
        db.session.commit()
        
    yield test_vehicle
