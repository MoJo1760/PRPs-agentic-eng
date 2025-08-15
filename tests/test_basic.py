"""Basic tests for Flask PRP Wrapper."""

import pytest
from flask_prp_wrapper.app import create_app


@pytest.fixture
def app():
    """Create test application."""
    app = create_app('testing')
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


def test_app_creation(app):
    """Test that app can be created."""
    assert app is not None
    assert app.config['TESTING'] is True


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    
    data = response.get_json()
    assert 'status' in data
    assert data['status'] == 'healthy'


def test_index_page(client):
    """Test that index page loads."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Flask PRP Generator' in response.data


def test_api_status_endpoint(client):
    """Test API status endpoint."""
    response = client.get('/api/v1/status')
    assert response.status_code == 200
    
    data = response.get_json()
    assert 'status' in data
    assert 'statistics' in data
    assert 'services' in data