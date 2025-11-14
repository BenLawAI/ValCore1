"""
Pytest configuration and fixtures
"""

import pytest
import sys
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "01_Client_Brain"))
sys.path.insert(0, str(Path(__file__).parent.parent / "02_Server_Brain"))
sys.path.insert(0, str(Path(__file__).parent.parent / "03_Shared"))


@pytest.fixture(scope="session")
def test_data_dir(tmp_path_factory):
    """Create temporary directory for test data"""
    return tmp_path_factory.mktemp("test_data")


@pytest.fixture
def sample_config():
    """Sample configuration for testing"""
    return {
        "model": "test_model",
        "temperature": 0.7,
        "max_tokens": 2000,
        "timeout": 30
    }
