"""
Unit tests for Network Fallback Manager
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "01_Client_Brain"))

from core.network_fallback import NetworkFallbackManager


@pytest.fixture
def network_config_file(temp_dir):
    """Create a temporary network config file"""
    config = {
        "atom_local_ip": "192.168.1.100",
        "atom_tailscale_ip": "100.64.0.1",
        "atom_port": 5000,
        "prefer_tailscale": False,
        "connection_timeout": 30
    }
    config_file = temp_dir / "network_config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f)
    return config_file


@pytest.fixture
def fallback_manager(network_config_file):
    """Create a NetworkFallbackManager instance"""
    return NetworkFallbackManager(str(network_config_file))


@pytest.mark.unit
class TestNetworkFallbackManager:
    """Test NetworkFallbackManager class"""

    def test_initialization(self, fallback_manager):
        """Test that manager initializes correctly"""
        assert fallback_manager is not None
        assert fallback_manager.server_available == False
        assert fallback_manager.offline_queue.qsize() == 0

    def test_get_server_url_local(self, fallback_manager):
        """Test getting local server URL"""
        url = fallback_manager.get_server_url()
        assert url == "http://192.168.1.100:5000"

    def test_get_server_url_tailscale(self, fallback_manager):
        """Test getting Tailscale server URL"""
        fallback_manager.config['prefer_tailscale'] = True
        url = fallback_manager.get_server_url()
        assert url == "http://100.64.0.1:5000"

    @patch('requests.get')
    def test_check_server_health_success(self, mock_get, fallback_manager):
        """Test successful server health check"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = fallback_manager.check_server_health()

        assert result == True
        assert fallback_manager.server_available == True
        mock_get.assert_called_once()

    @patch('requests.get')
    def test_check_server_health_failure(self, mock_get, fallback_manager):
        """Test failed server health check"""
        mock_get.side_effect = Exception("Connection failed")

        result = fallback_manager.check_server_health()

        assert result == False
        assert fallback_manager.server_available == False

    @patch('requests.post')
    @patch.object(NetworkFallbackManager, 'check_server_health')
    def test_send_to_server_success(self, mock_health, mock_post, fallback_manager):
        """Test successful message send"""
        mock_health.return_value = True
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_post.return_value = mock_response

        message = {"type": "test", "data": "hello"}
        result = fallback_manager.send_to_server(message)

        assert result == {"status": "ok"}
        assert fallback_manager.offline_queue.qsize() == 0

    @patch.object(NetworkFallbackManager, 'check_server_health')
    def test_send_to_server_offline(self, mock_health, fallback_manager):
        """Test message queuing when server offline"""
        mock_health.return_value = False

        message = {"type": "test", "data": "hello"}
        result = fallback_manager.send_to_server(message)

        assert result is None
        assert fallback_manager.offline_queue.qsize() == 1

    def test_has_conflict_no_conflict(self, fallback_manager):
        """Test conflict detection with no conflict"""
        message = {"type": "unknown"}
        result = fallback_manager._has_conflict(message)
        assert result == False

    @patch.object(NetworkFallbackManager, '_get_server_conversation_version')
    def test_has_conflict_conversation_match(self, mock_get_version, fallback_manager):
        """Test conversation conflict when versions match"""
        mock_get_version.return_value = 1

        message = {
            "type": "conversation",
            "conversation_id": "123",
            "version": 1
        }

        result = fallback_manager._has_conflict(message)
        assert result == False

    @patch.object(NetworkFallbackManager, '_get_server_conversation_version')
    def test_has_conflict_conversation_mismatch(self, mock_get_version, fallback_manager):
        """Test conversation conflict when versions differ"""
        mock_get_version.return_value = 2

        message = {
            "type": "conversation",
            "conversation_id": "123",
            "version": 1
        }

        result = fallback_manager._has_conflict(message)
        assert result == True

    @patch('requests.post')
    def test_get_server_conversation_version(self, mock_post, fallback_manager):
        """Test fetching conversation version from server"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "exists": True,
            "version": 5
        }
        mock_post.return_value = mock_response

        version = fallback_manager._get_server_conversation_version("test-id")

        assert version == 5
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_get_server_file_timestamp(self, mock_post, fallback_manager):
        """Test fetching file timestamp from server"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "exists": True,
            "timestamp": "2025-11-14T10:00:00"
        }
        mock_post.return_value = mock_response

        timestamp = fallback_manager._get_server_file_timestamp("test.txt")

        assert timestamp == "2025-11-14T10:00:00"
        mock_post.assert_called_once()

    def test_get_status(self, fallback_manager):
        """Test getting manager status"""
        status = fallback_manager.get_status()

        assert isinstance(status, dict)
        assert 'server_available' in status
        assert 'queue_size' in status
        assert 'sync_in_progress' in status
        assert 'conflicts' in status
