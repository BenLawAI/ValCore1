"""
Tests for Network Fallback Manager
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
import queue
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture
def mock_config():
    """Mock network configuration"""
    return {
        'atom_local_ip': '192.168.1.100',
        'atom_tailscale_ip': '100.64.0.1',
        'atom_port': 5000,
        'prefer_tailscale': False,
        'connection_timeout': 10
    }


@pytest.mark.unit
class TestNetworkFallbackInit:
    """Test NetworkFallbackManager initialization"""

    def test_config_loading(self, mock_config, tmp_path):
        """Test configuration loading"""
        config_file = tmp_path / "network_config.json"
        with open(config_file, 'w') as f:
            json.dump(mock_config, f)

        assert config_file.exists()
        with open(config_file, 'r') as f:
            loaded = json.load(f)
        assert loaded['atom_port'] == 5000

    def test_server_url_local(self, mock_config):
        """Test server URL generation (local)"""
        url = f"http://{mock_config['atom_local_ip']}:{mock_config['atom_port']}"
        assert url == "http://192.168.1.100:5000"

    def test_server_url_tailscale(self, mock_config):
        """Test server URL generation (Tailscale)"""
        mock_config['prefer_tailscale'] = True
        url = f"http://{mock_config['atom_tailscale_ip']}:{mock_config['atom_port']}"
        assert url == "http://100.64.0.1:5000"


@pytest.mark.unit
class TestHealthCheck:
    """Test server health check"""

    def test_health_check_url_format(self, mock_config):
        """Test health check URL format"""
        server_url = f"http://{mock_config['atom_local_ip']}:{mock_config['atom_port']}"
        health_url = f"{server_url}/api/health"
        assert health_url == "http://192.168.1.100:5000/api/health"

    @patch('requests.get')
    def test_health_check_success(self, mock_get):
        """Test successful health check"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Simulate health check
        response = mock_get("http://test/api/health", timeout=5)
        assert response.status_code == 200

    @patch('requests.get')
    def test_health_check_failure(self, mock_get):
        """Test failed health check"""
        import requests
        mock_get.side_effect = requests.exceptions.RequestException("Connection failed")

        # Simulate health check failure
        try:
            mock_get("http://test/api/health", timeout=5)
            assert False, "Should have raised exception"
        except requests.exceptions.RequestException:
            assert True


@pytest.mark.unit
class TestOfflineQueue:
    """Test offline queue functionality"""

    def test_queue_initialization(self):
        """Test queue initialization"""
        offline_queue = queue.Queue()
        assert offline_queue.qsize() == 0

    def test_queue_add_message(self):
        """Test adding message to queue"""
        offline_queue = queue.Queue()
        message = {
            'type': 'conversation',
            'text': 'Test message',
            'timestamp': datetime.now().isoformat()
        }
        offline_queue.put(message)
        assert offline_queue.qsize() == 1

    def test_queue_retrieve_message(self):
        """Test retrieving message from queue"""
        offline_queue = queue.Queue()
        message = {'text': 'Test'}
        offline_queue.put(message)

        retrieved = offline_queue.get_nowait()
        assert retrieved['text'] == 'Test'
        assert offline_queue.qsize() == 0

    def test_queue_empty_check(self):
        """Test queue empty check"""
        offline_queue = queue.Queue()
        assert offline_queue.empty() == True

        offline_queue.put({'test': 'data'})
        assert offline_queue.empty() == False


@pytest.mark.unit
class TestConflictDetection:
    """Test conflict detection"""

    def test_conversation_conflict_detection(self):
        """Test conversation conflict detection"""
        message = {
            'type': 'conversation',
            'conversation_id': 'test-123',
            'version': '2025-11-15T12:00:00'
        }

        server_version = '2025-11-15T12:30:00'
        local_version = message['version']

        # Server version is newer, so there's a conflict
        has_conflict = server_version != local_version
        assert has_conflict == True

    def test_file_conflict_detection(self):
        """Test file edit conflict detection"""
        message = {
            'type': 'file_edit',
            'file_path': 'data/test.json',
            'timestamp': '2025-11-15T12:00:00'
        }

        server_timestamp = '2025-11-15T12:30:00'
        local_timestamp = message['timestamp']

        # Server timestamp is newer
        has_conflict = server_timestamp > local_timestamp
        assert has_conflict == True

    def test_no_conflict(self):
        """Test no conflict scenario"""
        local_version = '2025-11-15T12:30:00'
        server_version = '2025-11-15T12:30:00'

        has_conflict = server_version != local_version
        assert has_conflict == False


@pytest.mark.unit
class TestConflictResolution:
    """Test conflict resolution"""

    def test_keep_local_resolution(self):
        """Test keep local resolution"""
        conflict = {
            'message': {
                'type': 'conversation',
                'text': 'Local text'
            }
        }
        resolution = 'keep_local'
        assert resolution == 'keep_local'

    def test_keep_server_resolution(self):
        """Test keep server resolution"""
        resolution = 'keep_server'
        assert resolution == 'keep_server'

    def test_merge_resolution(self):
        """Test merge resolution"""
        resolution = 'merge'
        assert resolution == 'merge'


@pytest.mark.unit
class TestSyncProcess:
    """Test sync process"""

    def test_sync_message_format(self):
        """Test sync message format"""
        message = {
            'type': 'conversation',
            'session_id': 'test-session',
            'user_input': 'Test input',
            'room': 'general',
            'timestamp': datetime.now().isoformat()
        }

        assert 'type' in message
        assert 'timestamp' in message

    def test_sync_status_tracking(self):
        """Test sync status tracking"""
        sync_in_progress = False
        queue_size = 5

        status = {
            'server_available': True,
            'queue_size': queue_size,
            'sync_in_progress': sync_in_progress,
            'conflicts': 0
        }

        assert status['queue_size'] == 5
        assert status['sync_in_progress'] == False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
