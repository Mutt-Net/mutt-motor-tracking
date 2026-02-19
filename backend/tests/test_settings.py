"""
Tests for Settings endpoints.

Covers CRUD operations, export, backup, and test mode functionality.
"""
import pytest
import sys
import os
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.tests.helpers import (
    assert_response_success, assert_response_created, assert_response_not_found,
    assert_response_bad_request
)


class TestSettings:
    """Tests for Settings CRUD endpoints."""

    def test_get_settings(self, client, app, db_session):
        """Test getting all settings."""
        from backend.models import Setting
        
        with app.app_context():
            setting = Setting(key='test_key', value='test_value', value_type='string')
            db_session.add(setting)
            db_session.commit()
        
        response = client.get('/api/settings')
        assert_response_success(response)
        data = response.get_json()
        assert 'test_key' in data

    def test_get_settings_empty(self, client):
        """Test getting settings when none exist."""
        response = client.get('/api/settings')
        assert_response_success(response)

    def test_create_setting(self, client):
        """Test creating a new setting."""
        response = client.put('/api/settings', json={
            'key': 'new_setting',
            'value': 'new_value',
            'value_type': 'string',
            'description': 'A new setting'
        })
        assert_response_success(response)

    def test_update_existing_setting(self, client, app, db_session):
        """Test updating an existing setting."""
        from backend.models import Setting
        
        with app.app_context():
            setting = Setting(key='existing', value='old', value_type='string')
            db_session.add(setting)
            db_session.commit()
        
        response = client.put('/api/settings', json={
            'key': 'existing',
            'value': 'updated'
        })
        assert_response_success(response)

    def test_create_setting_missing_key(self, client):
        """Test creating setting without key returns 400."""
        response = client.put('/api/settings', json={
            'value': 'some_value'
        })
        assert_response_bad_request(response)

    def test_create_setting_boolean_type(self, client):
        """Test creating a boolean setting."""
        response = client.put('/api/settings', json={
            'key': 'test_boolean',
            'value': 'true',
            'value_type': 'boolean'
        })
        assert_response_success(response)

    def test_create_setting_json_type(self, client):
        """Test creating a JSON setting."""
        response = client.put('/api/settings', json={
            'key': 'test_json',
            'value': {'key': 'value'},
            'value_type': 'json'
        })
        assert_response_success(response)

    def test_create_setting_number_type(self, client):
        """Test creating a number setting."""
        response = client.put('/api/settings', json={
            'key': 'test_number',
            'value': '42.5',
            'value_type': 'number'
        })
        assert_response_success(response)

    def test_update_setting_by_key(self, client, app, db_session):
        """Test updating a setting using key in URL."""
        from backend.models import Setting
        
        with app.app_context():
            setting = Setting(key='url_test', value='old', value_type='string')
            db_session.add(setting)
            db_session.commit()
        
        response = client.put('/api/settings/url_test', json={
            'value': 'new_value'
        })
        assert_response_success(response)

    def test_update_setting_by_key_new(self, client):
        """Test updating a non-existent setting creates it."""
        response = client.put('/api/settings/brand_new', json={
            'value': 'brand_value',
            'value_type': 'string'
        })
        assert_response_success(response)

    def test_delete_setting(self, client, app, db_session):
        """Test deleting a setting."""
        from backend.models import Setting
        
        with app.app_context():
            setting = Setting(key='to_delete', value='value')
            db_session.add(setting)
            db_session.commit()
        
        response = client.delete('/api/settings/to_delete')
        assert_response_success(response)

    def test_delete_setting_not_found(self, client):
        """Test deleting non-existent setting returns 404."""
        response = client.delete('/api/settings/nonexistent')
        assert_response_not_found(response)


class TestSettingsExport:
    """Tests for Settings export and backup endpoints."""

    def test_export_all_data(self, client, app, db_session):
        """Test exporting all data as CSV."""
        from backend.models import Vehicle, Maintenance
        
        with app.app_context():
            vehicle = Vehicle(name='Export Test', make='VW', model='Golf', year=2020, mileage=50000)
            db_session.add(vehicle)
            db_session.commit()
            
            maintenance = Maintenance(vehicle_id=vehicle.id, date=date(2024,1,1), category='oil_change', cost=50.0)
            db_session.add(maintenance)
            db_session.commit()
        
        response = client.get('/api/settings/export')
        assert_response_success(response)
        assert 'text/csv' in response.content_type
        csv_data = response.data.decode('utf-8')
        assert 'VEHICLES' in csv_data
        assert 'MAINTENANCE' in csv_data

    def test_backup_settings(self, client, app, db_session):
        """Test backing up settings as JSON."""
        from backend.models import Setting
        
        with app.app_context():
            setting = Setting(key='backup_test', value='test', value_type='string')
            db_session.add(setting)
            db_session.commit()
        
        response = client.get('/api/settings/backup')
        assert_response_success(response)
        data = response.get_json()
        assert 'settings' in data
        assert 'backup_test' in data['settings']


class TestTestMode:
    """Tests for test mode functionality."""

    def test_create_setting_test_mode_enabled(self, client):
        """Test creating test mode enabled setting."""
        response = client.put('/api/settings', json={
            'key': 'test_mode_enabled',
            'value': 'true',
            'value_type': 'boolean'
        })
        assert_response_success(response)

    def test_create_setting_test_key(self, client):
        """Test creating test key setting."""
        response = client.put('/api/settings', json={
            'key': 'test_key',
            'value': 'test_abc123',
            'value_type': 'string'
        })
        assert_response_success(response)

    def test_create_setting_include_test_data(self, client):
        """Test creating include test data setting."""
        response = client.put('/api/settings', json={
            'key': 'include_test_data',
            'value': 'false',
            'value_type': 'boolean'
        })
        assert_response_success(response)
