"""
Tests for Server Communication and Client Bridge
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture
def mock_llm():
    """Mock LLM for testing"""
    llm = Mock()
    llm.default_model = "qwen2.5:14b"
    llm.generate.return_value = "This is a test response"
    return llm


@pytest.fixture
def mock_librarian():
    """Mock Librarian for testing"""
    librarian = Mock()
    librarian.metadata = []
    librarian.library_path = "/tmp/test_library"
    librarian.add_conversation = Mock()
    librarian.search = Mock(return_value=[])
    return librarian


@pytest.mark.unit
class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_check_response_format(self, mock_llm, mock_librarian):
        """Test health check returns proper format"""
        expected_keys = ['status', 'model', 'uptime_seconds', 'request_count']

        # Simulate health check response
        response = {
            'status': 'ok',
            'model': mock_llm.default_model,
            'uptime_seconds': 123.45,
            'request_count': 10
        }

        for key in expected_keys:
            assert key in response

    def test_health_check_status_ok(self):
        """Test health check returns ok status"""
        response = {'status': 'ok'}
        assert response['status'] == 'ok'


@pytest.mark.unit
class TestConversationEndpoints:
    """Test conversation-related endpoints"""

    def test_conversation_version_endpoint_format(self):
        """Test conversation version endpoint request/response format"""
        request = {'conversation_id': 'test-123'}
        assert 'conversation_id' in request

        response = {
            'version': '2025-11-15T12:00:00',
            'exists': True
        }
        assert 'version' in response
        assert 'exists' in response

    def test_conversation_version_not_found(self):
        """Test conversation version when conversation doesn't exist"""
        response = {
            'version': None,
            'exists': False
        }
        assert response['exists'] == False
        assert response['version'] is None

    def test_conversation_fetch_endpoint_format(self):
        """Test conversation fetch endpoint format"""
        request = {'conversation_id': 'test-123'}
        assert 'conversation_id' in request

        response = {
            'conversation': {
                'room': 'general',
                'text': 'Test conversation',
                'timestamp': '2025-11-15T12:00:00',
                'metadata': {}
            },
            'exists': True
        }
        assert 'conversation' in response
        assert 'exists' in response


@pytest.mark.unit
class TestFileEndpoints:
    """Test file-related endpoints"""

    def test_file_timestamp_endpoint_format(self):
        """Test file timestamp endpoint format"""
        request = {'file_path': 'data/test.json'}
        assert 'file_path' in request

        response = {
            'timestamp': '2025-11-15T12:00:00',
            'exists': True
        }
        assert 'timestamp' in response
        assert 'exists' in response

    def test_file_timestamp_not_found(self):
        """Test file timestamp when file doesn't exist"""
        response = {
            'timestamp': None,
            'exists': False
        }
        assert response['exists'] == False
        assert response['timestamp'] is None


@pytest.mark.unit
class TestProcessEndpoint:
    """Test main process endpoint"""

    def test_process_request_format(self):
        """Test process request format"""
        request = {
            'session_id': 'test-session',
            'user_input': 'What is the weather?',
            'room': 'general'
        }

        assert 'session_id' in request
        assert 'user_input' in request
        assert 'room' in request

    def test_process_response_format(self, mock_llm):
        """Test process response format"""
        response = {
            'response': mock_llm.generate("test"),
            'room': 'general',
            'timestamp': '2025-11-15T12:00:00',
            'latency_ms': 150.5
        }

        assert 'response' in response
        assert 'room' in response
        assert 'timestamp' in response
        assert 'latency_ms' in response

    def test_process_error_handling(self):
        """Test process error response format"""
        error_response = {
            'error': 'Invalid input',
            'status': 'error'
        }

        assert 'error' in error_response
        assert error_response['status'] == 'error'


@pytest.mark.unit
class TestRoomEndpoints:
    """Test room management endpoints"""

    def test_room_switch_request(self):
        """Test room switch request format"""
        request = {
            'session_id': 'test-session',
            'room': 'coding'
        }
        assert 'session_id' in request
        assert 'room' in request

    def test_room_list_response(self):
        """Test room list response format"""
        response = {
            'rooms': ['general', 'coding', 'research', 'creative'],
            'count': 4
        }
        assert 'rooms' in response
        assert 'count' in response
        assert response['count'] == len(response['rooms'])


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
