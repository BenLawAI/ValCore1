# VALCORE1 Test Suite

Comprehensive unit and integration tests for VALCORE1 voice assistant system.

## Overview

The test suite covers:
- **Server Components**: BackupManager, Librarian, ClientBridge (Flask API), LLM Interface
- **Client Components**: Voice System, Automation, Server Bridge
- **Integration Tests**: End-to-end workflows
- **Security Tests**: Command injection, authentication, input validation

## Test Structure

```
tests/
├── __init__.py
├── conftest.py                    # Shared fixtures and configuration
├── pytest.ini                      # Pytest configuration
├── README.md                       # This file
├── client/                         # Client-side tests
│   ├── __init__.py
│   └── test_automation.py         # Automation & security tests
├── server/                         # Server-side tests
│   ├── __init__.py
│   ├── test_backup_manager.py     # Backup system tests
│   ├── test_client_bridge.py      # Flask API tests
│   └── test_librarian.py          # FAISS search tests
├── shared/                         # Shared component tests
│   └── __init__.py
└── integration/                    # Integration tests
    └── __init__.py
```

## Installation

### Install Test Dependencies

```bash
# Install pytest and related packages
pip install pytest pytest-cov pytest-mock pytest-timeout pytest-xdist

# Or install from requirements
pip install -r requirements.txt
```

### Required Dependencies

The test suite requires:
- `pytest` >= 7.0.0 - Test framework
- `pytest-cov` >= 4.0.0 - Coverage reporting
- `pytest-mock` >= 3.10.0 - Mocking support
- `pytest-timeout` >= 2.1.0 - Test timeouts
- `pytest-xdist` >= 3.0.0 - Parallel execution (optional)

## Running Tests

### Run All Tests

```bash
# From VALCORE1 directory
cd /home/user/ValCore1/VALCORE1
pytest

# Or with more verbose output
pytest -v

# With coverage report
pytest --cov=. --cov-report=html --cov-report=term
```

### Run Specific Test Categories

```bash
# Run only unit tests (fast)
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only server tests
pytest -m server

# Run only client tests
pytest -m client

# Run slow tests separately
pytest -m slow
```

### Run Specific Test Files

```bash
# Run backup manager tests
pytest tests/server/test_backup_manager.py

# Run API tests
pytest tests/server/test_client_bridge.py

# Run security tests
pytest tests/client/test_automation.py

# Run specific test class
pytest tests/server/test_backup_manager.py::TestBackupManager

# Run specific test method
pytest tests/server/test_backup_manager.py::TestBackupManager::test_create_backup
```

### Run with Coverage

```bash
# Generate HTML coverage report
pytest --cov=VALCORE1 --cov-report=html --cov-report=term-missing

# View coverage report
# Open htmlcov/index.html in browser

# Coverage for specific module
pytest tests/server/test_backup_manager.py --cov=VALCORE1/02_Server_Brain/core/backup_manager --cov-report=term
```

### Parallel Execution

```bash
# Run tests in parallel (requires pytest-xdist)
pytest -n auto

# Run with specific number of workers
pytest -n 4
```

### Debug Mode

```bash
# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Drop into debugger on failure
pytest --pdb

# Show local variables on failure
pytest -l
```

## Test Markers

Tests are marked for easy categorization and selective execution:

- `@pytest.mark.unit` - Fast, isolated unit tests
- `@pytest.mark.integration` - Slower integration tests
- `@pytest.mark.server` - Server-side tests
- `@pytest.mark.client` - Client-side tests
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.gpu` - Tests requiring GPU
- `@pytest.mark.network` - Tests requiring network access
- `@pytest.mark.voice` - Tests requiring voice/audio hardware

### Skip Tests Requiring Hardware

```bash
# Skip GPU tests
pytest -m "not gpu"

# Skip GPU and network tests
pytest -m "not gpu and not network"

# Skip voice hardware tests
pytest -m "not voice"
```

## Test Fixtures

Common fixtures available in `conftest.py`:

- `temp_dir` - Temporary directory (auto-cleaned)
- `temp_library_dir` - Temporary Library directory
- `temp_backup_dir` - Temporary Backup directory
- `sample_faiss_data` - Sample FAISS metadata
- `mock_env_vars` - Mock environment variables
- `mock_llm_response` - Mock LLM response
- `sample_audio_data` - Sample audio array
- `room_config` - Sample room configuration

## Writing Tests

### Basic Test Structure

```python
import pytest

@pytest.mark.unit
class TestMyComponent:
    """Test suite for MyComponent"""

    @pytest.fixture
    def component(self):
        """Create component instance"""
        return MyComponent()

    def test_basic_functionality(self, component):
        """Test basic functionality"""
        result = component.do_something()
        assert result is True
```

### Using Fixtures

```python
def test_with_fixtures(temp_dir, mock_env_vars):
    """Test using shared fixtures"""
    # temp_dir is a Path object
    test_file = temp_dir / "test.txt"
    test_file.write_text("Hello")

    # mock_env_vars already set up
    api_key = os.getenv('VALCORE_API_KEY')
    assert api_key == 'test-api-key-12345'
```

### Mocking External Dependencies

```python
from unittest.mock import Mock, patch

def test_with_mock():
    """Test with mocked dependencies"""
    with patch('subprocess.Popen') as mock_popen:
        mock_popen.return_value = Mock()

        result = launch_application('app.exe')

        mock_popen.assert_called_once()
```

## Continuous Integration

Tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pytest -v --cov=. --cov-report=xml --cov-report=term

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

## Test Coverage Goals

Target coverage levels:
- **Overall**: 80%+ coverage
- **Core modules**: 90%+ coverage
- **Security-critical code**: 100% coverage
  - `automation.py` (command injection prevention)
  - `client_bridge.py` (authentication, input validation)
  - `backup_manager.py` (data protection)

### Check Coverage

```bash
# Overall coverage
pytest --cov=. --cov-report=term-missing

# Module-specific coverage
pytest --cov=VALCORE1/02_Server_Brain/core/backup_manager --cov-report=term-missing
```

## Known Issues & Limitations

### GPU Tests
- GPU tests (`@pytest.mark.gpu`) require NVIDIA GPU with CUDA
- Skip with: `pytest -m "not gpu"`

### Voice Tests
- Voice tests require audio hardware and drivers
- Skip with: `pytest -m "not voice"`

### Network Tests
- Network tests may fail in isolated environments
- Skip with: `pytest -m "not network"`

### Platform-Specific Tests
- Some tests are Windows-specific (automation, voice)
- Linux/macOS tests may be skipped automatically

## Troubleshooting

### Import Errors

```bash
# If import errors occur, ensure PYTHONPATH is set
export PYTHONPATH=/home/user/ValCore1/VALCORE1:$PYTHONPATH
pytest
```

### Missing Dependencies

```bash
# Install missing test dependencies
pip install pytest pytest-cov pytest-mock

# Install component dependencies
pip install -r VALCORE1/01_Client_Brain/setup/requirements_client.txt
pip install -r VALCORE1/02_Server_Brain/setup/requirements_server.txt
```

### Fixture Errors

```bash
# Clear pytest cache
pytest --cache-clear

# Verify fixtures are available
pytest --fixtures
```

### Slow Tests

```bash
# Run fast tests only
pytest -m "unit and not slow"

# Set timeout for slow tests
pytest --timeout=300
```

## Best Practices

1. **Keep tests fast**: Unit tests should run in milliseconds
2. **Mock external dependencies**: Database, network, filesystem
3. **Use descriptive names**: Test names should explain what they test
4. **One assertion per test**: Makes failures easier to debug
5. **Arrange-Act-Assert**: Structure tests clearly
6. **Clean up resources**: Use fixtures with teardown
7. **Test edge cases**: Empty input, null values, large data
8. **Test error handling**: Verify exceptions are raised correctly
9. **Avoid test interdependence**: Each test should run independently
10. **Document complex tests**: Add docstrings explaining test purpose

## Contributing Tests

When adding new tests:

1. Place tests in appropriate directory (`client/`, `server/`, `integration/`)
2. Add appropriate markers (`@pytest.mark.unit`, etc.)
3. Use shared fixtures from `conftest.py` when possible
4. Follow naming convention: `test_*.py`, `test_*()`, `Test*`
5. Add docstrings explaining test purpose
6. Ensure tests pass locally before committing
7. Check coverage for new code: `pytest --cov=path/to/new/code`

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Python Testing Best Practices](https://docs.python-guide.org/writing/tests/)

## Support

For test-related issues:
1. Check test logs: `pytest -v --tb=long`
2. Review this documentation
3. Check fixture availability: `pytest --fixtures`
4. Verify dependencies: `pip list | grep pytest`
