# Testing Guide

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/test_config.py
pytest tests/test_agent_runner.py
pytest tests/test_engine.py
pytest tests/test_integration.py
```

### Run API Test Script

```bash
# Make sure engine is running with API first: python run_with_api.py
python tests/test_api.py
```

### Run with Verbose Output

```bash
pytest -v
```

### Run with Coverage

```bash
pytest --cov=engine --cov-report=html
```

### Run Specific Test

```bash
pytest tests/test_config.py::test_load_config_success
```

## Test Structure

```
tests/
├── __init__.py          # Test package
├── conftest.py          # Pytest fixtures and configuration
├── test_config.py       # Configuration loading tests
├── test_agent_runner.py # Agent runner tests
├── test_engine.py       # Engine orchestration tests
├── test_integration.py  # Integration tests
└── test_api.py          # API endpoint testing script
```

## Test Categories

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test full workflows with mocked dependencies
- **Fixtures**: Reusable test data and mocks in `conftest.py`

## Writing New Tests

1. Create test file: `tests/test_your_feature.py`
2. Import pytest and your module
3. Use fixtures from `conftest.py`
4. Follow naming: `test_function_name()`
5. Use descriptive test names

Example:

```python
def test_new_feature():
    """Test description."""
    # Arrange
    config = load_config("test_config.yaml")
    
    # Act
    result = your_function(config)
    
    # Assert
    assert result == expected_value
```

## Continuous Integration

Tests are designed to run in CI/CD pipelines:
- Fast execution
- No external dependencies
- Mocked Letta client
- Isolated test environment

