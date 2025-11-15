"""
Unit tests for EmergencyStop
Tests panic hotkey, state preservation, and process killing
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
from pathlib import Path
from datetime import datetime


class TestEmergencyStopBasic(unittest.TestCase):
    """Test basic emergency stop functionality"""

    @patch('sys.path')
    @patch('VALCORE1.01_Client_Brain.core.emergency_stop.keyboard')
    def test_initialization(self, mock_keyboard, mock_syspath):
        """Test EmergencyStop initializes correctly"""
        import sys
        sys.path.insert(0, '/home/user/ValCore1/VALCORE1')
        from VALCORE1.01_Client_Brain.core.emergency_stop import EmergencyStop

        es = EmergencyStop()

        self.assertTrue(es.enabled)
        self.assertTrue(es.state_dir.exists())
        mock_keyboard.add_hotkey.assert_called_once()

    @patch('sys.path')
    @patch('VALCORE1.01_Client_Brain.core.emergency_stop.keyboard')
    def test_initialization_with_voice_system(self, mock_keyboard, mock_syspath):
        """Test initialization with voice system reference"""
        import sys
        sys.path.insert(0, '/home/user/ValCore1/VALCORE1')
        from VALCORE1.01_Client_Brain.core.emergency_stop import EmergencyStop

        # Mock voice system
        mock_voice_system = Mock()
        mock_voice_system.microphone_enabled = True

        es = EmergencyStop(voice_system=mock_voice_system)

        self.assertEqual(es.voice_system, mock_voice_system)

    @patch('sys.path')
    @patch('VALCORE1.01_Client_Brain.core.emergency_stop.keyboard')
    def test_get_mic_state_with_voice_system(self, mock_keyboard, mock_syspath):
        """Test getting microphone state from voice system"""
        import sys
        sys.path.insert(0, '/home/user/ValCore1/VALCORE1')
        from VALCORE1.01_Client_Brain.core.emergency_stop import EmergencyStop

        # Test with enabled microphone
        mock_voice_system = Mock()
        mock_voice_system.microphone_enabled = True

        es = EmergencyStop(voice_system=mock_voice_system)
        state = es.get_mic_state()

        self.assertEqual(state, "enabled")

        # Test with disabled microphone
        mock_voice_system.microphone_enabled = False
        state = es.get_mic_state()

        self.assertEqual(state, "disabled")

    @patch('sys.path')
    @patch('VALCORE1.01_Client_Brain.core.emergency_stop.keyboard')
    def test_get_mic_state_without_voice_system(self, mock_keyboard, mock_syspath):
        """Test getting microphone state without voice system"""
        import sys
        sys.path.insert(0, '/home/user/ValCore1/VALCORE1')
        from VALCORE1.01_Client_Brain.core.emergency_stop import EmergencyStop

        es = EmergencyStop(voice_system=None)
        state = es.get_mic_state()

        self.assertEqual(state, "unknown")


class TestEmergencyStopCheckpoint(unittest.TestCase):
    """Test checkpoint save/restore functionality"""

    def setUp(self):
        """Set up test fixtures"""
        # Create test state directory
        self.state_dir = Path(".test_state")
        self.state_dir.mkdir(exist_ok=True)

    def tearDown(self):
        """Clean up test artifacts"""
        # Clean up test state directory
        if self.state_dir.exists():
            for file in self.state_dir.glob("*.json"):
                file.unlink()
            self.state_dir.rmdir()

    @patch('sys.path')
    @patch('VALCORE1.01_Client_Brain.core.emergency_stop.keyboard')
    def test_save_checkpoint(self, mock_keyboard, mock_syspath):
        """Test checkpoint save functionality"""
        import sys
        sys.path.insert(0, '/home/user/ValCore1/VALCORE1')
        from VALCORE1.01_Client_Brain.core.emergency_stop import EmergencyStop

        es = EmergencyStop()
        es.state_dir = self.state_dir

        es.save_checkpoint("test_reason")

        # Check checkpoint was created
        checkpoints = list(self.state_dir.glob("checkpoint_*.json"))
        self.assertEqual(len(checkpoints), 1)

        # Verify checkpoint contents
        with open(checkpoints[0], 'r') as f:
            data = json.load(f)

        self.assertEqual(data['reason'], "test_reason")
        self.assertIn('timestamp', data)
        self.assertIn('active_room', data)
        self.assertIn('pending_commands', data)
        self.assertIn('mic_state', data)

    @patch('sys.path')
    def test_find_latest_checkpoint(self, mock_syspath):
        """Test finding latest checkpoint"""
        import sys
        sys.path.insert(0, '/home/user/ValCore1/VALCORE1')
        from VALCORE1.01_Client_Brain.core.emergency_stop import find_latest_checkpoint

        # Create multiple checkpoints
        import time
        for i in range(3):
            checkpoint = self.state_dir / f"checkpoint_test{i}.json"
            with open(checkpoint, 'w') as f:
                json.dump({"timestamp": datetime.now().isoformat()}, f)
            time.sleep(0.01)  # Ensure different mtimes

        # Temporarily change state_dir in module
        with patch('VALCORE1.01_Client_Brain.core.emergency_stop.Path') as mock_path:
            mock_path.return_value = self.state_dir
            latest = find_latest_checkpoint()

        self.assertIsNotNone(latest)
        self.assertTrue(latest.name.startswith("checkpoint_"))

    @patch('sys.path')
    def test_recover_from_checkpoint(self, mock_syspath):
        """Test checkpoint recovery"""
        import sys
        sys.path.insert(0, '/home/user/ValCore1/VALCORE1')
        from VALCORE1.01_Client_Brain.core.emergency_stop import recover_from_checkpoint

        # Create test checkpoint
        checkpoint_file = self.state_dir / "checkpoint_test.json"
        checkpoint_data = {
            "timestamp": "2025-01-01T10:00:00",
            "reason": "test",
            "active_room": "general",
            "pending_commands": [],
            "mic_state": "enabled"
        }

        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint_data, f)

        # Recover checkpoint
        recovered = recover_from_checkpoint(checkpoint_file)

        self.assertEqual(recovered['reason'], "test")
        self.assertEqual(recovered['active_room'], "general")


class TestEmergencyStopProcessKilling(unittest.TestCase):
    """Test process killing functionality"""

    @patch('sys.path')
    @patch('VALCORE1.01_Client_Brain.core.emergency_stop.keyboard')
    @patch('VALCORE1.01_Client_Brain.core.emergency_stop.psutil')
    def test_kill_valcore_processes(self, mock_psutil, mock_keyboard, mock_syspath):
        """Test killing VALCORE1 processes"""
        import sys
        sys.path.insert(0, '/home/user/ValCore1/VALCORE1')
        from VALCORE1.01_Client_Brain.core.emergency_stop import EmergencyStop

        # Mock processes
        mock_proc1 = Mock()
        mock_proc1.info = {'name': 'python.exe', 'cmdline': ['python', 'valcore1/main_client.py']}

        mock_proc2 = Mock()
        mock_proc2.info = {'name': 'chrome.exe', 'cmdline': ['chrome.exe']}

        mock_psutil.process_iter.return_value = [mock_proc1, mock_proc2]

        es = EmergencyStop()
        killed = es.kill_all_valcore_processes()

        # Should only kill VALCORE1 process
        self.assertEqual(len(killed), 1)
        mock_proc1.kill.assert_called_once()
        mock_proc2.kill.assert_not_called()


if __name__ == '__main__':
    unittest.main()
