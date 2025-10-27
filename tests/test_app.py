"""
Tests for the Flask application
"""
import pytest
import json
from src.app import create_app

@pytest.fixture
def app():
    """Create test app instance"""
    app = create_app({'TESTING': True, 'DEBUG': False})
    return app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert 'version' in data

def test_verify_endpoint_get(client):
    """Test verify endpoint with GET"""
    response = client.get('/api/verify')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'

def test_verify_endpoint_post(client):
    """Test verify endpoint with POST"""
    response = client.post('/api/verify', 
                          data=json.dumps({'test': 'data'}),
                          content_type='application/json')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'

def test_status_endpoint(client):
    """Test status endpoint"""
    response = client.get('/api/status')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'online'
    assert 'environment' in data