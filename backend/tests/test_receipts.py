"""
Tests for Receipt endpoints.

Covers CRUD operations, filtering by vehicle/maintenance, and error handling.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.tests.helpers import (
    assert_response_success, assert_response_created, assert_response_not_found,
    assert_response_bad_request, create_test_maintenance
)


class TestReceipts:
    """Tests for Receipt CRUD endpoints."""

    def test_get_receipts_empty(self, client, test_vehicle):
        """Test getting receipts returns empty list when none exist."""
        response = client.get(f'/api/receipts?vehicle_id={test_vehicle}')
        assert_response_success(response)
        data = response.get_json()
        assert data == []

    def test_get_receipts(self, client, test_vehicle, sample_receipt):
        """Test getting receipts for a vehicle."""
        response = client.get(f'/api/receipts?vehicle_id={test_vehicle}')
        assert_response_success(response)
        data = response.get_json()
        assert len(data) >= 1
        assert data[0]['vendor'] == 'AutoZone'

    def test_get_receipts_by_maintenance(self, client, test_vehicle, sample_maintenance, sample_receipt):
        """Test filtering receipts by maintenance_id."""
        response = client.get(f'/api/receipts?maintenance_id={sample_maintenance}')
        assert_response_success(response)
        data = response.get_json()
        assert len(data) >= 1
        assert data[0]['maintenance_id'] == sample_maintenance

    def test_create_receipt(self, client, test_vehicle):
        """Test creating a receipt."""
        response = client.post('/api/receipts', json={
            'vehicle_id': test_vehicle,
            'date': '2024-01-15',
            'vendor': 'AutoZone',
            'amount': 50.0,
            'category': 'parts'
        })
        assert_response_created(response)
        data = response.get_json()
        assert 'id' in data

    def test_create_receipt_with_maintenance(self, client, test_vehicle, sample_maintenance):
        """Test creating a receipt linked to maintenance."""
        response = client.post('/api/receipts', json={
            'vehicle_id': test_vehicle,
            'maintenance_id': sample_maintenance,
            'date': '2024-01-15',
            'vendor': 'AutoZone',
            'amount': 50.0,
            'category': 'parts'
        })
        assert_response_created(response)
        data = response.get_json()
        assert 'id' in data

    def test_create_receipt_missing_vehicle_id(self, client):
        """Test creating receipt without vehicle_id returns 400."""
        response = client.post('/api/receipts', json={
            'vendor': 'AutoZone',
            'amount': 50.0
        })
        assert_response_bad_request(response)

    def test_update_receipt(self, client, test_vehicle, sample_receipt):
        """Test updating a receipt."""
        response = client.put(f'/api/receipts/{sample_receipt}', json={
            'amount': 75.0,
            'vendor': 'Updated Vendor'
        })
        assert_response_success(response)

        response = client.get(f'/api/receipts?vehicle_id={test_vehicle}')
        data = response.get_json()
        assert data[0]['amount'] == 75.0

    def test_update_receipt_date(self, client, test_vehicle, sample_receipt):
        """Test updating receipt date."""
        response = client.put(f'/api/receipts/{sample_receipt}', json={
            'date': '2024-02-01'
        })
        assert_response_success(response)

    def test_delete_receipt(self, client, test_vehicle, sample_receipt):
        """Test deleting a receipt."""
        response = client.delete(f'/api/receipts/{sample_receipt}')
        assert_response_success(response)

        response = client.get(f'/api/receipts?vehicle_id={test_vehicle}')
        data = response.get_json()
        assert len(data) == 0

    def test_delete_receipt_not_found(self, client):
        """Test deleting non-existent receipt returns 404."""
        response = client.delete('/api/receipts/99999')
        assert_response_not_found(response)

    def test_get_receipts_multiple(self, client, test_vehicle):
        """Test getting multiple receipts."""
        for i in range(3):
            client.post('/api/receipts', json={
                'vehicle_id': test_vehicle,
                'vendor': f'Vendor {i}',
                'amount': 50.0 + i * 10
            })

        response = client.get(f'/api/receipts?vehicle_id={test_vehicle}')
        assert_response_success(response)
        data = response.get_json()
        assert len(data) == 3
