import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.tests.helpers import (
    assert_response_success, assert_response_created, assert_response_not_found,
    assert_response_bad_request, assert_valid_json_response, create_test_vehicle,
    create_test_maintenance, create_test_mod, create_test_cost, create_test_note,
    create_test_reminder, create_test_fuel
)


class TestVehicles:
    """Tests for Vehicle CRUD endpoints."""

    def test_get_vehicles(self, client, test_vehicle):
        """Test getting all vehicles returns the test vehicle."""
        response = client.get('/api/vehicles')
        assert_response_success(response)
        data = response.get_json()
        assert len(data) >= 1

    def test_get_vehicle(self, client, test_vehicle):
        """Test getting a specific vehicle by ID."""
        response = client.get(f'/api/vehicles/{test_vehicle}')
        assert_response_success(response)
        data = response.get_json()
        assert data['name'] == 'Test Vehicle'

    def test_get_vehicle_not_found(self, client):
        """Test getting a non-existent vehicle returns 404."""
        response = client.get('/api/vehicles/99999')
        assert_response_not_found(response)

    def test_create_vehicle(self, client):
        """Test creating a new vehicle."""
        response = client.post('/api/vehicles', json={
            'name': 'New Vehicle',
            'year': 2022,
            'make': 'Toyota',
            'model': 'Corolla'
        })
        assert_response_created(response)
        data = response.get_json()
        assert 'id' in data

    def test_create_vehicle_missing_name(self, client):
        """Test creating a vehicle without required name returns error."""
        import pytest
        with pytest.raises(Exception):
            response = client.post('/api/vehicles', json={'year': 2022})

    def test_update_vehicle(self, client, test_vehicle):
        """Test updating a vehicle."""
        response = client.put(f'/api/vehicles/{test_vehicle}', json={
            'name': 'Updated Vehicle',
            'mileage': 55000
        })
        assert_response_success(response)

        response = client.get(f'/api/vehicles/{test_vehicle}')
        data = response.get_json()
        assert data['name'] == 'Updated Vehicle'
        assert data['mileage'] == 55000

    def test_delete_vehicle(self, client, test_vehicle):
        """Test deleting a vehicle."""
        response = client.delete(f'/api/vehicles/{test_vehicle}')
        assert_response_success(response)

        response = client.get(f'/api/vehicles/{test_vehicle}')
        assert_response_not_found(response)

    def test_cascade_delete(self, client, test_vehicle):
        """Test that deleting a vehicle cascades to related records."""
        from backend.models import Maintenance, Mod, Cost

        client.post('/api/maintenance', json={
            'vehicle_id': test_vehicle,
            'date': '2024-01-15',
            'category': 'oil_change',
            'cost': 50.0
        })

        client.post('/api/mods', json={
            'vehicle_id': test_vehicle,
            'date': '2024-01-01',
            'category': 'engine',
            'description': 'Test mod'
        })

        client.post('/api/costs', json={
            'vehicle_id': test_vehicle,
            'date': '2024-01-01',
            'category': 'maintenance',
            'amount': 100.0
        })

        response = client.delete(f'/api/vehicles/{test_vehicle}')
        assert_response_success(response)

        response = client.get(f'/api/maintenance?vehicle_id={test_vehicle}')
        data = response.get_json()
        assert len(data) == 0


class TestMaintenance:
    """Tests for Maintenance CRUD endpoints."""

    def test_get_maintenance(self, client, test_vehicle, sample_maintenance):
        """Test getting maintenance records for a vehicle."""
        response = client.get(f'/api/maintenance?vehicle_id={test_vehicle}')
        assert_response_success(response)
        data = response.get_json()
        assert len(data) >= 1
        assert data[0]['category'] == 'oil_change'

    def test_create_maintenance(self, client, test_vehicle):
        """Test creating a maintenance record."""
        response = client.post('/api/maintenance', json={
            'vehicle_id': test_vehicle,
            'date': '2024-01-15',
            'category': 'oil_change',
            'cost': 50.0
        })
        assert_response_created(response)
        data = response.get_json()
        assert 'id' in data

    def test_create_maintenance_missing_required(self, client, test_vehicle):
        """Test creating maintenance without required fields returns 400."""
        response = client.post('/api/maintenance', json={'category': 'oil_change'})
        assert_response_bad_request(response)

    def test_update_maintenance(self, client, test_vehicle, sample_maintenance):
        """Test updating a maintenance record."""
        response = client.put(f'/api/maintenance/{sample_maintenance}', json={
            'cost': 75.0,
            'notes': 'Updated'
        })
        assert_response_success(response)

    def test_delete_maintenance(self, client, test_vehicle, sample_maintenance):
        """Test deleting a maintenance record."""
        response = client.delete(f'/api/maintenance/{sample_maintenance}')
        assert_response_success(response)


class TestMods:
    """Tests for Mod CRUD endpoints."""

    def test_get_mods(self, client, test_vehicle, sample_mod):
        """Test getting mods for a vehicle."""
        response = client.get(f'/api/mods?vehicle_id={test_vehicle}')
        assert_response_success(response)
        data = response.get_json()
        assert len(data) >= 1

    def test_create_mod(self, client, test_vehicle):
        """Test creating a mod."""
        response = client.post('/api/mods', json={
            'vehicle_id': test_vehicle,
            'date': '2024-01-01',
            'category': 'suspension',
            'description': 'New suspension'
        })
        assert_response_created(response)

    def test_update_mod(self, client, test_vehicle, sample_mod):
        """Test updating a mod status."""
        response = client.put(f'/api/mods/{sample_mod}', json={'status': 'completed'})
        assert_response_success(response)

    def test_delete_mod(self, client, test_vehicle, sample_mod):
        """Test deleting a mod."""
        response = client.delete(f'/api/mods/{sample_mod}')
        assert_response_success(response)


class TestCosts:
    """Tests for Cost CRUD endpoints."""

    def test_get_costs(self, client, test_vehicle, sample_cost):
        """Test getting costs for a vehicle."""
        response = client.get(f'/api/costs?vehicle_id={test_vehicle}')
        assert_response_success(response)
        data = response.get_json()
        assert len(data) >= 1

    def test_create_cost(self, client, test_vehicle):
        """Test creating a cost."""
        response = client.post('/api/costs', json={
            'vehicle_id': test_vehicle,
            'category': 'insurance',
            'amount': 500.0
        })
        assert_response_created(response)

    def test_cost_summary(self, client, test_vehicle):
        """Test getting cost summary by category."""
        client.post('/api/costs', json={
            'vehicle_id': test_vehicle,
            'category': 'fuel',
            'amount': 50.0
        })
        client.post('/api/costs', json={
            'vehicle_id': test_vehicle,
            'category': 'fuel',
            'amount': 60.0
        })
        client.post('/api/costs', json={
            'vehicle_id': test_vehicle,
            'category': 'insurance',
            'amount': 500.0
        })

        response = client.get(f'/api/costs/summary?vehicle_id={test_vehicle}')
        assert_response_success(response)
        data = response.get_json()
        assert data['fuel'] == 110.0
        assert data['insurance'] == 500.0


class TestNotes:
    """Tests for Note CRUD endpoints."""

    def test_get_notes(self, client, test_vehicle, sample_note):
        """Test getting notes for a vehicle."""
        response = client.get(f'/api/notes?vehicle_id={test_vehicle}')
        assert_response_success(response)
        data = response.get_json()
        assert len(data) >= 1

    def test_create_note(self, client, test_vehicle):
        """Test creating a note."""
        response = client.post('/api/notes', json={
            'vehicle_id': test_vehicle,
            'title': 'New Note',
            'content': 'Some content'
        })
        assert_response_created(response)

    def test_delete_note(self, client, test_vehicle, sample_note):
        """Test deleting a note."""
        response = client.delete(f'/api/notes/{sample_note}')
        assert_response_success(response)


class TestVCDS:
    """Tests for VCDS fault code endpoints."""

    def test_get_vcds_faults(self, client, test_vehicle, sample_vcds_fault):
        """Test getting VCDS faults for a vehicle."""
        response = client.get(f'/api/vcds?vehicle_id={test_vehicle}')
        assert_response_success(response)

    def test_create_vcds_fault(self, client, test_vehicle):
        """Test creating a VCDS fault."""
        response = client.post('/api/vcds', json={
            'vehicle_id': test_vehicle,
            'address': '01 Engine',
            'fault_code': 'P0301',
            'component': 'Cylinder 1'
        })
        assert_response_created(response)

    def test_update_vcds_fault(self, client, test_vehicle, sample_vcds_fault):
        """Test updating a VCDS fault status."""
        response = client.put(f'/api/vcds/{sample_vcds_fault}', json={'status': 'cleared'})
        assert_response_success(response)

    def test_parse_vcds(self, client):
        """Test parsing VCDS output text."""
        response = client.post('/api/vcds/parse', json={
            'content': '01 Engine\n12345 Random Fault\n67890 Another Fault'
        })
        assert_response_success(response)
        data = response.get_json()
        assert len(data) >= 1


class TestGuides:
    """Tests for Guide endpoints."""

    def test_get_guides(self, client, sample_guide):
        """Test getting guides."""
        response = client.get('/api/guides')
        assert_response_success(response)

    def test_create_guide(self, client):
        """Test creating a guide."""
        response = client.post('/api/guides', json={
            'title': 'New Guide',
            'category': 'howto',
            'content': 'Step by step'
        })
        assert_response_created(response)

    def test_update_guide(self, client, sample_guide):
        """Test updating a guide."""
        response = client.put(f'/api/guides/{sample_guide}', json={'title': 'Updated'})
        assert_response_success(response)

    def test_delete_guide(self, client, sample_guide):
        """Test deleting a guide."""
        response = client.delete(f'/api/guides/{sample_guide}')
        assert_response_success(response)

    def test_get_templates(self, client):
        """Test getting guide templates."""
        response = client.get('/api/guides/templates')
        assert_response_success(response)

    def test_create_templates(self, client):
        """Test creating default guide templates."""
        response = client.post('/api/guides/templates')
        assert_response_success(response)


class TestDashboard:
    """Tests for Dashboard endpoint."""

    def test_dashboard_requires_vehicle_id(self, client):
        """Test that dashboard requires vehicle_id parameter."""
        response = client.get('/api/dashboard')
        assert_response_bad_request(response)

    def test_dashboard(self, client, test_vehicle):
        """Test getting dashboard statistics."""
        client.post('/api/maintenance', json={
            'vehicle_id': test_vehicle,
            'cost': 100.0,
            'date': '2024-01-01',
            'category': 'oil_change'
        })
        client.post('/api/mods', json={
            'vehicle_id': test_vehicle,
            'cost': 200.0,
            'date': '2024-01-01',
            'status': 'completed'
        })
        client.post('/api/costs', json={
            'vehicle_id': test_vehicle,
            'amount': 50.0,
            'date': '2024-01-01'
        })

        response = client.get(f'/api/dashboard?vehicle_id={test_vehicle}')
        assert_response_success(response)
        data = response.get_json()
        assert data['maintenance_cost'] == 100.0
        assert data['mods_cost'] == 200.0
        assert data['other_costs'] == 50.0
        assert data['total_spent'] == 350.0


class TestAnalytics:
    """Tests for Analytics endpoint."""

    def test_analytics_requires_vehicle_id(self, client):
        """Test that analytics requires vehicle_id parameter."""
        response = client.get('/api/analytics')
        assert_response_bad_request(response)

    def test_analytics(self, client, test_vehicle):
        """Test getting analytics data."""
        client.post('/api/maintenance', json={
            'vehicle_id': test_vehicle,
            'cost': 100.0,
            'date': '2024-01-15',
            'category': 'oil_change'
        })
        client.post('/api/costs', json={
            'vehicle_id': test_vehicle,
            'amount': 200.0,
            'date': '2024-01-01',
            'category': 'insurance'
        })

        response = client.get(f'/api/analytics?vehicle_id={test_vehicle}')
        assert_response_success(response)
        data = response.get_json()
        assert data['total_spent'] == 300.0
        assert 'service_intervals' in data

    def test_analytics_with_date_filter(self, client, test_vehicle):
        """Test analytics with date range filtering."""
        client.post('/api/maintenance', json={
            'vehicle_id': test_vehicle,
            'cost': 100.0,
            'date': '2024-01-15'
        })
        client.post('/api/maintenance', json={
            'vehicle_id': test_vehicle,
            'cost': 200.0,
            'date': '2024-06-15'
        })

        response = client.get(
            f'/api/analytics?vehicle_id={test_vehicle}&start_date=2024-01-01&end_date=2024-03-31'
        )
        assert_response_success(response)
        data = response.get_json()
        assert data['total_spent'] == 100.0


class TestFuelEntries:
    """Tests for Fuel entry endpoints."""

    def test_get_fuel_entries(self, client, test_vehicle, sample_fuel_entry):
        """Test getting fuel entries for a vehicle."""
        response = client.get(f'/api/fuel?vehicle_id={test_vehicle}')
        assert_response_success(response)
        data = response.get_json()
        assert len(data) >= 1

    def test_create_fuel_entry(self, client, test_vehicle):
        """Test creating a fuel entry."""
        response = client.post('/api/fuel', json={
            'vehicle_id': test_vehicle,
            'date': '2024-01-15',
            'gallons': 12.5,
            'price_per_gallon': 3.50,
            'total_cost': 43.75
        })
        assert_response_created(response)

    def test_update_fuel_entry(self, client, test_vehicle, sample_fuel_entry):
        """Test updating a fuel entry."""
        response = client.put(f'/api/fuel/{sample_fuel_entry}', json={'gallons': 12.0})
        assert_response_success(response)

    def test_delete_fuel_entry(self, client, test_vehicle, sample_fuel_entry):
        """Test deleting a fuel entry."""
        response = client.delete(f'/api/fuel/{sample_fuel_entry}')
        assert_response_success(response)


class TestReminders:
    """Tests for Reminder endpoints."""

    def test_get_reminders(self, client, test_vehicle, sample_reminder):
        """Test getting reminders for a vehicle."""
        response = client.get(f'/api/reminders?vehicle_id={test_vehicle}')
        assert_response_success(response)

    def test_create_reminder(self, client, test_vehicle):
        """Test creating a reminder."""
        response = client.post('/api/reminders', json={
            'vehicle_id': test_vehicle,
            'type': 'oil_change',
            'interval_miles': 5000,
            'interval_months': 6
        })
        assert_response_created(response)

    def test_update_reminder(self, client, test_vehicle, sample_reminder):
        """Test updating a reminder."""
        response = client.put(f'/api/reminders/{sample_reminder}', json={
            'interval_miles': 7500
        })
        assert_response_success(response)

    def test_delete_reminder(self, client, test_vehicle, sample_reminder):
        """Test deleting a reminder."""
        response = client.delete(f'/api/reminders/{sample_reminder}')
        assert_response_success(response)


class TestVehiclePhotos:
    """Tests for Vehicle photo endpoints."""

    def test_get_photos(self, client, test_vehicle, sample_photo):
        """Test getting vehicle photos."""
        response = client.get(f'/api/vehicle-photos?vehicle_id={test_vehicle}')
        assert_response_success(response)

    def test_create_photo(self, client, test_vehicle):
        """Test creating a vehicle photo."""
        response = client.post('/api/vehicle-photos', json={
            'vehicle_id': test_vehicle,
            'filename': 'new_photo.jpg',
            'caption': 'Test'
        })
        assert_response_created(response)

    def test_primary_photo_flag(self, client, test_vehicle):
        """Test that setting a photo as primary clears other primaries."""
        client.post('/api/vehicle-photos', json={
            'vehicle_id': test_vehicle,
            'filename': 'photo1.jpg',
            'is_primary': True
        })

        response = client.post('/api/vehicle-photos', json={
            'vehicle_id': test_vehicle,
            'filename': 'photo2.jpg',
            'is_primary': True
        })
        assert_response_created(response)


class TestValidation:
    """Tests for input validation."""

    def test_invalid_vehicle_id_on_create(self, client):
        """Test that invalid vehicle_id is handled."""
        response = client.post('/api/maintenance', json={
            'vehicle_id': 99999,
            'date': '2024-01-01'
        })
        assert response.status_code == 201

    def test_invalid_date_format(self, client, test_vehicle):
        """Test that invalid date format is handled."""
        import pytest
        with pytest.raises(Exception):
            response = client.post('/api/maintenance', json={
                'vehicle_id': test_vehicle,
                'date': 'invalid-date'
            })
