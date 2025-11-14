"""
Unit tests for ClientBridge (Flask API)
Tests API endpoints, authentication, CORS, and input validation
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

# Import ClientBridge
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "02_Server_Brain"))


@pytest.mark.unit
class TestClientBridge:
    """Test suite for ClientBridge Flask API"""

    @pytest.fixture
    def mock_llm(self):
        """Mock LLM interface"""
        llm = Mock()
        llm.default_model = "test-model"
        llm.generate = Mock(return_value="Test response from LLM")
        return llm

    @pytest.fixture
    def mock_librarian(self):
        """Mock Librarian"""
        librarian = Mock()
        librarian.add_conversation = Mock()
        librarian.search = Mock(return_value=[
            {"text": "test query", "similarity": 0.95}
        ])
        return librarian

    @pytest.fixture
    def mock_room_manager(self):
        """Mock RoomManager"""
        room_manager = Mock()
        room_manager.get_room_config = Mock(return_value={
            'system_prompt': 'Test prompt',
            'llm_temperature': 0.7,
            'max_tokens': 2000
        })
        room_manager.get_room_context = Mock(return_value="Test context")
        room_manager.switch_room = Mock(return_value=True)
        room_manager.list_rooms = Mock(return_value=[
            {'name': 'general', 'description': 'General room'},
            {'name': 'truck', 'description': 'Truck room'}
        ])
        return room_manager

    @pytest.fixture
    def client_bridge(self, mock_llm, mock_librarian, mock_room_manager, monkeypatch):
        """Create ClientBridge instance with mocks"""
        # Set test API key
        monkeypatch.setenv('VALCORE_API_KEY', 'test-api-key-12345')

        from core.client_bridge import ClientBridge

        bridge = ClientBridge(mock_llm, mock_librarian, mock_room_manager)
        return bridge

    @pytest.fixture
    def client_bridge_no_auth(self, mock_llm, mock_librarian, mock_room_manager, monkeypatch):
        """Create ClientBridge without authentication"""
        # Remove API key
        monkeypatch.delenv('VALCORE_API_KEY', raising=False)

        from core.client_bridge import ClientBridge

        bridge = ClientBridge(mock_llm, mock_librarian, mock_room_manager)
        return bridge

    def test_initialization_with_auth(self, client_bridge):
        """Test ClientBridge initialization with authentication"""
        assert client_bridge.auth_enabled is True
        assert client_bridge.api_key == 'test-api-key-12345'

    def test_initialization_without_auth(self, client_bridge_no_auth):
        """Test ClientBridge initialization without authentication"""
        assert client_bridge_no_auth.auth_enabled is False

    def test_health_endpoint_no_auth_required(self, client_bridge):
        """Test /api/health endpoint (public, no auth required)"""
        client = client_bridge.app.test_client()

        response = client.get('/api/health')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'ok'
        assert 'model' in data
        assert 'uptime_seconds' in data
        assert 'auth_enabled' in data

    def test_process_endpoint_with_valid_auth(self, client_bridge):
        """Test /api/process with valid authentication"""
        client = client_bridge.app.test_client()

        response = client.post(
            '/api/process',
            json={
                'user_input': 'Hello, VAL!',
                'session_id': 'test-session',
                'room': 'general'
            },
            headers={'X-API-Key': 'test-api-key-12345'}
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'response' in data
        assert 'timestamp' in data
        assert 'latency_ms' in data

    def test_process_endpoint_without_auth(self, client_bridge):
        """Test /api/process without authentication header"""
        client = client_bridge.app.test_client()

        response = client.post(
            '/api/process',
            json={'user_input': 'Hello, VAL!'}
        )

        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Unauthorized'

    def test_process_endpoint_invalid_api_key(self, client_bridge):
        """Test /api/process with invalid API key"""
        client = client_bridge.app.test_client()

        response = client.post(
            '/api/process',
            json={'user_input': 'Hello, VAL!'},
            headers={'X-API-Key': 'wrong-key'}
        )

        assert response.status_code == 401

    def test_process_endpoint_missing_required_field(self, client_bridge):
        """Test /api/process with missing required field"""
        client = client_bridge.app.test_client()

        response = client.post(
            '/api/process',
            json={'session_id': 'test'},  # Missing user_input
            headers={'X-API-Key': 'test-api-key-12345'}
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'user_input' in data['message']

    def test_process_endpoint_empty_input(self, client_bridge):
        """Test /api/process with empty input"""
        client = client_bridge.app.test_client()

        response = client.post(
            '/api/process',
            json={'user_input': '   '},  # Empty after strip
            headers={'X-API-Key': 'test-api-key-12345'}
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'empty' in data['message'].lower()

    def test_process_endpoint_invalid_room(self, client_bridge):
        """Test /api/process with invalid room name"""
        client = client_bridge.app.test_client()

        response = client.post(
            '/api/process',
            json={
                'user_input': 'Hello',
                'room': 'invalid_room'  # Not in whitelist
            },
            headers={'X-API-Key': 'test-api-key-12345'}
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'room' in data['message'].lower()

    def test_process_endpoint_input_too_long(self, client_bridge):
        """Test /api/process with input exceeding max length"""
        client = client_bridge.app.test_client()

        # Create input > 50,000 characters
        long_input = 'a' * 50001

        response = client.post(
            '/api/process',
            json={'user_input': long_input},
            headers={'X-API-Key': 'test-api-key-12345'}
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'length' in data['message'].lower() or 'exceeds' in data['message'].lower()

    def test_search_endpoint_with_auth(self, client_bridge):
        """Test /api/search with authentication"""
        client = client_bridge.app.test_client()

        response = client.post(
            '/api/search',
            json={
                'query': 'test query',
                'max_results': 10
            },
            headers={'X-API-Key': 'test-api-key-12345'}
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'results' in data
        assert 'count' in data

    def test_search_endpoint_with_room_filter(self, client_bridge):
        """Test /api/search with room filter"""
        client = client_bridge.app.test_client()

        response = client.post(
            '/api/search',
            json={
                'query': 'test query',
                'room': 'general',
                'max_results': 5
            },
            headers={'X-API-Key': 'test-api-key-12345'}
        )

        assert response.status_code == 200

    def test_search_endpoint_empty_query(self, client_bridge):
        """Test /api/search with empty query"""
        client = client_bridge.app.test_client()

        response = client.post(
            '/api/search',
            json={'query': '  '},
            headers={'X-API-Key': 'test-api-key-12345'}
        )

        assert response.status_code == 400

    def test_search_endpoint_invalid_max_results(self, client_bridge):
        """Test /api/search with invalid max_results"""
        client = client_bridge.app.test_client()

        # Test max_results > 100
        response = client.post(
            '/api/search',
            json={
                'query': 'test',
                'max_results': 150
            },
            headers={'X-API-Key': 'test-api-key-12345'}
        )

        assert response.status_code == 400

    def test_room_switch_endpoint(self, client_bridge):
        """Test /api/room/switch endpoint"""
        client = client_bridge.app.test_client()

        response = client.post(
            '/api/room/switch',
            json={
                'room': 'truck',
                'session_id': 'test-session'
            },
            headers={'X-API-Key': 'test-api-key-12345'}
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'ok'
        assert data['room'] == 'truck'

    def test_room_switch_invalid_room(self, client_bridge):
        """Test /api/room/switch with invalid room"""
        client = client_bridge.app.test_client()

        response = client.post(
            '/api/room/switch',
            json={'room': 'invalid_room'},
            headers={'X-API-Key': 'test-api-key-12345'}
        )

        assert response.status_code == 400

    def test_list_rooms_endpoint(self, client_bridge):
        """Test /api/rooms endpoint"""
        client = client_bridge.app.test_client()

        response = client.get(
            '/api/rooms',
            headers={'X-API-Key': 'test-api-key-12345'}
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'rooms' in data
        assert 'count' in data

    def test_cors_validation(self, client_bridge):
        """Test CORS origin validation"""
        # Test allowed origins
        allowed_origins = [
            'http://localhost:3000',
            'http://127.0.0.1:5000',
            'http://192.168.1.100:8080',
        ]

        for origin in allowed_origins:
            result = client_bridge._validate_cors_origin(origin)
            assert result is True, f"Origin {origin} should be allowed"

    def test_cors_rejection(self, client_bridge):
        """Test CORS origin rejection"""
        # Test rejected origins
        rejected_origins = [
            'http://evil.com',
            'https://malicious-site.net',
            'http://1.2.3.4:8000',
        ]

        for origin in rejected_origins:
            result = client_bridge._validate_cors_origin(origin)
            assert result is False, f"Origin {origin} should be rejected"

    def test_input_validation_method(self, client_bridge):
        """Test _validate_input helper method"""
        # Valid input
        valid, error = client_bridge._validate_input(
            {'name': 'test', 'count': 5},
            required_fields=['name'],
            optional_fields={'count': (int, (1, 10))}
        )
        assert valid is True
        assert error is None

        # Missing required field
        valid, error = client_bridge._validate_input(
            {'count': 5},
            required_fields=['name']
        )
        assert valid is False
        assert 'name' in error

        # Type mismatch
        valid, error = client_bridge._validate_input(
            {'name': 123},  # Should be string
            optional_fields={'name': (str, 100)}
        )
        assert valid is False
        assert 'type' in error.lower()

        # String too long
        valid, error = client_bridge._validate_input(
            {'name': 'a' * 101},
            optional_fields={'name': (str, 100)}
        )
        assert valid is False
        assert 'length' in error.lower()

        # Number out of range
        valid, error = client_bridge._validate_input(
            {'count': 150},
            optional_fields={'count': (int, (1, 100))}
        )
        assert valid is False
        assert 'between' in error.lower()


@pytest.mark.integration
class TestClientBridgeIntegration:
    """Integration tests for ClientBridge"""

    def test_full_request_flow(self, client_bridge, mock_llm, mock_librarian):
        """Test complete request processing flow"""
        client = client_bridge.app.test_client()

        # Send request
        response = client.post(
            '/api/process',
            json={
                'user_input': 'What is the weather?',
                'session_id': 'integration-test',
                'room': 'general'
            },
            headers={'X-API-Key': 'test-api-key-12345'}
        )

        # Verify response
        assert response.status_code == 200
        data = json.loads(response.data)

        # Verify LLM was called
        mock_llm.generate.assert_called_once()

        # Verify librarian stored conversation
        mock_librarian.add_conversation.assert_called_once()

    def test_no_auth_flow(self, client_bridge_no_auth):
        """Test request flow without authentication"""
        client = client_bridge_no_auth.app.test_client()

        # Should work without API key when auth is disabled
        response = client.post(
            '/api/process',
            json={'user_input': 'Hello'},
        )

        assert response.status_code == 200
