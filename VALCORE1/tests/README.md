# VALCORE1 Test Suite

## Running Tests

### Run all tests
```bash
cd /home/user/ValCore1/VALCORE1
pytest tests/
```

### Run specific test file
```bash
pytest tests/test_client_bridge.py
```

### Run with coverage
```bash
pytest --cov=. --cov-report=html tests/
```

### Run only unit tests
```bash
pytest -m unit tests/
```

## Test Structure

- `test_client_bridge.py` - Tests for Flask API endpoints
- `test_exceptions.py` - Tests for custom exception types
- `conftest.py` - Shared fixtures and configuration
- `pytest.ini` - Pytest configuration

## Writing Tests

Use pytest fixtures for common test objects:

```python
def test_example(client, mock_llm):
    # Test code here
    pass
```

## Test Coverage

Run coverage reports to ensure comprehensive testing:

```bash
pytest --cov=core --cov-report=term-missing tests/
```
