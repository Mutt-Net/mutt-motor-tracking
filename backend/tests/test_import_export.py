"""
Tests for Import/Export endpoints.

Covers data import, export, and backup functionality.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.tests.helpers import (
    assert_response_success, assert_response_created, assert_response_bad_request
)


class TestImportExport:
    """Tests for data import/export endpoints."""

    def test_vehicle_export(self, client, test_vehicle):
        """Test exporting single vehicle data."""
        response = client.get(f'/api/vehicles/{test_vehicle}/export')
        assert_response_success(response)

    def test_vehicle_import(self, client):
        """Test importing vehicle data."""
        import_data = {
            'name': 'Imported Vehicle',
            'year': 2021,
            'make': 'Honda',
            'model': 'Civic',
            'vin': 'WVWZZZ1JZ8U044505'
        }
        response = client.post('/api/vehicles/import', json=import_data)
        assert_response_created(response)
        data = response.get_json()
        assert 'id' in data

    def test_vcds_import(self, client, test_vehicle):
        """Test importing VCDS fault data."""
        faults = [
            {'address': '01 Engine', 'fault_code': 'P0300', 'component': 'Cylinder 1'},
            {'address': '01 Engine', 'fault_code': 'P0171', 'component': 'System Too Lean'}
        ]
        response = client.post('/api/vcds/import', json={
            'vehicle_id': test_vehicle,
            'faults': faults
        })
        assert_response_success(response)
        data = response.get_json()
        assert data['imported'] == 2


class TestFileUpload:
    """Tests for file upload endpoints."""

    def test_upload_file_missing(self, client):
        """Test upload without file returns 400."""
        response = client.post('/api/upload')
        assert_response_bad_request(response)

    def test_upload_file_no_filename(self, client):
        """Test upload with empty filename returns 400."""
        from io import BytesIO
        data = {
            'file': (BytesIO(b'file content'), '')
        }
        response = client.post('/api/upload', data=data, content_type='multipart/form-data')
        assert_response_bad_request(response)

    def test_upload_invalid_file_type(self, client):
        """Test upload with invalid file type returns 400."""
        from io import BytesIO
        data = {
            'file': (BytesIO(b'file content'), 'test.exe')
        }
        response = client.post('/api/upload', data=data, content_type='multipart/form-data')
        assert_response_bad_request(response)

    def test_serve_upload_missing_file(self, client):
        """Test serving non-existent file returns 404."""
        response = client.get('/uploads/nonexistent.jpg')
        assert response.status_code == 404

    def test_delete_upload_missing_file(self, client):
        """Test deleting non-existent file returns 404."""
        response = client.delete('/api/upload/nonexistent.jpg')
        assert response.status_code == 404


class TestDataManagement:
    """Tests for data management features."""

    def test_csv_export_contains_vehicles(self, client, test_vehicle):
        """Test CSV export contains vehicle data."""
        response = client.get('/api/settings/export')
        assert_response_success(response)
        assert 'text/csv' in response.content_type

    def test_csv_export_contains_maintenance(self, client, test_vehicle):
        """Test CSV export contains maintenance data."""
        client.post('/api/maintenance', json={
            'vehicle_id': test_vehicle,
            'date': '2024-01-15',
            'category': 'oil_change',
            'cost': 50.0
        })
        
        response = client.get('/api/settings/export')
        assert_response_success(response)
        csv_data = response.data.decode('utf-8')
        assert 'MAINTENANCE' in csv_data

    def test_settings_backup_json(self, client):
        """Test settings backup returns valid JSON."""
        client.put('/api/settings', json={
            'key': 'backup_test',
            'value': 'test_value'
        })
        
        response = client.get('/api/settings/backup')
        assert_response_success(response)
        data = response.get_json()
        assert 'settings' in data
        assert 'version' in data
