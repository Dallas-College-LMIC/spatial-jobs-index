"""
Tests for refactored error handling with helper function.
"""

import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException


def test_helper_function_logs_and_raises_generic_error():
    """Test that the helper function logs errors and raises generic HTTPException."""
    # Import the helper function when it exists
    from app.main import handle_internal_error

    with patch("app.main.logger") as mock_logger:
        # Create a test exception
        test_error = Exception(
            "Database connection failed: postgresql://user:pass@host/db"
        )

        # Call the helper function and expect it to raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            handle_internal_error(test_error, "test_endpoint")

        # Verify the exception details
        assert exc_info.value.status_code == 500
        assert (
            exc_info.value.detail["message"]
            == "An internal error occurred. Please try again later."
        )
        assert exc_info.value.detail["error_code"] == "INTERNAL_SERVER_ERROR"
        assert exc_info.value.detail["context"] == {}

        # Verify logging was called with full error details
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args
        assert "Error in test_endpoint" in call_args[0][0]
        assert call_args[1]["exc_info"] is True


def test_get_occupation_ids_uses_helper_function():
    """Test that get_occupation_ids endpoint uses the helper function for error handling."""
    with patch("app.main.DatabaseConfig.from_env"):
        with patch("app.main.init_database"):
            from app.main import app
            from app.database import get_db_session

            # Mock the database session and service to raise an error
            mock_session = Mock()

            def override_get_db():
                yield mock_session

            app.dependency_overrides[get_db_session] = override_get_db

            from fastapi.testclient import TestClient

            with TestClient(app) as client:
                # Mock the service to raise an error
                with patch("app.main.OccupationService") as mock_service_class:
                    mock_service = Mock()
                    mock_service.get_occupations_with_names.side_effect = Exception(
                        "Database error with sensitive info"
                    )
                    mock_service_class.return_value = mock_service

                    # Make request and verify generic error response
                    response = client.get("/occupation_ids")
                    assert response.status_code == 500
                    error_data = response.json()
                    assert (
                        error_data["detail"]["message"]
                        == "An internal error occurred. Please try again later."
                    )
                    assert "sensitive info" not in str(error_data)

            app.dependency_overrides.clear()
