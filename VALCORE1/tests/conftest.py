"""
Shared pytest fixtures and configuration for VALCORE1 tests
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
import pytest
import logging

# Add project paths to sys.path
PROJECT_ROOT = Path(__file__).parent.parent
CLIENT_PATH = PROJECT_ROOT / "01_Client_Brain"
SERVER_PATH = PROJECT_ROOT / "02_Server_Brain"

sys.path.insert(0, str(CLIENT_PATH))
sys.path.insert(0, str(SERVER_PATH))

# Configure logging for tests
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


@pytest.fixture
def temp_dir():
    """
    Create a temporary directory for test files

    Yields:
        Path: Temporary directory path

    Cleanup:
        Removes directory after test completes
    """
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def temp_library_dir(temp_dir):
    """
    Create a temporary Library directory for testing

    Args:
        temp_dir: Temporary directory fixture

    Returns:
        Path: Temporary library directory
    """
    library_path = temp_dir / "Library"
    library_path.mkdir(parents=True, exist_ok=True)
    return library_path


@pytest.fixture
def temp_backup_dir(temp_dir):
    """
    Create a temporary Backup directory for testing

    Args:
        temp_dir: Temporary directory fixture

    Returns:
        Path: Temporary backup directory
    """
    backup_path = temp_dir / "Backups"
    backup_path.mkdir(parents=True, exist_ok=True)
    return backup_path


@pytest.fixture
def sample_faiss_data(temp_library_dir):
    """
    Create sample FAISS index data for testing

    Args:
        temp_library_dir: Temporary library directory

    Returns:
        dict: Sample metadata entries
    """
    import json

    # Create sample metadata
    metadata = [
        {
            "room": "general",
            "text": "Hello, how are you?",
            "timestamp": "2025-01-14T12:00:00",
            "metadata": {"response": "I'm doing well, thank you!"}
        },
        {
            "room": "truck",
            "text": "What's the status of truck 42?",
            "timestamp": "2025-01-14T12:05:00",
            "metadata": {"response": "Truck 42 is en route."}
        }
    ]

    # Save to temporary library
    metadata_file = temp_library_dir / "metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)

    return metadata


@pytest.fixture
def mock_env_vars(monkeypatch):
    """
    Set up mock environment variables for testing

    Args:
        monkeypatch: Pytest monkeypatch fixture

    Returns:
        dict: Dictionary of set environment variables
    """
    env_vars = {
        'VALCORE_API_KEY': 'test-api-key-12345',
        'PICOVOICE_ACCESS_KEY': 'test-picovoice-key',
        'MAX_BACKUPS': '3',
        'BACKUP_INTERVAL_HOURS': '1',
        'BACKUP_ON_STARTUP': 'false'
    }

    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)

    return env_vars


@pytest.fixture
def mock_llm_response():
    """
    Mock LLM response for testing

    Returns:
        str: Sample LLM response
    """
    return "This is a test response from the LLM."


@pytest.fixture
def sample_audio_data():
    """
    Generate sample audio data for voice system testing

    Returns:
        numpy.ndarray: Sample audio array (16kHz, 1 second)
    """
    try:
        import numpy as np
        # Generate 1 second of silence at 16kHz
        sample_rate = 16000
        duration = 1.0
        samples = int(sample_rate * duration)
        audio = np.zeros(samples, dtype=np.float32)
        return audio
    except ImportError:
        pytest.skip("NumPy not available for audio testing")


@pytest.fixture
def flask_test_client():
    """
    Create a Flask test client for API testing

    Returns:
        FlaskClient: Flask test client
    """
    # This will be implemented in server tests
    pytest.skip("Flask test client requires full server setup")


@pytest.fixture(scope="session")
def check_gpu_available():
    """
    Check if GPU is available for testing

    Returns:
        bool: True if GPU is available
    """
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


@pytest.fixture
def room_config():
    """
    Sample room configuration for testing

    Returns:
        dict: Room configuration dictionary
    """
    return {
        "rooms": {
            "general": {
                "system_prompt": "You are VAL, a helpful assistant.",
                "llm_temperature": 0.7,
                "max_tokens": 2000
            },
            "truck": {
                "system_prompt": "You are VAL, a truck logistics assistant.",
                "llm_temperature": 0.5,
                "max_tokens": 1500
            }
        },
        "active_room": "general"
    }


# Pytest hooks for custom behavior

def pytest_configure(config):
    """Called after command line options have been parsed"""
    # Add custom markers
    config.addinivalue_line(
        "markers", "unit: Unit tests (fast, isolated)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (slower, may require resources)"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test location"""
    for item in items:
        # Add markers based on test file location
        if "server" in str(item.fspath):
            item.add_marker(pytest.mark.server)
        if "client" in str(item.fspath):
            item.add_marker(pytest.mark.client)
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        else:
            item.add_marker(pytest.mark.unit)
