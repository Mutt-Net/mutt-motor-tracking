"""
Database Seeding for Integration Tests

Provides functions to create realistic test datasets for integration testing.
"""
import uuid
from datetime import date, timedelta
import random


class SeedData:
    """Class for generating realistic test data."""
    
    VEHICLE_MAKES = ['VW', 'Toyota', 'Honda', 'Ford', 'BMW', 'Audi']
    VEHICLE_MODELS = {
        'VW': ['Golf', 'Polo', 'Tiguan', 'EOS', 'Passat'],
        'Toyota': ['Corolla', 'Camry', 'RAV4', 'Yaris'],
        'Honda': ['Civic', 'Accord', 'CR-V', 'HR-V'],
        'Ford': ['Focus', 'Fiesta', 'Kuga', 'Mustang'],
        'BMW': ['3 Series', '5 Series', 'X3', 'X5'],
        'Audi': ['A3', 'A4', 'Q5', 'A6']
    }
    
    MAINTENANCE_CATEGORIES = [
        'oil_change', 'brakes', 'tire_rotation', 'inspection',
        'transmission', 'coolant', 'spark_plugs', 'air_filter', 'fuel_filter'
    ]
    
    MOD_CATEGORIES = ['engine', 'exhaust', 'suspension', 'interior', 'exterior', 'audio']
    MOD_STATUSES = ['planned', 'in_progress', 'completed']
    
    COST_CATEGORIES = ['fuel', 'insurance', 'tax', 'maintenance', 'mods', 'parking', 'other']
    
    FUEL_STATIONS = ['Shell', 'BP', 'Esso', 'Tesco', 'Sainsburys', 'Asda', 'Morrisons']
    
    @staticmethod
    def generate_vin():
        """Generate a random 17-character VIN."""
        return f'WVWZZZ{chr(65 + random.randint(0, 25))}{random.randint(100000000, 999999999)}'
    
    @classmethod
    def create_test_vehicle_with_history(cls, db_session, **kwargs):
        """Create a vehicle with comprehensive service history."""
        from backend.models import Vehicle, Maintenance, Mod, Cost, Note, FuelEntry, Reminder
        
        make = kwargs.get('make', random.choice(cls.VEHICLE_MAKES))
        model = random.choice(cls.VEHICLE_MODELS.get(make, ['Model']))
        
        vehicle = Vehicle(
            name=kwargs.get('name', f'{make} {model}'),
            vin=kwargs.get('vin', cls.generate_vin()),
            year=kwargs.get('year', random.randint(2015, 2023)),
            make=make,
            model=model,
            engine=kwargs.get('engine', '2.0L Turbo'),
            transmission=kwargs.get('transmission', '6-speed Manual'),
            mileage=kwargs.get('mileage', random.randint(10000, 120000))
        )
        db_session.add(vehicle)
        db_session.commit()
        db_session.refresh(vehicle)
        
        vehicle_id = vehicle.id
        
        current_mileage = vehicle.mileage
        current_date = date.today()
        
        num_maintenance = random.randint(5, 15)
        for i in range(num_maintenance):
            days_ago = random.randint(30, 730)
            maintenance_date = current_date - timedelta(days=days_ago)
            mileage_at_service = current_mileage - (days_ago * 30)
            
            maintenance = Maintenance(
                vehicle_id=vehicle_id,
                date=maintenance_date,
                mileage=mileage_at_service,
                category=random.choice(cls.MAINTENANCE_CATEGORIES),
                description=f'Service {i+1}',
                cost=random.uniform(30, 300),
                parts_used='Oil, Filter',
                labor_hours=random.uniform(0.5, 2.0),
                shop_name=random.choice(['Local Garage', 'Main Dealer', 'Specialist', 'DIY'])
            )
            db_session.add(maintenance)
        
        num_mods = random.randint(2, 8)
        for i in range(num_mods):
            days_ago = random.randint(60, 1000)
            mod_date = current_date - timedelta(days=days_ago)
            mileage_at_mod = current_mileage - (days_ago * 30)
            
            mod = Mod(
                vehicle_id=vehicle_id,
                date=mod_date,
                mileage=mileage_at_mod,
                category=random.choice(cls.MOD_CATEGORIES),
                description=f'Modification {i+1}',
                parts=f'Parts for mod {i+1}',
                cost=random.uniform(50, 2000),
                status=random.choice(cls.MOD_STATUSES)
            )
            db_session.add(mod)
        
        num_costs = random.randint(5, 20)
        for i in range(num_costs):
            days_ago = random.randint(1, 365)
            cost_date = current_date - timedelta(days=days_ago)
            
            cost = Cost(
                vehicle_id=vehicle_id,
                date=cost_date,
                category=random.choice(cls.COST_CATEGORIES),
                amount=random.uniform(10, 600),
                description=f'Expense {i+1}'
            )
            db_session.add(cost)
        
        num_fuel = random.randint(3, 10)
        mileage = vehicle.mileage
        for i in range(num_fuel):
            days_ago = (i + 1) * 15
            fuel_date = current_date - timedelta(days=days_ago)
            mileage += random.randint(200, 500)
            
            fuel = FuelEntry(
                vehicle_id=vehicle_id,
                date=fuel_date,
                mileage=mileage,
                gallons=random.uniform(10, 15),
                price_per_gallon=random.uniform(3.20, 3.80),
                total_cost=random.uniform(35, 55),
                station=random.choice(cls.FUEL_STATIONS),
                notes='Regular fill up'
            )
            db_session.add(fuel)
        
        num_notes = random.randint(1, 5)
        for i in range(num_notes):
            days_ago = random.randint(1, 180)
            note_date = current_date - timedelta(days=days_ago)
            
            note = Note(
                vehicle_id=vehicle_id,
                date=note_date,
                title=f'Note {i+1}',
                content=f'Test content for note {i+1}',
                tags=random.choice(['repair', 'modification', 'service', 'issue', 'general'])
            )
            db_session.add(note)
        
        num_reminders = random.randint(2, 5)
        for i in range(num_reminders):
            reminder = Reminder(
                vehicle_id=vehicle_id,
                type=random.choice(cls.MAINTENANCE_CATEGORIES),
                interval_miles=random.randint(3000, 15000),
                interval_months=random.randint(6, 24),
                last_service_date=current_date - timedelta(days=random.randint(30, 180)),
                last_service_mileage=current_mileage - random.randint(1000, 10000),
                notes=f'Reminder {i+1}'
            )
            db_session.add(reminder)
        
        db_session.commit()
        
        return vehicle
    
    @classmethod
    def create_realistic_dataset(cls, db_session, num_vehicles=3):
        """Create multiple vehicles with realistic data."""
        vehicles = []
        for i in range(num_vehicles):
            vehicle = cls.create_test_vehicle_with_history(
                db_session,
                name=f'Family Vehicle {i+1}'
            )
            vehicles.append(vehicle)
        return vehicles


def create_vehicle_for_timeline_testing(db_session, vehicle_id):
    """Create maintenance records specifically for timeline testing."""
    from backend.models import Maintenance
    
    intervals = {
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
    
    base_date = date.today() - timedelta(days=365)
    base_mileage = 50000
    
    for service_type, interval in intervals.items():
        for i in range(3):
            days_ago = (i + 1) * interval['months'] * 30
            mileage_ago = (i + 1) * interval['miles']
            
            maintenance = Maintenance(
                vehicle_id=vehicle_id,
                date=base_date + timedelta(days=days_ago),
                mileage=base_mileage + mileage_ago,
                category=service_type,
                description=f'{service_type} service {i+1}',
                cost=random.uniform(30, 200)
            )
            db_session.add(maintenance)
    
    db_session.commit()
    return vehicle_id


def create_test_mode_data(db_session, vehicle_id, test_key):
    """Create data marked with a test key for filtering."""
    from backend.models import Maintenance, Mod, Cost
    
    for i in range(3):
        maintenance = Maintenance(
            vehicle_id=vehicle_id,
            date=date.today() - timedelta(days=i*30),
            category='oil_change',
            cost=50.0,
            mileage=50000 + (i * 3000)
        )
        maintenance.test_key = test_key
        db_session.add(maintenance)
    
    mod = Mod(
        vehicle_id=vehicle_id,
        date=date.today(),
        category='engine',
        description='Test mod',
        cost=100.0,
        status='completed'
    )
    mod.test_key = test_key
    db_session.add(mod)
    
    cost = Cost(
        vehicle_id=vehicle_id,
        date=date.today(),
        category='fuel',
        amount=50.0
    )
    cost.test_key = test_key
    db_session.add(cost)
    
    db_session.commit()
    return vehicle_id


def create_data_for_analytics_testing(db_session, vehicle_id):
    """Create data specifically designed for analytics endpoint testing."""
    from backend.models import Maintenance, Mod, Cost, FuelEntry
    
    costs = [
        ('2024-01-01', 'insurance', 500.0),
        ('2024-02-01', 'fuel', 45.0),
        ('2024-02-15', 'fuel', 52.0),
        ('2024-03-01', 'maintenance', 150.0),
        ('2024-03-15', 'tax', 200.0),
        ('2024-04-01', 'fuel', 48.0),
        ('2024-05-01', 'insurance', 500.0),
        ('2024-06-01', 'fuel', 55.0),
    ]
    
    for cost_date, category, amount in costs:
        cost = Cost(
            vehicle_id=vehicle_id,
            date=cost_date,
            category=category,
            amount=amount
        )
        db_session.add(cost)
    
    maintenance_records = [
        ('2024-01-15', 'oil_change', 50.0),
        ('2024-02-20', 'brakes', 180.0),
        ('2024-04-10', 'tire_rotation', 40.0),
    ]
    
    for maint_date, category, cost in maintenance_records:
        maintenance = Maintenance(
            vehicle_id=vehicle_id,
            date=maint_date,
            category=category,
            cost=cost,
            mileage=50000
        )
        db_session.add(maintenance)
    
    fuel_entries = [
        ('2024-02-01', 50100, 12.0, 3.50),
        ('2024-02-15', 50500, 11.5, 3.55),
        ('2024-03-01', 50900, 12.2, 3.60),
        ('2024-04-01', 51300, 11.8, 3.65),
    ]
    
    for fuel_date, mileage, gallons, price in fuel_entries:
        fuel = FuelEntry(
            vehicle_id=vehicle_id,
            date=fuel_date,
            mileage=mileage,
            gallons=gallons,
            price_per_gallon=price,
            total_cost=gallons * price
        )
        db_session.add(fuel)
    
    db_session.commit()
    return vehicle_id
