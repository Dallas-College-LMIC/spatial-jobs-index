"""
Test cases for secure error handling that prevents information leakage.

These tests ensure that internal error details are not exposed to clients
while still providing useful debugging information via correlation IDs.
"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


@pytest.fixture
def mock_app():
    """Create a mock FastAPI app for testing without database dependencies."""
    with patch("app.main.DatabaseConfig.from_env"):
        with patch("app.main.init_database"):
            # Import app after mocking to avoid database initialization
            from app.main import app

            return app


@pytest.fixture
def mock_client(mock_app):
    """Create test client with mocked database."""
    # Mock the database session dependency
    mock_session = Mock(spec=Session)

    def override_get_db():
        yield mock_session

    from app.database import get_db_session

    mock_app.dependency_overrides[get_db_session] = override_get_db

    with TestClient(mock_app) as client:
        yield client

    # Clean up
    mock_app.dependency_overrides.clear()


class TestSecureErrorHandling:
    """Test that error responses don't leak sensitive information."""

    @patch("app.main.OccupationService.get_occupations_with_names")
    def test_database_error_does_not_leak_details(self, mock_service, mock_client):
        """Test that database connection errors don't expose connection strings."""
        # Simulate a database error with sensitive information
        mock_service.side_effect = Exception(
            "connection to server at 'db.internal:5432', database 'prod_db' failed: password authentication failed for user 'admin'"
        )

        response = mock_client.get("/occupation_ids")

        assert response.status_code == 500
        data = response.json()

        # The response should NOT contain sensitive database information
        response_text = str(data)
        assert "db.internal" not in response_text
        assert "5432" not in response_text
        assert "prod_db" not in response_text
        assert "admin" not in response_text
        assert "password" not in response_text.lower()

        # The response SHOULD contain a generic error message
        assert "detail" in data
        detail = data["detail"]
        assert (
            detail["message"] == "An internal error occurred. Please try again later."
        )
        assert detail["error_code"] == "INTERNAL_SERVER_ERROR"

    @patch("app.main.SchoolOfStudyService.get_school_ids")
    def test_school_of_study_error_does_not_leak_details(
        self, mock_service, mock_client
    ):
        """Test that school of study errors don't expose internal details."""
        # Simulate an error with sensitive information
        mock_service.side_effect = Exception(
            "Failed to connect to database at internal.db:5432"
        )

        response = mock_client.get("/school_of_study_ids")

        assert response.status_code == 500
        data = response.json()

        # Should not expose internal details
        response_text = str(data)
        assert "internal.db" not in response_text
        assert "5432" not in response_text

        # Should return generic error
        assert "detail" in data
        assert "An internal error occurred" in str(data["detail"])
