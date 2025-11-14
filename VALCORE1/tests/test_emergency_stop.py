"""
Unit tests for Emergency Stop System
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "01_Client_Brain"))

from core.emergency_stop import EmergencyStop


@pytest.fixture
def emergency_stop(temp_dir, monkeypatch):
    """Create EmergencyStop instance with temp directory"""
    # Change to temp directory
    monkeypatch.chdir(temp_dir)

    # Mock keyboard registration to avoid requiring actual keyboard access
    with patch('keyboard.add_hotkey'):
        stop = EmergencyStop()
        return stop


@pytest.mark.unit
class TestEmergencyStop:
    """Test EmergencyStop class"""

    def test_initialization(self, emergency_stop):
        """Test emergency stop initializes correctly"""
        assert emergency_stop is not None
        assert emergency_stop.enabled == True
        assert emergency_stop.state_dir.exists()

    def test_get_active_room_no_file(self, emergency_stop):
        """Test getting active room when no config exists"""
        room = emergency_stop.get_active_room()
        assert room == "general"  # Default fallback

    def test_get_active_room_with_file(self, emergency_stop, temp_dir):
        """Test getting active room from config file"""
        config_dir = temp_dir / "config"
        config_dir.mkdir(exist_ok=True)

        config = {"active_room": "coding"}
        config_file = config_dir / "room_contexts.json"
        with open(config_file, 'w') as f:
            json.dump(config, f)

        room = emergency_stop.get_active_room()
        assert room == "coding"

    def test_get_command_queue_no_file(self, emergency_stop):
        """Test getting command queue when no state file"""
        queue = emergency_stop.get_command_queue()
        assert queue == []

    def test_get_command_queue_with_file(self, emergency_stop):
        """Test getting command queue from state file"""
        queue_data = {"pending": ["command1", "command2"]}
        queue_file = emergency_stop.state_dir / "command_queue.json"
        with open(queue_file, 'w') as f:
            json.dump(queue_data, f)

        queue = emergency_stop.get_command_queue()
        assert queue == ["command1", "command2"]

    def test_get_mic_state_no_file(self, emergency_stop):
        """Test getting mic state when no state file"""
        state = emergency_stop.get_mic_state()
        assert state == "enabled"  # Default

    def test_get_mic_state_with_file(self, emergency_stop):
        """Test getting mic state from state file"""
        state_data = {"microphone": "disabled"}
        state_file = emergency_stop.state_dir / "voice_state.json"
        with open(state_file, 'w') as f:
            json.dump(state_data, f)

        state = emergency_stop.get_mic_state()
        assert state == "disabled"

    def test_save_checkpoint(self, emergency_stop):
        """Test saving checkpoint"""
        emergency_stop.save_checkpoint("test_reason")

        # Check that checkpoint file was created
        checkpoint_files = list(emergency_stop.state_dir.glob("checkpoint_*.json"))
        assert len(checkpoint_files) >= 1

        # Read the checkpoint and verify contents
        checkpoint_file = checkpoint_files[0]
        with open(checkpoint_file, 'r') as f:
            checkpoint = json.load(f)

        assert checkpoint['reason'] == "test_reason"
        assert 'timestamp' in checkpoint
        assert 'active_room' in checkpoint
        assert 'pending_commands' in checkpoint
        assert 'mic_state' in checkpoint

    @patch('psutil.process_iter')
    def test_kill_all_valcore_processes(self, mock_process_iter, emergency_stop):
        """Test killing VALCORE processes"""
        # Create mock processes
        mock_proc1 = Mock()
        mock_proc1.info = {'pid': 1234, 'name': 'python.exe', 'cmdline': ['python', 'main_client.py']}
        mock_proc1.terminate = Mock()

        mock_proc2 = Mock()
        mock_proc2.info = {'pid': 5678, 'name': 'python.exe', 'cmdline': ['python', 'main_server.py']}
        mock_proc2.terminate = Mock()

        mock_proc3 = Mock()
        mock_proc3.info = {'pid': 9999, 'name': 'notepad.exe', 'cmdline': ['notepad.exe']}

        mock_process_iter.return_value = [mock_proc1, mock_proc2, mock_proc3]

        killed = emergency_stop.kill_all_valcore_processes()

        # Should kill 2 VALCORE processes
        assert len(killed) == 2
        mock_proc1.terminate.assert_called_once()
        mock_proc2.terminate.assert_called_once()

    @patch('psutil.process_iter')
    def test_trigger_shutdown(self, mock_process_iter, emergency_stop):
        """Test emergency shutdown trigger"""
        mock_proc = Mock()
        mock_proc.info = {'pid': 1234, 'name': 'python.exe', 'cmdline': ['python', 'main_client.py']}
        mock_proc.terminate = Mock()
        mock_process_iter.return_value = [mock_proc]

        emergency_stop.trigger_shutdown()

        # Should save checkpoint and kill processes
        checkpoint_files = list(emergency_stop.state_dir.glob("checkpoint_*.json"))
        assert len(checkpoint_files) >= 1

        mock_proc.terminate.assert_called_once()

    def test_restore_from_checkpoint(self, emergency_stop):
        """Test restoring from checkpoint"""
        # Create a checkpoint first
        emergency_stop.save_checkpoint("test")

        checkpoint_files = list(emergency_stop.state_dir.glob("checkpoint_*.json"))
        checkpoint_file = checkpoint_files[0]

        restored = emergency_stop.restore_from_checkpoint(str(checkpoint_file))

        assert restored is not None
        assert isinstance(restored, dict)
        assert 'reason' in restored
        assert 'active_room' in restored
