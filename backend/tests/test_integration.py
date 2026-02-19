"""
Integration tests for MuttLogbook.

Tests end-to-end workflows combining multiple endpoints.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.tests.helpers import (
    assert_response_success, assert_response_created
)


class TestVehicleLifecycle:
    """Integration tests for complete vehicle lifecycle."""

    def test_full_vehicle_lifecycle(self, client):
        """Test creating vehicle with all related data."""
        response = client.post('/api/vehicles', json={
            'name': 'Lifecycle Test Vehicle',
            'year': 2021,
            'make': 'VW',
            'model': 'Golf',
            'mileage': 50000
        })
        assert_response_created(response)
        vehicle_id = response.get_json()['id']
        
        response = client.post('/api/maintenance', json={
            'vehicle_id': vehicle_id,
            'date': '2024-01-15',
            'category': 'oil_change',
            'cost': 50.0
        })
        assert_response_created(response)
        
        response = client.post('/api/mods', json={
            'vehicle_id': vehicle_id,
            'date': '2024-01-01',
            'category': 'engine',
            'description': 'ECU Tune',
            'cost': 500.0,
            'status': 'completed'
        })
        assert_response_created(response)
        
        response = client.get(f'/api/dashboard?vehicle_id={vehicle_id}')
        assert_response_success(response)
        data = response.get_json()
        assert data['total_spent'] == 550.0

    def test_vehicle_with_fuel_tracking(self, client):
        """Test vehicle with fuel tracking."""
        response = client.post('/api/vehicles', json={
            'name': 'Fuel Test',
            'year': 2022,
            'make': 'Toyota',
            'model': 'Corolla'
        })
        assert_response_created(response)
        vehicle_id = response.get_json()['id']
        
        for i in range(3):
            client.post('/api/fuel', json={
                'vehicle_id': vehicle_id,
                'date': f'2024-0{i+1}-15',
                'gallons': 12.0,
                'total_cost': 42.0
            })
        
        response = client.get(f'/api/fuel?vehicle_id={vehicle_id}')
        assert_response_success(response)
        data = response.get_json()
        assert len(data) == 3


class TestModWorkflow:
    """Integration tests for mod workflow."""

    def test_mod_status_progression(self, client):
        """Test mod goes from planned to completed."""
        response = client.post('/api/vehicles', json={
            'name': 'Mod Test',
            'year': 2020,
            'make': 'VW',
            'model': 'Golf'
        })
        vehicle_id = response.get_json()['id']
        
        response = client.post('/api/mods', json={
            'vehicle_id': vehicle_id,
            'date': '2024-01-01',
            'category': 'suspension',
            'description': 'Coilovers',
            'cost': 1200.0,
            'status': 'planned'
        })
        assert_response_created(response)
        mod_id = response.get_json()['id']
        
        response = client.put(f'/api/mods/{mod_id}', json={'status': 'in_progress'})
        assert_response_success(response)
        
        response = client.put(f'/api/mods/{mod_id}', json={'status': 'completed'})
        assert_response_success(response)
        
        response = client.get(f'/api/dashboard?vehicle_id={vehicle_id}')
        data = response.get_json()
        assert data['mods_cost'] == 1200.0


class TestServiceHistory:
    """Integration tests for service history."""

    def test_full_service_history(self, client):
        """Test building complete service history."""
        response = client.post('/api/vehicles', json={
            'name': 'Service History Test',
            'year': 2019,
            'make': 'VW',
            'model': 'EOS',
            'mileage': 100000
        })
        vehicle_id = response.get_json()['id']
        
        services = [
            {'category': 'oil_change', 'cost': 50.0},
            {'category': 'brakes', 'cost': 200.0},
            {'category': 'tire_rotation', 'cost': 40.0},
        ]
        
        for service in services:
            client.post('/api/maintenance', json={
                'vehicle_id': vehicle_id,
                'date': '2024-01-01',
                'category': service['category'],
                'cost': service['cost']
            })
        
        response = client.get(f'/api/analytics?vehicle_id={vehicle_id}')
        assert_response_success(response)
        data = response.get_json()
        assert data['total_spent'] == 290.0


class TestErrorHandling:
    """Integration tests for error handling across endpoints."""

    def test_cascade_delete_all_related(self, client):
        """Test deleting vehicle cascades to all related data."""
        response = client.post('/api/vehicles', json={
            'name': 'Delete Test',
            'year': 2020,
            'make': 'VW',
            'model': 'Golf'
        })
        vehicle_id = response.get_json()['id']
        
        client.post('/api/maintenance', json={
            'vehicle_id': vehicle_id,
            'date': '2024-01-01',
            'category': 'oil_change',
            'cost': 50.0
        })
        client.post('/api/mods', json={
            'vehicle_id': vehicle_id,
            'date': '2024-01-01',
            'category': 'engine',
            'description': 'Test'
        })
        client.post('/api/costs', json={
            'vehicle_id': vehicle_id,
            'date': '2024-01-01',
            'category': 'fuel',
            'amount': 50.0
        })
        
        response = client.delete(f'/api/vehicles/{vehicle_id}')
        assert_response_success(response)
        
        response = client.get(f'/api/maintenance?vehicle_id={vehicle_id}')
        assert response.get_json() == []
        
        response = client.get(f'/api/mods?vehicle_id={vehicle_id}')
        assert response.get_json() == []


class TestAnalyticsIntegration:
    """Integration tests for analytics with various data."""

    def test_analytics_with_all_costs(self, client):
        """Test analytics with all cost types."""
        response = client.post('/api/vehicles', json={
            'name': 'Analytics Test',
            'year': 2021,
            'make': 'VW',
            'model': 'Golf'
        })
        vehicle_id = response.get_json()['id']
        
        client.post('/api/maintenance', json={
            'vehicle_id': vehicle_id,
            'date': '2024-01-01',
            'category': 'oil_change',
            'cost': 50.0
        })
        client.post('/api/mods', json={
            'vehicle_id': vehicle_id,
            'date': '2024-01-01',
            'status': 'completed',
            'cost': 500.0
        })
        client.post('/api/costs', json={
            'vehicle_id': vehicle_id,
            'date': '2024-01-01',
            'category': 'insurance',
            'amount': 500.0
        })
        client.post('/api/fuel', json={
            'vehicle_id': vehicle_id,
            'date': '2024-01-01',
            'total_cost': 50.0
        })
        
        response = client.get(f'/api/analytics?vehicle_id={vehicle_id}')
        assert_response_success(response)
        data = response.get_json()
        
        assert 'monthly_spending' in data
        assert 'yearly_spending' in data
        assert 'category_spending' in data

    def test_analytics_date_filtering(self, client):
        """Test analytics respects date filters."""
        response = client.post('/api/vehicles', json={
            'name': 'Date Filter Test',
            'year': 2021,
            'make': 'VW',
            'model': 'Golf'
        })
        vehicle_id = response.get_json()['id']
        
        client.post('/api/maintenance', json={
            'vehicle_id': vehicle_id,
            'date': '2024-01-01',
            'cost': 100.0
        })
        client.post('/api/maintenance', json={
            'vehicle_id': vehicle_id,
            'date': '2024-06-01',
            'cost': 100.0
        })
        
        response = client.get(
            f'/api/analytics?vehicle_id={vehicle_id}&start_date=2024-01-01&end_date=2024-03-31'
        )
        assert_response_success(response)
        data = response.get_json()
        assert data['total_spent'] == 100.0


class TestSettingsIntegration:
    """Integration tests for settings affecting other endpoints."""

    def test_service_intervals_in_analytics(self, client):
        """Test that service intervals appear in analytics."""
        response = client.post('/api/vehicles', json={
            'name': 'Interval Test',
            'year': 2021,
            'make': 'VW',
            'model': 'Golf',
            'mileage': 50000
        })
        vehicle_id = response.get_json()['id']
        
        client.post('/api/maintenance', json={
            'vehicle_id': vehicle_id,
            'date': '2024-01-01',
            'category': 'oil_change',
            'cost': 50.0
        })
        
        response = client.get(f'/api/analytics?vehicle_id={vehicle_id}')
        assert_response_success(response)
        data = response.get_json()
        assert 'service_intervals' in data

    def test_timeline_includes_all_services(self, client):
        """Test timeline includes all service types."""
        response = client.post('/api/vehicles', json={
            'name': 'Timeline Test',
            'year': 2021,
            'make': 'VW',
            'model': 'Golf'
        })
        vehicle_id = response.get_json()['id']
        
        response = client.get(f'/api/maintenance/timeline?vehicle_id={vehicle_id}')
        assert_response_success(response)
        data = response.get_json()
        
        service_types = [item['service_type'] for item in data]
        assert 'oil_change' in service_types
        assert 'brakes' in service_types
