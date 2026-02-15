import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from backend.extensions import db
from backend.models import Vehicle, Maintenance, Mod, Cost, Note, VCDSFault, Guide, VehiclePhoto, FuelEntry, Reminder

@pytest.fixture
def client():
    test_app = Flask(__name__)
    test_app.config['TESTING'] = True
    test_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    test_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(test_app)
    
    with test_app.app_context():
        db.create_all()
        
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
        
        with test_app.test_client() as test_client:
            yield test_client
        
        db.drop_all()

@pytest.fixture
def test_vehicle_id(client):
    with app.app_context():
        vehicle = Vehicle.query.first()
        return vehicle.id

class TestVehicles:
    def test_get_vehicles(self, client):
        response = client.get('/api/vehicles')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]['name'] == 'Test Vehicle'
    
    def test_get_vehicle(self, client, test_vehicle_id):
        response = client.get(f'/api/vehicles/{test_vehicle_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['name'] == 'Test Vehicle'
    
    def test_get_vehicle_not_found(self, client):
        response = client.get('/api/vehicles/99999')
        assert response.status_code == 404
    
    def test_create_vehicle(self, client):
        response = client.post('/api/vehicles', json={
            'name': 'New Vehicle',
            'year': 2022,
            'make': 'Toyota',
            'model': 'Corolla'
        })
        assert response.status_code == 201
        data = response.get_json()
        assert 'id' in data
        
        with app.app_context():
            vehicles = Vehicle.query.all()
            assert len(vehicles) == 2
    
    def test_create_vehicle_missing_name(self, client):
        response = client.post('/api/vehicles', json={'year': 2022})
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_update_vehicle(self, client, test_vehicle_id):
        response = client.put(f'/api/vehicles/{test_vehicle_id}', json={
            'name': 'Updated Vehicle',
            'mileage': 55000
        })
        assert response.status_code == 200
        
        with app.app_context():
            vehicle = db.session.get(Vehicle, test_vehicle_id)
            assert vehicle.name == 'Updated Vehicle'
            assert vehicle.mileage == 55000
    
    def test_delete_vehicle(self, client, test_vehicle_id):
        response = client.delete(f'/api/vehicles/{test_vehicle_id}')
        assert response.status_code == 200
        
        with app.app_context():
            vehicle = db.session.get(Vehicle, test_vehicle_id)
            assert vehicle is None
    
    def test_cascade_delete(self, client, test_vehicle_id):
        with app.app_context():
            maintenance = Maintenance(
                vehicle_id=test_vehicle_id,
                date='2024-01-15',
                category='oil_change',
                cost=50.0
            )
            mod = Mod(
                vehicle_id=test_vehicle_id,
                date='2024-01-01',
                category='engine',
                description='Test mod'
            )
            cost = Cost(
                vehicle_id=test_vehicle_id,
                date='2024-01-01',
                category='maintenance',
                amount=100.0
            )
            db.session.add_all([maintenance, mod, cost])
            db.session.commit()
        
        response = client.delete(f'/api/vehicles/{test_vehicle_id}')
        assert response.status_code == 200
        
        with app.app_context():
            assert Maintenance.query.count() == 0
            assert Mod.query.count() == 0
            assert Cost.query.count() == 0

class TestMaintenance:
    def test_get_maintenance(self, client, test_vehicle_id):
        with app.app_context():
            maintenance = Maintenance(
                vehicle_id=test_vehicle_id,
                date='2024-01-15',
                category='oil_change',
                cost=50.0
            )
            db.session.add(maintenance)
            db.session.commit()
        
        response = client.get(f'/api/maintenance?vehicle_id={test_vehicle_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]['category'] == 'oil_change'
    
    def test_create_maintenance(self, client, test_vehicle_id):
        response = client.post('/api/maintenance', json={
            'vehicle_id': test_vehicle_id,
            'date': '2024-01-15',
            'category': 'oil_change',
            'cost': 50.0
        })
        assert response.status_code == 201
        data = response.get_json()
        assert 'id' in data
    
    def test_create_maintenance_missing_required(self, client):
        response = client.post('/api/maintenance', json={'category': 'oil_change'})
        assert response.status_code == 400
    
    def test_update_maintenance(self, client, test_vehicle_id):
        with app.app_context():
            maintenance = Maintenance(
                vehicle_id=test_vehicle_id,
                date='2024-01-15',
                category='oil_change',
                cost=50.0
            )
            db.session.add(maintenance)
            db.session.commit()
            maintenance_id = maintenance.id
        
        response = client.put(f'/api/maintenance/{maintenance_id}', json={
            'cost': 75.0,
            'notes': 'Updated'
        })
        assert response.status_code == 200
        
        with app.app_context():
            m = db.session.get(Maintenance, maintenance_id)
            assert m.cost == 75.0
            assert m.notes == 'Updated'
    
    def test_delete_maintenance(self, client, test_vehicle_id):
        with app.app_context():
            maintenance = Maintenance(
                vehicle_id=test_vehicle_id,
                date='2024-01-15',
                category='oil_change'
            )
            db.session.add(maintenance)
            db.session.commit()
            maintenance_id = maintenance.id
        
        response = client.delete(f'/api/maintenance/{maintenance_id}')
        assert response.status_code == 200
        
        with app.app_context():
            assert db.session.get(Maintenance, maintenance_id) is None

class TestMods:
    def test_get_mods(self, client, test_vehicle_id):
        with app.app_context():
            mod = Mod(
                vehicle_id=test_vehicle_id,
                date='2024-01-01',
                category='engine',
                description='Test mod',
                status='completed'
            )
            db.session.add(mod)
            db.session.commit()
        
        response = client.get(f'/api/mods?vehicle_id={test_vehicle_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]['status'] == 'completed'
    
    def test_create_mod(self, client, test_vehicle_id):
        response = client.post('/api/mods', json={
            'vehicle_id': test_vehicle_id,
            'date': '2024-01-01',
            'category': 'suspension',
            'description': 'New suspension'
        })
        assert response.status_code == 201
    
    def test_update_mod(self, client, test_vehicle_id):
        with app.app_context():
            mod = Mod(vehicle_id=test_vehicle_id, status='planned')
            db.session.add(mod)
            db.session.commit()
            mod_id = mod.id
        
        response = client.put(f'/api/mods/{mod_id}', json={'status': 'completed'})
        assert response.status_code == 200
        
        with app.app_context():
            m = db.session.get(Mod, mod_id)
            assert m.status == 'completed'
    
    def test_delete_mod(self, client, test_vehicle_id):
        with app.app_context():
            mod = Mod(vehicle_id=test_vehicle_id)
            db.session.add(mod)
            db.session.commit()
            mod_id = mod.id
        
        response = client.delete(f'/api/mods/{mod_id}')
        assert response.status_code == 200

class TestCosts:
    def test_get_costs(self, client, test_vehicle_id):
        with app.app_context():
            cost = Cost(vehicle_id=test_vehicle_id, category='fuel', amount=50.0)
            db.session.add(cost)
            db.session.commit()
        
        response = client.get(f'/api/costs?vehicle_id={test_vehicle_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
    
    def test_create_cost(self, client, test_vehicle_id):
        response = client.post('/api/costs', json={
            'vehicle_id': test_vehicle_id,
            'category': 'insurance',
            'amount': 500.0
        })
        assert response.status_code == 201
    
    def test_cost_summary(self, client, test_vehicle_id):
        with app.app_context():
            db.session.add_all([
                Cost(vehicle_id=test_vehicle_id, category='fuel', amount=50.0),
                Cost(vehicle_id=test_vehicle_id, category='fuel', amount=60.0),
                Cost(vehicle_id=test_vehicle_id, category='insurance', amount=500.0)
            ])
            db.session.commit()
        
        response = client.get(f'/api/costs/summary?vehicle_id={test_vehicle_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['fuel'] == 110.0
        assert data['insurance'] == 500.0

class TestNotes:
    def test_get_notes(self, client, test_vehicle_id):
        with app.app_context():
            note = Note(vehicle_id=test_vehicle_id, title='Test Note', content='Content')
            db.session.add(note)
            db.session.commit()
        
        response = client.get(f'/api/notes?vehicle_id={test_vehicle_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
    
    def test_create_note(self, client, test_vehicle_id):
        response = client.post('/api/notes', json={
            'vehicle_id': test_vehicle_id,
            'title': 'New Note',
            'content': 'Some content'
        })
        assert response.status_code == 201
    
    def test_delete_note(self, client, test_vehicle_id):
        with app.app_context():
            note = Note(vehicle_id=test_vehicle_id)
            db.session.add(note)
            db.session.commit()
            note_id = note.id
        
        response = client.delete(f'/api/notes/{note_id}')
        assert response.status_code == 200

class TestVCDS:
    def test_get_vcds_faults(self, client, test_vehicle_id):
        with app.app_context():
            fault = VCDSFault(
                vehicle_id=test_vehicle_id,
                address='01 Engine',
                fault_code='P0300',
                status='active'
            )
            db.session.add(fault)
            db.session.commit()
        
        response = client.get(f'/api/vcds?vehicle_id={test_vehicle_id}')
        assert response.status_code == 200
    
    def test_create_vcds_fault(self, client, test_vehicle_id):
        response = client.post('/api/vcds', json={
            'vehicle_id': test_vehicle_id,
            'address': '01 Engine',
            'fault_code': 'P0301',
            'component': 'Cylinder 1'
        })
        assert response.status_code == 201
    
    def test_update_vcds_fault(self, client, test_vehicle_id):
        with app.app_context():
            fault = VCDSFault(vehicle_id=test_vehicle_id, status='active')
            db.session.add(fault)
            db.session.commit()
            fault_id = fault.id
        
        response = client.put(f'/api/vcds/{fault_id}', json={'status': 'cleared'})
        assert response.status_code == 200
    
    def test_parse_vcds(self, client):
        response = client.post('/api/vcds/parse', json={
            'content': '01 Engine\n12345 Random Fault\n67890 Another Fault'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2

class TestGuides:
    def test_get_guides(self, client):
        with app.app_context():
            guide = Guide(title='Test Guide', category='maintenance', is_template=True)
            db.session.add(guide)
            db.session.commit()
        
        response = client.get('/api/guides')
        assert response.status_code == 200
    
    def test_create_guide(self, client):
        response = client.post('/api/guides', json={
            'title': 'New Guide',
            'category': 'howto',
            'content': 'Step by step'
        })
        assert response.status_code == 201
    
    def test_update_guide(self, client):
        with app.app_context():
            guide = Guide(title='Original')
            db.session.add(guide)
            db.session.commit()
            guide_id = guide.id
        
        response = client.put(f'/api/guides/{guide_id}', json={'title': 'Updated'})
        assert response.status_code == 200
    
    def test_delete_guide(self, client):
        with app.app_context():
            guide = Guide(title='To Delete')
            db.session.add(guide)
            db.session.commit()
            guide_id = guide.id
        
        response = client.delete(f'/api/guides/{guide_id}')
        assert response.status_code == 200
    
    def test_get_templates(self, client):
        response = client.get('/api/guides/templates')
        assert response.status_code == 200
    
    def test_create_templates(self, client):
        response = client.post('/api/guides/templates')
        assert response.status_code == 200

class TestDashboard:
    def test_dashboard_requires_vehicle_id(self, client):
        response = client.get('/api/dashboard')
        assert response.status_code == 400
    
    def test_dashboard(self, client, test_vehicle_id):
        with app.app_context():
            db.session.add_all([
                Maintenance(vehicle_id=test_vehicle_id, cost=100.0, date='2024-01-01'),
                Mod(vehicle_id=test_vehicle_id, cost=200.0, date='2024-01-01'),
                Cost(vehicle_id=test_vehicle_id, amount=50.0, date='2024-01-01')
            ])
            db.session.commit()
        
        response = client.get(f'/api/dashboard?vehicle_id={test_vehicle_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['maintenance_cost'] == 100.0
        assert data['mods_cost'] == 200.0
        assert data['other_costs'] == 50.0
        assert data['total_spent'] == 350.0

class TestAnalytics:
    def test_analytics_requires_vehicle_id(self, client):
        response = client.get('/api/analytics')
        assert response.status_code == 400
    
    def test_analytics(self, client, test_vehicle_id):
        with app.app_context():
            db.session.add_all([
                Maintenance(vehicle_id=test_vehicle_id, cost=100.0, date='2024-01-15', category='oil_change'),
                Maintenance(vehicle_id=test_vehicle_id, cost=50.0, date='2024-02-15', category='oil_change'),
                Cost(vehicle_id=test_vehicle_id, amount=200.0, date='2024-01-01', category='insurance')
            ])
            db.session.commit()
        
        response = client.get(f'/api/analytics?vehicle_id={test_vehicle_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['total_spent'] == 350.0
        assert 'service_intervals' in data
    
    def test_analytics_with_date_filter(self, client, test_vehicle_id):
        with app.app_context():
            db.session.add_all([
                Maintenance(vehicle_id=test_vehicle_id, cost=100.0, date='2024-01-15'),
                Maintenance(vehicle_id=test_vehicle_id, cost=200.0, date='2024-06-15')
            ])
            db.session.commit()
        
        response = client.get(
            f'/api/analytics?vehicle_id={test_vehicle_id}&start_date=2024-01-01&end_date=2024-03-31'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['total_spent'] == 100.0

class TestFuelEntries:
    def test_get_fuel_entries(self, client, test_vehicle_id):
        with app.app_context():
            entry = FuelEntry(vehicle_id=test_vehicle_id, gallons=10.0, total_cost=35.0)
            db.session.add(entry)
            db.session.commit()
        
        response = client.get(f'/api/fuel?vehicle_id={test_vehicle_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
    
    def test_create_fuel_entry(self, client, test_vehicle_id):
        response = client.post('/api/fuel', json={
            'vehicle_id': test_vehicle_id,
            'date': '2024-01-15',
            'gallons': 12.5,
            'price_per_gallon': 3.50,
            'total_cost': 43.75
        })
        assert response.status_code == 201
    
    def test_update_fuel_entry(self, client, test_vehicle_id):
        with app.app_context():
            entry = FuelEntry(vehicle_id=test_vehicle_id, gallons=10.0)
            db.session.add(entry)
            db.session.commit()
            entry_id = entry.id
        
        response = client.put(f'/api/fuel/{entry_id}', json={'gallons': 12.0})
        assert response.status_code == 200
    
    def test_delete_fuel_entry(self, client, test_vehicle_id):
        with app.app_context():
            entry = FuelEntry(vehicle_id=test_vehicle_id)
            db.session.add(entry)
            db.session.commit()
            entry_id = entry.id
        
        response = client.delete(f'/api/fuel/{entry_id}')
        assert response.status_code == 200

class TestReminders:
    def test_get_reminders(self, client, test_vehicle_id):
        with app.app_context():
            reminder = Reminder(vehicle_id=test_vehicle_id, type='oil_change')
            db.session.add(reminder)
            db.session.commit()
        
        response = client.get(f'/api/reminders?vehicle_id={test_vehicle_id}')
        assert response.status_code == 200
    
    def test_create_reminder(self, client, test_vehicle_id):
        response = client.post('/api/reminders', json={
            'vehicle_id': test_vehicle_id,
            'type': 'oil_change',
            'interval_miles': 5000,
            'interval_months': 6
        })
        assert response.status_code == 201
    
    def test_update_reminder(self, client, test_vehicle_id):
        with app.app_context():
            reminder = Reminder(vehicle_id=test_vehicle_id, type='oil_change')
            db.session.add(reminder)
            db.session.commit()
            reminder_id = reminder.id
        
        response = client.put(f'/api/reminders/{reminder_id}', json={
            'interval_miles': 7500
        })
        assert response.status_code == 200
    
    def test_delete_reminder(self, client, test_vehicle_id):
        with app.app_context():
            reminder = Reminder(vehicle_id=test_vehicle_id)
            db.session.add(reminder)
            db.session.commit()
            reminder_id = reminder.id
        
        response = client.delete(f'/api/reminders/{reminder_id}')
        assert response.status_code == 200

class TestVehiclePhotos:
    def test_get_photos(self, client, test_vehicle_id):
        with app.app_context():
            photo = VehiclePhoto(vehicle_id=test_vehicle_id, filename='test.jpg')
            db.session.add(photo)
            db.session.commit()
        
        response = client.get(f'/api/vehicle-photos?vehicle_id={test_vehicle_id}')
        assert response.status_code == 200
    
    def test_create_photo(self, client, test_vehicle_id):
        response = client.post('/api/vehicle-photos', json={
            'vehicle_id': test_vehicle_id,
            'filename': 'new_photo.jpg',
            'caption': 'Test'
        })
        assert response.status_code == 201
    
    def test_primary_photo_flag(self, client, test_vehicle_id):
        with app.app_context():
            photo1 = VehiclePhoto(vehicle_id=test_vehicle_id, filename='photo1.jpg', is_primary=True)
            db.session.add(photo1)
            db.session.commit()
        
        response = client.post('/api/vehicle-photos', json={
            'vehicle_id': test_vehicle_id,
            'filename': 'photo2.jpg',
            'is_primary': True
        })
        assert response.status_code == 201
        
        with app.app_context():
            photos = VehiclePhoto.query.filter_by(vehicle_id=test_vehicle_id).all()
            primary_count = sum(1 for p in photos if p.is_primary)
            assert primary_count == 1

class TestValidation:
    def test_invalid_vehicle_id_on_create(self, client):
        response = client.post('/api/maintenance', json={
            'vehicle_id': 99999,
            'date': '2024-01-01'
        })
        assert response.status_code == 201
    
    def test_invalid_date_format(self, client, test_vehicle_id):
        response = client.post('/api/maintenance', json={
            'vehicle_id': test_vehicle_id,
            'date': 'invalid-date'
        })
        assert response.status_code == 201
