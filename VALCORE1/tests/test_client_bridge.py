"""
Unit tests for ClientBridge
"""

import pytest
import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "02_Server_Brain"))
sys.path.insert(0, str(Path(__file__).parent.parent / "03_Shared"))

from exceptions import (
    InputValidationError,
    RoomNotFoundError,
    RoomException,
    LLMException,
    StorageException
)


@pytest.fixture
def mock_llm():
    """Mock LLM"""
    llm = Mock()
    llm.default_model = "test_model"
    llm.generate.return_value = "Test response"
    return llm


@pytest.fixture
def mock_librarian():
    """Mock Librarian"""
    librarian = Mock()
    librarian.add_conversation = Mock()
    librarian.search.return_value = [
        {"text": "result1", "score": 0.9},
        {"text": "result2", "score": 0.8}
    ]
    return librarian


@pytest.fixture
def mock_room_manager():
    """Mock RoomManager"""
    room_manager = Mock()
    room_manager.get_room_config.return_value = {
        'system_prompt': 'Test prompt',
        'llm_temperature': 0.7,
        'max_tokens': 2000
    }
    room_manager.get_room_context.return_value = "Previous context"
    room_manager.switch_room.return_value = True
    room_manager.list_rooms.return_value = ['general', 'office', 'living_room']
    return room_manager


@pytest.fixture
def client_bridge(mock_llm, mock_librarian, mock_room_manager):
    """Create ClientBridge instance"""
    from core.client_bridge import ClientBridge
    bridge = ClientBridge(mock_llm, mock_librarian, mock_room_manager)
    return bridge


@pytest.fixture
def client(client_bridge):
    """Flask test client"""
    client_bridge.app.config['TESTING'] = True
    return client_bridge.app.test_client()


class TestHealthEndpoint:
    """Test /api/health endpoint"""

    def test_health_check_success(self, client):
        """Test successful health check"""
        response = client.get('/api/health')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'ok'
        assert 'model' in data
        assert 'uptime_seconds' in data
        assert 'request_count' in data


class TestProcessEndpoint:
    """Test /api/process endpoint"""

    def test_process_success(self, client, mock_llm, mock_librarian):
        """Test successful request processing"""
        payload = {
            'session_id': 'test_session',
            'user_input': 'Hello, Val',
            'room': 'general'
        }

        response = client.post(
            '/api/process',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'response' in data
        assert 'room' in data
        assert 'latency_ms' in data
        assert data['room'] == 'general'

    def test_process_missing_json(self, client):
        """Test request with no JSON data"""
        response = client.post('/api/process')
        assert response.status_code == 400

        data = json.loads(response.data)
        assert data['status'] == 'validation_error'

    def test_process_missing_user_input(self, client):
        """Test request with missing user_input"""
        payload = {
            'session_id': 'test_session',
            'room': 'general'
        }

        response = client.post(
            '/api/process',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'validation_error'

    def test_process_llm_error(self, client, mock_llm):
        """Test LLM error handling"""
        mock_llm.generate.side_effect = LLMException("Model failed")

        payload = {
            'session_id': 'test_session',
            'user_input': 'Test input',
            'room': 'general'
        }

        response = client.post(
            '/api/process',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 503
        data = json.loads(response.data)
        assert 'error' in data


class TestSearchEndpoint:
    """Test /api/search endpoint"""

    def test_search_success(self, client, mock_librarian):
        """Test successful search"""
        payload = {
            'query': 'test query',
            'room': 'general',
            'max_results': 10
        }

        response = client.post(
            '/api/search',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'results' in data
        assert 'count' in data
        assert data['count'] == 2

    def test_search_missing_query(self, client):
        """Test search with missing query"""
        payload = {'room': 'general'}

        response = client.post(
            '/api/search',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'validation_error'

    def test_search_storage_error(self, client, mock_librarian):
        """Test storage error handling"""
        mock_librarian.search.side_effect = StorageException("Database error")

        payload = {'query': 'test'}

        response = client.post(
            '/api/search',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 500


class TestRoomEndpoints:
    """Test room management endpoints"""

    def test_switch_room_success(self, client, mock_room_manager):
        """Test successful room switch"""
        payload = {
            'session_id': 'test_session',
            'room': 'office'
        }

        response = client.post(
            '/api/room/switch',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'ok'
        assert data['room'] == 'office'

    def test_switch_room_missing_name(self, client):
        """Test room switch with missing room name"""
        payload = {'session_id': 'test_session'}

        response = client.post(
            '/api/room/switch',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 400

    def test_switch_room_not_found(self, client, mock_room_manager):
        """Test room switch with non-existent room"""
        mock_room_manager.switch_room.return_value = False

        payload = {
            'session_id': 'test_session',
            'room': 'nonexistent'
        }

        response = client.post(
            '/api/room/switch',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 404

    def test_list_rooms_success(self, client, mock_room_manager):
        """Test successful room listing"""
        response = client.get('/api/rooms')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'rooms' in data
        assert 'count' in data
        assert data['count'] == 3
        assert 'general' in data['rooms']
