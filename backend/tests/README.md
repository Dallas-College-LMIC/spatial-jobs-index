# Test Infrastructure for Spatial Index API

This directory contains the test suite for the spatial-index-api project.

## Setup

Install test dependencies:
```bash
uv sync --group test
```

## Running Tests

Run all tests:
```bash
uv run pytest
```

Run specific test categories:
```bash
# Unit tests only
uv run pytest -m unit

# Integration tests
uv run pytest -m integration

# API tests
uv run pytest -m api

# Exclude slow tests
uv run pytest -m "not slow"
```

Run with coverage:
```bash
uv run pytest --cov=app --cov-report=html
```

## Test Structure

- `conftest.py` - Global fixtures and test configuration
- `factories.py` - Test data factories using factory-boy
- `test_*.py` - Test modules organized by functionality

## Key Fixtures

### Database Fixtures
- `test_session` - Provides an isolated database session for each test
- `mock_db_session` - Overrides FastAPI's database dependency
- `test_engine` - SQLite in-memory database engine for fast testing

### Client Fixtures
- `test_client` - Synchronous FastAPI test client
- `async_test_client` - Asynchronous test client for async endpoints

### Data Fixtures
- `mock_geojson_data` - Sample GeoJSON data
- `mock_occupation_data` - Sample occupation categories
- `mock_sqlalchemy_query` - Mocked SQLAlchemy query for unit tests

### Environment Fixtures
- `mock_env_vars` - Mocks required environment variables
- `setup_test_environment` - Automatically sets up test environment

## Writing Tests

### Unit Test Example
```python
def test_service_method(mock_sqlalchemy_query):
    session, query = mock_sqlalchemy_query
    # Test service logic without database
```

### Integration Test Example
```python
@pytest.mark.integration
def test_with_database(test_session):
    # Create test data
    data = TTICloneFactory()
    test_session.add(data)
    test_session.commit()
    # Test with real database operations
```

### API Test Example
```python
@pytest.mark.api
def test_endpoint(test_client):
    response = test_client.get("/endpoint")
    assert response.status_code == 200
```

## Test Data Generation

Use factories to create consistent test data:
```python
from tests.factories import (
    OccupationLvlDataFactory,
    TTICloneFactory,
    create_sample_occupation_data,
    create_sample_spatial_data
)

# Create single instance
occupation = OccupationLvlDataFactory()

# Create batch
spatial_data = TTICloneFactory.create_batch(5)

# Create with specific attributes
high_jobs_area = TTICloneFactory(
    all_jobs_zscore=2.5,
    all_jobs_zscore_cat="High"
)
```

## Notes

- Tests use SQLite in-memory database for speed and isolation
- Some spatial features require PostgreSQL with PostGIS
- Rate limiting is automatically reset between tests
- Database transactions are rolled back after each test for isolation
