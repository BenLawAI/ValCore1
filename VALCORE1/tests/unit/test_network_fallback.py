"""
Unit tests for NetworkFallbackManager
Tests offline queue, conflict detection, and resolution
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import queue
from pathlib import Path
from datetime import datetime


class TestNetworkFallbackBasic(unittest.TestCase):
    """Test basic network fallback functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_config = {
            "atom_local_ip": "192.168.1.121",
            "atom_port": 5000,
            "atom_tailscale_ip": "",
            "prefer_tailscale": False,
            "connection_timeout": 10
        }

        # Create temporary config file
        self.config_file = Path("test_network_config.json")
        with open(self.config_file, 'w') as f:
            json.dump(self.test_config, f)

    def tearDown(self):
        """Clean up test artifacts"""
        if self.config_file.exists():
            self.config_file.unlink()

        # Clean up test logs
        log_file = Path("logs/conflict_log.json")
        if log_file.exists():
            log_file.unlink()

    @patch('sys.path')
    def test_initialization(self, mock_syspath):
        """Test NetworkFallbackManager initializes correctly"""
        import sys
        sys.path.insert(0, '/home/user/ValCore1/VALCORE1')
        from VALCORE1.01_Client_Brain.core.network_fallback import NetworkFallbackManager

        nfm = NetworkFallbackManager(config_path=str(self.config_file))

        self.assertFalse(nfm.server_available)
        self.assertFalse(nfm.sync_in_progress)
        self.assertIsInstance(nfm.offline_queue, queue.Queue)
        self.assertEqual(nfm.conflict_log, [])

    @patch('sys.path')
    def test_get_server_url(self, mock_syspath):
        """Test server URL construction"""
        import sys
        sys.path.insert(0, '/home/user/ValCore1/VALCORE1')
        from VALCORE1.01_Client_Brain.core.network_fallback import NetworkFallbackManager

        nfm = NetworkFallbackManager(config_path=str(self.config_file))
        url = nfm.get_server_url()

        self.assertEqual(url, "http://192.168.1.121:5000")

    @patch('sys.path')
    @patch('VALCORE1.01_Client_Brain.core.network_fallback.requests')
    def test_offline_queueing(self, mock_requests, mock_syspath):
        """Test messages are queued when server is offline"""
        import sys
        sys.path.insert(0, '/home/user/ValCore1/VALCORE1')
        from VALCORE1.01_Client_Brain.core.network_fallback import NetworkFallbackManager

        # Mock server as unavailable
        mock_requests.get.side_effect = Exception("Connection refused")

        nfm = NetworkFallbackManager(config_path=str(self.config_file))

        # Send message while offline
        message = {"type": "conversation", "content": "test"}
        result = nfm.send_to_server(message)

        self.assertIsNone(result)
        self.assertFalse(nfm.server_available)
        self.assertEqual(nfm.offline_queue.qsize(), 1)


class TestNetworkFallbackConflictDetection(unittest.TestCase):
    """Test conflict detection logic"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_config = {
            "atom_local_ip": "192.168.1.121",
            "atom_port": 5000,
            "atom_tailscale_ip": "",
            "prefer_tailscale": False,
            "connection_timeout": 10
        }

        self.config_file = Path("test_network_config.json")
        with open(self.config_file, 'w') as f:
            json.dump(self.test_config, f)

    def tearDown(self):
        """Clean up"""
        if self.config_file.exists():
            self.config_file.unlink()

    @patch('sys.path')
    @patch('VALCORE1.01_Client_Brain.core.network_fallback.requests')
    def test_conversation_conflict_detection(self, mock_requests, mock_syspath):
        """Test conversation version conflict detection"""
        import sys
        sys.path.insert(0, '/home/user/ValCore1/VALCORE1')
        from VALCORE1.01_Client_Brain.core.network_fallback import NetworkFallbackManager

        nfm = NetworkFallbackManager(config_path=str(self.config_file))

        # Mock server response with different version
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"version": 5}
        mock_requests.get.return_value = mock_response

        message = {
            "type": "conversation",
            "conversation_id": "test123",
            "version": 3
        }

        has_conflict = nfm._has_conflict(message)

        self.assertTrue(has_conflict)

    @patch('sys.path')
    @patch('VALCORE1.01_Client_Brain.core.network_fallback.requests')
    def test_no_conflict_when_versions_match(self, mock_requests, mock_syspath):
        """Test no conflict when versions match"""
        import sys
        sys.path.insert(0, '/home/user/ValCore1/VALCORE1')
        from VALCORE1.01_Client_Brain.core.network_fallback import NetworkFallbackManager

        nfm = NetworkFallbackManager(config_path=str(self.config_file))

        # Mock server response with same version
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"version": 3}
        mock_requests.get.return_value = mock_response

        message = {
            "type": "conversation",
            "conversation_id": "test123",
            "version": 3
        }

        has_conflict = nfm._has_conflict(message)

        self.assertFalse(has_conflict)


class TestNetworkFallbackConflictResolution(unittest.TestCase):
    """Test conflict resolution logic"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_config = {
            "atom_local_ip": "192.168.1.121",
            "atom_port": 5000,
            "atom_tailscale_ip": "",
            "prefer_tailscale": False,
            "connection_timeout": 10
        }

        self.config_file = Path("test_network_config.json")
        with open(self.config_file, 'w') as f:
            json.dump(self.test_config, f)

    def tearDown(self):
        """Clean up"""
        if self.config_file.exists():
            self.config_file.unlink()

    @patch('sys.path')
    @patch('VALCORE1.01_Client_Brain.core.network_fallback.requests')
    def test_resolve_conflict_keep_local(self, mock_requests, mock_syspath):
        """Test conflict resolution: keep local"""
        import sys
        sys.path.insert(0, '/home/user/ValCore1/VALCORE1')
        from VALCORE1.01_Client_Brain.core.network_fallback import NetworkFallbackManager

        nfm = NetworkFallbackManager(config_path=str(self.config_file))

        # Mock successful server communication
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_requests.post.return_value = mock_response
        mock_requests.get.return_value = mock_response

        conflict = {
            "message": {
                "type": "conversation",
                "conversation_id": "test123",
                "version": 3
            }
        }

        result = nfm.resolve_conflict(conflict, resolution="keep_local")

        self.assertTrue(result)

    @patch('sys.path')
    @patch('VALCORE1.01_Client_Brain.core.network_fallback.requests')
    def test_merge_conversations(self, mock_requests, mock_syspath):
        """Test conversation merge logic"""
        import sys
        sys.path.insert(0, '/home/user/ValCore1/VALCORE1')
        from VALCORE1.01_Client_Brain.core.network_fallback import NetworkFallbackManager

        nfm = NetworkFallbackManager(config_path=str(self.config_file))

        # Mock server conversation data
        server_data = {
            "type": "conversation",
            "conversation_id": "test123",
            "version": 3,
            "messages": [
                {"timestamp": "2025-01-01T10:00:00", "content": "server message 1"},
                {"timestamp": "2025-01-01T10:01:00", "content": "server message 2"}
            ]
        }

        local_message = {
            "type": "conversation",
            "conversation_id": "test123",
            "version": 3,
            "messages": [
                {"timestamp": "2025-01-01T10:00:00", "content": "server message 1"},
                {"timestamp": "2025-01-01T10:02:00", "content": "local message"}
            ]
        }

        # Mock fetch from server
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = server_data

        # Mock send to server
        mock_post_response = Mock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = {"success": True}

        mock_requests.get.return_value = mock_get_response
        mock_requests.post.return_value = mock_post_response

        result = nfm._merge_changes(local_message)

        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
