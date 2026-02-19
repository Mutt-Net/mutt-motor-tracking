"""
Test Helper Utilities for MuttLogbook

Provides reusable helper functions for test assertions and common operations.
"""
import json
import io
from datetime import date, datetime


def assert_response_success(response, status_code=200):
    """Assert that a response was successful."""
    assert response.status_code == status_code, \
        f"Expected {status_code}, got {response.status_code}: {response.get_json()}"


def assert_response_created(response):
    """Assert that a response indicates resource creation."""
    assert response.status_code == 201, \
        f"Expected 201, got {response.status_code}: {response.get_json()}"


def assert_response_error(response, status_code):
    """Assert that a response is an error with expected status code."""
    assert response.status_code == status_code, \
        f"Expected error {status_code}, got {response.status_code}"


def assert_response_not_found(response):
    """Assert that a response is a 404 Not Found."""
    assert_response_error(response, 404)


def assert_response_bad_request(response):
    """Assert that a response is a 400 Bad Request."""
    assert_response_error(response, 400)


def assert_valid_json_response(response, expected_keys=None):
    """Assert that response is valid JSON and optionally contains expected keys."""
    data = response.get_json()
    assert data is not None, "Response is not valid JSON"
    
    if expected_keys:
        for key in expected_keys:
            assert key in data, f"Expected key '{key}' in response: {data}"
    
    return data


def assert_pagination(response, expected_count=None):
    """Assert that response contains pagination metadata."""
    data = response.get_json()
    assert isinstance(data, (list, dict)), "Response is not a list or dict"
    
    if expected_count is not None:
        if isinstance(data, list):
            assert len(data) == expected_count, \
                f"Expected {expected_count} items, got {len(data)}"
    
    return data


def create_test_vehicle(client, **kwargs):
    """Helper to create a test vehicle via API."""
    vehicle_data = {
        'name': kwargs.get('name', 'API Test Vehicle'),
        'year': kwargs.get('year', 2021),
        'make': kwargs.get('make', 'Honda'),
        'model': kwargs.get('model', 'Civic'),
        'vin': kwargs.get('vin', 'WVWZZZ1JZ8U044504'),
        'mileage': kwargs.get('mileage', 30000)
    }
    response = client.post('/api/vehicles', json=vehicle_data)
    assert_response_created(response)
    return response.get_json()['id']


def create_test_maintenance(client, vehicle_id, **kwargs):
    """Helper to create a test maintenance record via API."""
    maintenance_data = {
        'vehicle_id': vehicle_id,
        'date': kwargs.get('date', '2024-01-15'),
        'category': kwargs.get('category', 'oil_change'),
        'cost': kwargs.get('cost', 50.0),
        'mileage': kwargs.get('mileage', 50000)
    }
    response = client.post('/api/maintenance', json=maintenance_data)
    assert_response_created(response)
    return response.get_json()['id']


def create_test_mod(client, vehicle_id, **kwargs):
    """Helper to create a test mod via API."""
    mod_data = {
        'vehicle_id': vehicle_id,
        'date': kwargs.get('date', '2024-01-01'),
        'category': kwargs.get('category', 'engine'),
        'description': kwargs.get('description', 'Test mod'),
        'cost': kwargs.get('cost', 100.0),
        'status': kwargs.get('status', 'completed')
    }
    response = client.post('/api/mods', json=mod_data)
    assert_response_created(response)
    return response.get_json()['id']


def create_test_cost(client, vehicle_id, **kwargs):
    """Helper to create a test cost via API."""
    cost_data = {
        'vehicle_id': vehicle_id,
        'date': kwargs.get('date', '2024-01-10'),
        'category': kwargs.get('category', 'fuel'),
        'amount': kwargs.get('amount', 50.0)
    }
    response = client.post('/api/costs', json=cost_data)
    assert_response_created(response)
    return response.get_json()['id']


def create_test_note(client, vehicle_id, **kwargs):
    """Helper to create a test note via API."""
    note_data = {
        'vehicle_id': vehicle_id,
        'title': kwargs.get('title', 'Test Note'),
        'content': kwargs.get('content', 'Test content'),
        'date': kwargs.get('date', '2024-01-05')
    }
    response = client.post('/api/notes', json=note_data)
    assert_response_created(response)
    return response.get_json()['id']


def create_test_reminder(client, vehicle_id, **kwargs):
    """Helper to create a test reminder via API."""
    reminder_data = {
        'vehicle_id': vehicle_id,
        'type': kwargs.get('type', 'oil_change'),
        'interval_miles': kwargs.get('interval_miles', 5000),
        'interval_months': kwargs.get('interval_months', 6)
    }
    response = client.post('/api/reminders', json=reminder_data)
    assert_response_created(response)
    return response.get_json()['id']


def create_test_fuel(client, vehicle_id, **kwargs):
    """Helper to create a test fuel entry via API."""
    fuel_data = {
        'vehicle_id': vehicle_id,
        'date': kwargs.get('date', '2024-01-20'),
        'gallons': kwargs.get('gallons', 12.5),
        'price_per_gallon': kwargs.get('price_per_gallon', 3.50),
        'total_cost': kwargs.get('total_cost', 43.75),
        'mileage': kwargs.get('mileage', 50500)
    }
    response = client.post('/api/fuel', json=fuel_data)
    assert_response_created(response)
    return response.get_json()['id']


def create_multiple_maintenance(client, vehicle_id, count=5):
    """Create multiple maintenance records for testing."""
    ids = []
    categories = ['oil_change', 'brakes', 'tire_rotation', 'inspection', 'air_filter']
    
    for i in range(count):
        maintenance_id = create_test_maintenance(
            client, vehicle_id,
            category=categories[i % len(categories)],
            cost=50.0 + (i * 10),
            date=date(2024, 1, 1+i)
        )
        ids.append(maintenance_id)
    
    return ids


def get_vehicle_data(client, vehicle_id):
    """Get vehicle data via API."""
    response = client.get(f'/api/vehicles/{vehicle_id}')
    assert_response_success(response)
    return response.get_json()


def delete_entity(client, endpoint, entity_id):
    """Delete an entity via API."""
    response = client.delete(f'/api/{endpoint}/{entity_id}')
    assert_response_success(response)


def update_entity(client, endpoint, entity_id, data):
    """Update an entity via API."""
    response = client.put(f'/api/{endpoint}/{entity_id}', json=data)
    assert_response_success(response)
    return response.get_json()


def parse_date(date_str):
    """Parse date string to date object for comparisons."""
    if isinstance(date_str, date):
        return date_str
    if isinstance(date_str, str):
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    return None


def assert_date_equal(date1, date2):
    """Assert two dates are equal, handling different input types."""
    d1 = parse_date(date1)
    d2 = parse_date(date2)
    assert d1 == d2, f"Dates not equal: {d1} vs {d2}"


def assert_total_in_range(response, expected_total, tolerance=0.01):
    """Assert that a total in the response is within tolerance."""
    data = response.get_json()
    assert 'total_spent' in data, "Response missing total_spent"
    actual = data['total_spent']
    assert abs(actual - expected_total) <= tolerance, \
        f"Total {actual} not within {tolerance} of expected {expected_total}"


def get_csv_data(response):
    """Extract CSV data from response."""
    assert response.status_code == 200
    return response.data.decode('utf-8')


def assert_csv_contains(response, expected_content):
    """Assert that CSV response contains expected content."""
    csv_data = get_csv_data(response)
    assert expected_content in csv_data, \
        f"CSV does not contain '{expected_content}'"


def create_vehicle_with_full_history(client):
    """Create a vehicle with comprehensive history for integration testing."""
    vehicle_id = create_test_vehicle(client, name='Integration Test Vehicle')
    
    create_test_maintenance(client, vehicle_id, category='oil_change', cost=50.0)
    create_test_maintenance(client, vehicle_id, category='brakes', cost=200.0)
    
    create_test_mod(client, vehicle_id, status='completed', cost=500.0)
    create_test_mod(client, vehicle_id, status='planned')
    
    create_test_cost(client, vehicle_id, category='fuel', amount=50.0)
    create_test_cost(client, vehicle_id, category='insurance', amount=500.0)
    
    create_test_fuel(client, vehicle_id)
    
    create_test_reminder(client, vehicle_id)
    
    return vehicle_id


def filter_test_data(client, endpoint, test_key):
    """Filter records by test key."""
    response = client.get(f'/api/{endpoint}?test_key={test_key}')
    assert_response_success(response)
    return response.get_json()


def assert_test_mode_response(response, include_test_data=True):
    """Assert response correctly handles test mode filtering."""
    data = response.get_json()
    
    if isinstance(data, dict) and 'test_key' in data:
        if include_test_data:
            assert data.get('test_key') is not None
        else:
            assert data.get('test_key') is None
    
    return data
