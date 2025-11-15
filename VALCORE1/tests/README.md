# VALCORE1 Test Suite

Comprehensive test suite for all VALCORE1 components.

## Directory Structure

```
tests/
├── unit/                      # Unit tests for individual modules
│   ├── test_voice_system.py  # Voice system tests (TTS, STT, etc.)
│   ├── test_network_fallback.py  # Network fallback tests
│   └── test_emergency_stop.py    # Emergency stop tests
├── integration/               # Integration tests
│   └── test_voice_to_server.py   # End-to-end workflow tests
├── fixtures/                  # Test fixtures and mock data
├── run_tests.py              # Test runner script
├── pytest.ini                # Pytest configuration
└── README.md                 # This file
```

## Running Tests

### Run All Tests
```bash
python tests/run_tests.py
```

### Run Only Unit Tests
```bash
python tests/run_tests.py --unit
```

### Run Only Integration Tests
```bash
python tests/run_tests.py --integration
```

### Quiet Mode
```bash
python tests/run_tests.py --quiet
```

### Using Pytest (if installed)
```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/

# Specific test file
pytest tests/unit/test_voice_system.py

# Specific test
pytest tests/unit/test_voice_system.py::TestVoiceSystemTTS::test_tts_initialization_pyttsx3

# With coverage
pytest --cov=VALCORE1 --cov-report=html
```

## Test Categories

### Unit Tests
- **test_voice_system.py**: Tests for voice system components
  - TTS initialization and speak() method
  - STT transcription
  - Wake word detection
  - Speaker verification

- **test_network_fallback.py**: Tests for network fallback
  - Offline queueing
  - Conflict detection
  - Conflict resolution (keep_local, keep_server, merge)
  - Server health checking

- **test_emergency_stop.py**: Tests for emergency stop
  - Hotkey registration
  - Checkpoint save/restore
  - Process killing
  - State preservation

### Integration Tests
- **test_voice_to_server.py**: End-to-end workflow tests
  - Voice → Server → Response pipeline
  - Offline fallback integration
  - Room switching
  - Memory/Librarian integration

## Test Coverage

Current test coverage:
- ✅ Voice System TTS: Initialization, speak() method
- ✅ Network Fallback: Queue, conflict detection, resolution
- ✅ Emergency Stop: Checkpoints, process killing, voice system integration
- ⚠️ Integration tests: Basic structure (needs expansion)

## Requirements

Core testing libraries:
```bash
pip install pytest pytest-cov pytest-timeout pytest-mock
```

Optional for mocking:
```bash
pip install responses mock
```

## Writing New Tests

### Unit Test Template
```python
import unittest
from unittest.mock import Mock, patch

class TestNewComponent(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        pass

    def tearDown(self):
        """Clean up after tests"""
        pass

    def test_feature(self):
        """Test specific feature"""
        # Arrange
        # Act
        # Assert
        pass
```

### Integration Test Template
```python
import unittest
from pathlib import Path

class TestNewIntegration(unittest.TestCase):
    def test_workflow(self):
        """Test complete workflow"""
        # Setup
        # Execute workflow
        # Verify results
        pass
```

## Test Markers

Use pytest markers to categorize tests:

```python
import pytest

@pytest.mark.slow
def test_slow_operation():
    """This test takes a while"""
    pass

@pytest.mark.requires_gpu
def test_gpu_operation():
    """This test requires CUDA"""
    pass
```

## CI/CD Integration

For continuous integration, run:

```bash
# Fast tests only (skip slow/GPU/network tests)
pytest -m "not slow and not requires_gpu and not requires_network"

# Generate XML report for CI
pytest --junitxml=test-results.xml
```

## Troubleshooting

### Import Errors
Ensure VALCORE1 is in Python path:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

### Mock Issues
Use `unittest.mock` for mocking external dependencies:
```python
from unittest.mock import patch, Mock

@patch('module.dependency')
def test_with_mock(mock_dep):
    mock_dep.return_value = "mocked"
    # test code
```

### Fixture Path Issues
Use absolute paths for test fixtures:
```python
from pathlib import Path
test_dir = Path(__file__).parent
fixture = test_dir / 'fixtures' / 'test_data.json'
```

## Coverage Goals

- **Critical Components**: >80% coverage
  - Voice System
  - Network Fallback
  - Emergency Stop

- **Server Components**: >70% coverage
  - LLM Interface
  - Librarian
  - Memory Compression

- **Overall Project**: >60% coverage

## Contributing

When adding new features:
1. Write unit tests first (TDD)
2. Ensure all tests pass before committing
3. Add integration tests for workflows
4. Update this README if adding new test categories

---

**Last Updated**: 2025-11-15
**Test Framework**: unittest + pytest
**Python Version**: 3.10+
