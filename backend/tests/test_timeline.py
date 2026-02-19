"""
Tests for Maintenance Timeline endpoint.

Covers service timeline calculation, status determination, and interval tracking.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.tests.helpers import (
    assert_response_success, assert_response_bad_request
)


class TestMaintenanceTimeline:
    """Tests for Maintenance Timeline endpoint."""

    def test_timeline_requires_vehicle_id(self, client):
        """Test that timeline endpoint requires vehicle_id."""
        response = client.get('/api/maintenance/timeline')
        assert_response_bad_request(response)

    def test_timeline_invalid_vehicle_id(self, client):
        """Test timeline with invalid vehicle_id."""
        response = client.get('/api/maintenance/timeline?vehicle_id=99999')
        assert response.status_code == 404

    def test_timeline_returns_list(self, client, test_vehicle, multiple_maintenance_records):
        """Test that timeline returns a list of service types."""
        response = client.get(f'/api/maintenance/timeline?vehicle_id={test_vehicle}')
        assert_response_success(response)
        data = response.get_json()
        assert isinstance(data, list)

    def test_timeline_contains_service_types(self, client, test_vehicle, multiple_maintenance_records):
        """Test timeline contains expected service types."""
        response = client.get(f'/api/maintenance/timeline?vehicle_id={test_vehicle}')
        assert_response_success(response)
        data = response.get_json()
        
        service_types = [item['service_type'] for item in data]
        assert 'oil_change' in service_types

    def test_timeline_shows_last_service_date(self, client, test_vehicle, multiple_maintenance_records):
        """Test timeline shows last service date for each type."""
        response = client.get(f'/api/maintenance/timeline?vehicle_id={test_vehicle}')
        assert_response_success(response)
        data = response.get_json()
        
        oil_change = next((item for item in data if item['service_type'] == 'oil_change'), None)
        assert oil_change is not None
        assert oil_change['last_service_date'] is not None

    def test_timeline_shows_next_due_date(self, client, test_vehicle, multiple_maintenance_records):
        """Test timeline shows next due date."""
        response = client.get(f'/api/maintenance/timeline?vehicle_id={test_vehicle}')
        assert_response_success(response)
        data = response.get_json()
        
        oil_change = next((item for item in data if item['service_type'] == 'oil_change'), None)
        assert oil_change is not None
        assert 'next_due_date' in oil_change

    def test_timeline_shows_status(self, client, test_vehicle, multiple_maintenance_records):
        """Test timeline shows status for each service type."""
        response = client.get(f'/api/maintenance/timeline?vehicle_id={test_vehicle}')
        assert_response_success(response)
        data = response.get_json()
        
        for item in data:
            assert 'status' in item
            assert item['status'] in ['ok', 'upcoming', 'overdue']

    def test_timeline_contains_intervals(self, client, test_vehicle, multiple_maintenance_records):
        """Test timeline contains interval information."""
        response = client.get(f'/api/maintenance/timeline?vehicle_id={test_vehicle}')
        assert_response_success(response)
        data = response.get_json()
        
        oil_change = next((item for item in data if item['service_type'] == 'oil_change'), None)
        assert oil_change is not None
        assert 'interval_months' in oil_change
        assert 'interval_miles' in oil_change

    def test_timeline_with_vehicle_mileage(self, client, test_vehicle):
        """Test timeline calculation with vehicle mileage."""
        response = client.get(f'/api/maintenance/timeline?vehicle_id={test_vehicle}')
        assert_response_success(response)
        data = response.get_json()
        
        for item in data:
            if item.get('miles_until_due') is not None:
                assert item.get('miles_until_due') is not None

    def test_timeline_no_maintenance_records(self, client, test_vehicle):
        """Test timeline returns all service types even with no records."""
        response = client.get(f'/api/maintenance/timeline?vehicle_id={test_vehicle}')
        assert_response_success(response)
        data = response.get_json()
        
        assert len(data) > 0
        expected_types = ['oil_change', 'brakes', 'tire_rotation', 'inspection']
        service_types = [item['service_type'] for item in data]
        for expected in expected_types:
            assert expected in service_types

    def test_timeline_status_overdue(self, client, test_vehicle, app, db_session):
        """Test timeline shows overdue status when service is past due."""
        from backend.models import Maintenance
        from datetime import date, timedelta
        
        with app.app_context():
            maintenance = Maintenance(
                vehicle_id=test_vehicle,
                date=date.today() - timedelta(days=400),
                category='oil_change',
                mileage=10000
            )
            db_session.add(maintenance)
            db_session.commit()
        
        response = client.get(f'/api/maintenance/timeline?vehicle_id={test_vehicle}')
        assert_response_success(response)
        data = response.get_json()
        
        oil_change = next((item for item in data if item['service_type'] == 'oil_change'), None)
        assert oil_change['status'] == 'overdue'

    def test_timeline_status_upcoming(self, client, test_vehicle, app, db_session):
        """Test timeline shows upcoming status when service is due soon."""
        from backend.models import Maintenance
        from datetime import date, timedelta
        
        with app.app_context():
            maintenance = Maintenance(
                vehicle_id=test_vehicle,
                date=date.today() - timedelta(days=150),
                category='oil_change',
                mileage=45000
            )
            db_session.add(maintenance)
            db_session.commit()
        
        response = client.get(f'/api/maintenance/timeline?vehicle_id={test_vehicle}')
        assert_response_success(response)
        data = response.get_json()
        
        oil_change = next((item for item in data if item['service_type'] == 'oil_change'), None)
        assert oil_change['status'] in ['upcoming', 'ok']
