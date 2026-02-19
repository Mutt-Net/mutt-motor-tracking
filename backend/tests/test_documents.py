"""
Tests for Service Document endpoints.

Covers document upload, retrieval, and deletion.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.tests.helpers import (
    assert_response_success, assert_response_created, assert_response_not_found,
    assert_response_bad_request
)


class TestDocuments:
    """Tests for Service Document endpoints."""

    def test_get_documents_empty(self, client, test_vehicle):
        """Test getting documents returns empty list when none exist."""
        response = client.get(f'/api/documents?vehicle_id={test_vehicle}')
        assert_response_success(response)
        data = response.get_json()
        assert data == []

    def test_get_documents(self, client, test_vehicle, sample_document):
        """Test getting documents for a vehicle."""
        response = client.get(f'/api/documents?vehicle_id={test_vehicle}')
        assert_response_success(response)
        data = response.get_json()
        assert len(data) >= 1
        assert data[0]['title'] == 'Service Manual'

    def test_create_document_missing_vehicle_id(self, client):
        """Test creating document without vehicle_id returns 400."""
        response = client.post('/api/documents', json={
            'title': 'Test Document'
        })
        assert_response_bad_request(response)

    def test_create_document_invalid_vehicle(self, client):
        """Test creating document with invalid vehicle_id returns error."""
        response = client.post('/api/documents', json={
            'vehicle_id': 99999,
            'title': 'Test Document'
        })
        assert response.status_code in [400, 404]

    def test_delete_document(self, client, test_vehicle, sample_document):
        """Test deleting a document."""
        response = client.delete(f'/api/documents/{sample_document}')
        assert_response_success(response)

    def test_delete_document_not_found(self, client):
        """Test deleting non-existent document returns 404."""
        response = client.delete('/api/documents/99999')
        assert_response_not_found(response)
