"""
Pytest configuration and fixtures for VALCORE1 tests.
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, MagicMock


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_config():
    """Mock configuration dictionary"""
    return {
        "stt": {
            "model": "base",
            "device": "cpu",
            "compute_type": "int8"
        },
        "tts": {
            "voice": "en_US-lessac-medium",
            "sample_rate": 22050
        },
        "wake_word": {
            "enabled": False
        },
        "audio": {
            "sample_rate": 16000,
            "chunk_size": 1024,
            "channels": 1,
            "use_default_device": True
        },
        "speaker_verification": {
            "enabled": False
        }
    }


@pytest.fixture
def mock_voice_config_file(temp_dir, mock_config):
    """Create a mock voice configuration file"""
    config_file = temp_dir / "voice_config.json"
    with open(config_file, 'w') as f:
        json.dump(mock_config, f)
    return config_file


@pytest.fixture
def mock_network_config():
    """Mock network configuration"""
    return {
        "atom_local_ip": "192.168.1.100",
        "atom_tailscale_ip": "100.64.0.1",
        "atom_port": 5000,
        "prefer_tailscale": False,
        "connection_timeout": 30
    }


@pytest.fixture
def mock_librarian():
    """Mock Librarian instance"""
    librarian = Mock()
    librarian.search = Mock(return_value=[])
    librarian.add_conversation = Mock(return_value=True)
    librarian.library_path = "library"
    return librarian


@pytest.fixture
def mock_llm():
    """Mock LLM instance"""
    llm = Mock()
    llm.generate = Mock(return_value="This is a test response")
    llm.default_model = "llama3.2:3b"
    return llm


@pytest.fixture
def mock_room_manager():
    """Mock RoomManager instance"""
    room_manager = Mock()
    room_manager.get_room_config = Mock(return_value={
        "system_prompt": "You are a helpful assistant",
        "llm_temperature": 0.7,
        "max_tokens": 2000
    })
    room_manager.get_room_context = Mock(return_value="Previous context")
    room_manager.list_rooms = Mock(return_value=["general", "coding", "research"])
    room_manager.switch_room = Mock(return_value=True)
    return room_manager
