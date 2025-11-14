"""
Unit tests for Client Bridge (Server HTTP API)
"""

import pytest
import json
from unittest.mock import Mock, patch
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "02_Server_Brain"))

from core.client_bridge import ClientBridge


@pytest.fixture
def client_bridge(mock_llm, mock_librarian, mock_room_manager):
    """Create ClientBridge instance with mocks"""
    bridge = ClientBridge(mock_llm, mock_librarian, mock_room_manager)
    bridge.app.config['TESTING'] = True
    return bridge


@pytest.fixture
def client(client_bridge):
    """Create Flask test client"""
    return client_bridge.app.test_client()


@pytest.mark.unit
class TestClientBridge:
    """Test ClientBridge endpoints"""

    def test_health_endpoint(self, client):
        """Test /api/health endpoint"""
        response = client.get('/api/health')

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['status'] == 'ok'
        assert 'model' in data
        assert 'uptime_seconds' in data
        assert 'request_count' in data

    def test_process_request_success(self, client, mock_llm, mock_librarian):
        """Test /api/process endpoint with successful request"""
        request_data = {
            "session_id": "test-session",
            "user_input": "Hello, how are you?",
            "room": "general"
        }

        response = client.post(
            '/api/process',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        assert 'response' in data
        assert data['room'] == 'general'
        assert 'timestamp' in data
        assert 'latency_ms' in data

        # Verify mocks were called
        mock_llm.generate.assert_called_once()
        mock_librarian.add_conversation.assert_called_once()

    def test_process_request_no_room_manager(self, mock_llm, mock_librarian):
        """Test processing without room manager"""
        bridge = ClientBridge(mock_llm, mock_librarian, room_manager=None)
        bridge.app.config['TESTING'] = True
        client = bridge.app.test_client()

        request_data = {
            "user_input": "Test message"
        }

        response = client.post(
            '/api/process',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        assert response.status_code == 200

    def test_search_library(self, client, mock_librarian):
        """Test /api/search endpoint"""
        mock_librarian.search.return_value = [
            {"text": "Result 1", "score": 0.9},
            {"text": "Result 2", "score": 0.8}
        ]

        request_data = {
            "query": "test query",
            "room": "general",
            "max_results": 10
        }

        response = client.post(
            '/api/search',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        assert len(data['results']) == 2
        assert data['count'] == 2

        mock_librarian.search.assert_called_once()

    def test_switch_room_success(self, client, mock_room_manager):
        """Test /api/room/switch endpoint success"""
        request_data = {
            "session_id": "test-session",
            "room": "coding"
        }

        response = client.post(
            '/api/room/switch',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['status'] == 'ok'
        assert data['room'] == 'coding'

        mock_room_manager.switch_room.assert_called_once_with("test-session", "coding")

    def test_switch_room_not_found(self, client, mock_room_manager):
        """Test switching to non-existent room"""
        mock_room_manager.switch_room.return_value = False

        request_data = {
            "session_id": "test-session",
            "room": "nonexistent"
        }

        response = client.post(
            '/api/room/switch',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        assert response.status_code == 404

    def test_switch_room_missing_parameter(self, client):
        """Test switching room without room parameter"""
        request_data = {
            "session_id": "test-session"
        }

        response = client.post(
            '/api/room/switch',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        assert response.status_code == 400

    def test_list_rooms(self, client, mock_room_manager):
        """Test /api/rooms endpoint"""
        response = client.get('/api/rooms')

        assert response.status_code == 200
        data = json.loads(response.data)

        assert 'rooms' in data
        assert data['count'] == 3
        assert 'general' in data['rooms']

    def test_conversation_version_endpoint(self, client, mock_librarian):
        """Test /api/conversation/version endpoint"""
        mock_librarian.search.return_value = [
            {"metadata": {"version": 5, "timestamp": "2025-11-14T10:00:00"}}
        ]

        request_data = {
            "conversation_id": "test-conv-123"
        }

        response = client.post(
            '/api/conversation/version',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['conversation_id'] == "test-conv-123"
        assert data['version'] == 5
        assert data['status'] == 'ok'

    def test_conversation_version_not_found(self, client, mock_librarian):
        """Test conversation version when conversation doesn't exist"""
        mock_librarian.search.return_value = []

        request_data = {
            "conversation_id": "nonexistent"
        }

        response = client.post(
            '/api/conversation/version',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['exists'] == False

    def test_file_timestamp_endpoint(self, client, mock_librarian):
        """Test /api/file/timestamp endpoint"""
        mock_librarian.search.return_value = [
            {"metadata": {"timestamp": "2025-11-14T10:00:00"}}
        ]

        request_data = {
            "file_path": "test/file.txt"
        }

        response = client.post(
            '/api/file/timestamp',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['file_path'] == "test/file.txt"
        assert data['timestamp'] == "2025-11-14T10:00:00"
        assert data['exists'] == True

    def test_fetch_conversation_endpoint(self, client, mock_librarian):
        """Test /api/conversation/fetch endpoint"""
        mock_librarian.search.return_value = [
            {"text": "Message 1", "metadata": {}},
            {"text": "Message 2", "metadata": {}}
        ]

        request_data = {
            "conversation_id": "test-conv",
            "room": "general"
        }

        response = client.post(
            '/api/conversation/fetch',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['conversation_id'] == "test-conv"
        assert data['count'] == 2
        assert len(data['results']) == 2
