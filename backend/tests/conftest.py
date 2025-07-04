"""
Global pytest fixtures for spatial-index-api tests.

This module contains fixtures that are available to all test modules.
"""
import os
import pytest
from typing import Generator, Dict, Any
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

from app.database import DatabaseConfig, get_db_session
from app.main import app


# Test database configuration
TEST_DB_CONFIG = {
    "USERNAME": "test_user",
    "PASS": "test_pass",
    "URL": "test_host:5432",
    "DB": "test_db"
}


@pytest.fixture(scope="session")
def mock_env_vars():
    """Mock environment variables for testing."""
    with patch.dict(os.environ, TEST_DB_CONFIG):
        yield TEST_DB_CONFIG


@pytest.fixture(scope="session")
def test_db_config(mock_env_vars) -> DatabaseConfig:
    """Create test database configuration."""
    return DatabaseConfig(
        username=TEST_DB_CONFIG["USERNAME"],
        password=TEST_DB_CONFIG["PASS"],
        url=TEST_DB_CONFIG["URL"],
        database=TEST_DB_CONFIG["DB"]
    )


@pytest.fixture(scope="session")
def test_engine():
    """
    Create a test database engine using SQLite in-memory database.
    
    This provides fast, isolated testing without requiring a real PostgreSQL instance.
    """
    # Use SQLite for testing with proper configuration
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
    
    # Enable foreign key support in SQLite
    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys=ON"))
        conn.commit()
    
    # Create tables manually without schema since SQLite doesn't support schemas
    with engine.connect() as conn:
        # Create occupation_lvl_data table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS occupation_lvl_data (
                geoid VARCHAR NOT NULL,
                category VARCHAR NOT NULL,
                openings_2024_zscore FLOAT,
                jobs_2024_zscore FLOAT,
                openings_2024_zscore_color VARCHAR,
                geom TEXT,
                PRIMARY KEY (geoid, category)
            )
        """))
        
        # Create tti_clone table (without geometry for SQLite)
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS tti_clone (
                geoid VARCHAR NOT NULL PRIMARY KEY,
                all_jobs_zscore FLOAT,
                all_jobs_zscore_cat VARCHAR,
                living_wage_zscore FLOAT,
                living_wage_zscore_cat VARCHAR,
                not_living_wage_zscore FLOAT,
                not_living_wage_zscore_cat VARCHAR,
                geom TEXT
            )
        """))
        conn.commit()
    
    yield engine
    
    # Cleanup
    engine.dispose()


@pytest.fixture(scope="function")
def test_session(test_engine) -> Generator[Session, None, None]:
    """
    Create a test database session for each test function.
    
    This fixture provides database isolation between tests using transactions.
    """
    TestSessionLocal = sessionmaker(bind=test_engine, expire_on_commit=False)
    
    # Start a transaction
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestSessionLocal(bind=connection)
    
    yield session
    
    # Rollback the transaction to ensure test isolation
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def mock_db_session(test_session):
    """
    Override the get_db_session dependency with test session.
    
    This fixture patches the FastAPI dependency to use our test database.
    """
    def override_get_db():
        try:
            yield test_session
        finally:
            pass  # Session cleanup is handled by test_session fixture
    
    app.dependency_overrides[get_db_session] = override_get_db
    yield test_session
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_client(mock_db_session, mock_env_vars) -> TestClient:
    """
    Create a test client for the FastAPI application.
    
    This client can be used for synchronous API testing.
    """
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function")
async def async_test_client(mock_db_session, mock_env_vars) -> AsyncClient:
    """
    Create an async test client for the FastAPI application.
    
    This client should be used for testing async endpoints.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client


@pytest.fixture
def mock_geojson_data() -> Dict[str, Any]:
    """Sample GeoJSON data for testing spatial endpoints."""
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [-96.7970, 32.7767]
                },
                "properties": {
                    "geoid": "12345",
                    "all_jobs_zscore": 1.5,
                    "all_jobs_zscore_cat": "High",
                    "living_wage_zscore": 0.8,
                    "living_wage_zscore_cat": "Medium",
                    "not_living_wage_zscore": -0.5,
                    "not_living_wage_zscore_cat": "Low"
                }
            }
        ]
    }


@pytest.fixture
def mock_occupation_data() -> list:
    """Sample occupation data for testing."""
    return [
        "Healthcare Support",
        "Computer and Mathematical",
        "Education and Training",
        "Business and Financial Operations",
        "Construction and Extraction"
    ]


@pytest.fixture
def mock_occupation_spatial_data() -> Dict[str, Any]:
    """Sample occupation spatial data for testing."""
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [-96.7970, 32.7767]
                },
                "properties": {
                    "geoid": "48257050209",
                    "category": "51-3091",
                    "openings_2024_zscore": -0.0956,
                    "jobs_2024_zscore": 0.0187,
                    "openings_2024_zscore_color": "-0.5SD ~ +0.5SD"
                }
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [-96.3838, 32.7399]
                },
                "properties": {
                    "geoid": "48257050213",
                    "category": "51-3091",
                    "openings_2024_zscore": -0.2926,
                    "jobs_2024_zscore": -0.2762,
                    "openings_2024_zscore_color": "-0.5SD ~ +0.5SD"
                }
            }
        ]
    }


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """
    Reset rate limiter between tests to avoid rate limit issues.
    
    This fixture automatically runs for every test.
    """
    # Clear any rate limit state
    if hasattr(app.state, 'limiter'):
        # Reset the limiter's storage
        app.state.limiter.reset()
    yield


@pytest.fixture
def mock_sqlalchemy_query():
    """
    Mock SQLAlchemy query for unit testing without database.
    
    Useful for testing service methods in isolation.
    """
    mock_query = MagicMock()
    mock_session = MagicMock()
    mock_session.query.return_value = mock_query
    return mock_session, mock_query


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Set up the test environment before any tests run.
    
    This fixture runs automatically at the start of the test session.
    """
    # Set testing environment variable
    os.environ["TESTING"] = "1"
    
    # Disable SQL echo during tests for cleaner output
    os.environ["SQL_ECHO"] = "false"
    
    yield
    
    # Cleanup
    os.environ.pop("TESTING", None)
    os.environ.pop("SQL_ECHO", None)


@pytest.fixture
def capture_logs():
    """
    Capture log messages during tests.
    
    Usage:
        def test_something(capture_logs):
            with capture_logs() as logs:
                # Do something that generates logs
                pass
            assert "expected message" in logs.output
    """
    import logging
    from io import StringIO
    
    class LogCapture:
        def __init__(self):
            self.output = StringIO()
            self.handler = logging.StreamHandler(self.output)
            self.handler.setLevel(logging.DEBUG)
            
        def __enter__(self):
            logging.getLogger().addHandler(self.handler)
            return self
            
        def __exit__(self, *args):
            logging.getLogger().removeHandler(self.handler)
            self.output = self.output.getvalue()
            
    return LogCapture