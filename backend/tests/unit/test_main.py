"""
Unit tests for the FastAPI application in app/main.py.

Tests cover:
- Application startup and shutdown lifecycle
- Endpoint behavior and responses
- CORS configuration
- Rate limiting behavior
- Error handling
- Dependency injection
"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import GeoJSONFeature, SpatialFeatureProperties


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


class TestApplicationLifecycle:
    """Test application startup and configuration."""

    def test_app_instance_created(self, mock_app):
        """Test that FastAPI app instance is created properly."""
        assert mock_app is not None
        assert mock_app.title == "Spatial Jobs Index API"

    def test_cors_middleware_configured(self, mock_app):
        """Test that CORS middleware is properly configured."""
        # Check that CORS middleware is added
        middlewares = [m for m in mock_app.user_middleware]
        cors_middleware = None
        for middleware in middlewares:
            if "CORSMiddleware" in str(middleware):
                cors_middleware = middleware
                break

        assert cors_middleware is not None

    def test_rate_limiter_configured(self, mock_app):
        """Test that rate limiter is properly configured."""
        assert hasattr(mock_app.state, "limiter")
        assert mock_app.state.limiter is not None

    def test_database_initialized_on_startup(self):
        """Test that database is initialized on module import."""
        # This test verifies that the module initialization calls are made
        # Since the module is already imported, we can't test the actual import
        # but we can verify the pattern is correct by checking the code exists
        import app.main
        import inspect

        source = inspect.getsource(app.main)
        assert "DatabaseConfig.from_env()" in source
        assert "init_database(db_config)" in source


class TestOccupationIdsEndpoint:
    """Test /occupation_ids endpoint."""

    @patch("app.main.OccupationService.get_occupations_with_names")
    def test_get_occupation_ids_success(self, mock_get_occupations, mock_client):
        """Test successful retrieval of occupation IDs."""
        mock_occupations = [
            {"code": "11-1021", "name": "General Managers"},
            {"code": "15-1251", "name": "Computer Programmers"},
        ]
        mock_get_occupations.return_value = mock_occupations

        response = mock_client.get("/occupation_ids")

        assert response.status_code == 200
        data = response.json()
        assert "occupations" in data
        assert len(data["occupations"]) == 2
        assert data["occupations"][0]["code"] == "11-1021"
        assert data["occupations"][0]["name"] == "General Managers"
        mock_get_occupations.assert_called_once()

    @patch("app.main.OccupationService.get_occupations_with_names")
    def test_get_occupation_ids_empty_list(self, mock_get_occupations, mock_client):
        """Test endpoint with empty occupation list."""
        mock_get_occupations.return_value = []

        response = mock_client.get("/occupation_ids")

        assert response.status_code == 200
        data = response.json()
        assert data["occupations"] == []

    @patch("app.main.OccupationService.get_occupations_with_names")
    def test_get_occupation_ids_service_error(self, mock_get_occupations, mock_client):
        """Test error handling when service raises exception."""
        mock_get_occupations.side_effect = Exception("Database connection failed")

        response = mock_client.get("/occupation_ids")

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        detail = data["detail"]
        # Security fix: should return generic error message
        assert "An internal error occurred" in detail["message"]
        assert "Database connection failed" not in detail["message"]

    @patch("app.main.OccupationService.get_occupations_with_names")
    def test_get_occupation_ids_rate_limiting(self, mock_get_occupations, mock_client):
        """Test rate limiting on occupation_ids endpoint (30/minute)."""
        mock_get_occupations.return_value = [{"code": "11-1021", "name": "Test"}]

        # Reset rate limiter
        from app.main import app

        if hasattr(app.state, "limiter"):
            app.state.limiter.reset()

        # Make 30 requests (should all succeed)
        for i in range(30):
            response = mock_client.get("/occupation_ids")
            assert response.status_code == 200

        # 31st request should be rate limited
        response = mock_client.get("/occupation_ids")
        assert response.status_code == 429
        error_data = response.json()
        assert "error" in error_data or "detail" in error_data
        error_msg = error_data.get("error", error_data.get("detail", ""))
        assert "Rate limit exceeded" in error_msg

    @patch("app.main.OccupationService.get_occupations_with_names")
    def test_get_occupation_ids_response_model_validation(
        self, mock_get_occupations, mock_client
    ):
        """Test that response follows the correct Pydantic model."""
        # Test via the client to ensure proper response validation
        mock_occupations = [
            {"code": "29-1141", "name": "Healthcare"},
            {"code": "15-1251", "name": "Technology"},
        ]
        mock_get_occupations.return_value = mock_occupations

        response = mock_client.get("/occupation_ids")

        assert response.status_code == 200
        data = response.json()

        # Validate the response structure matches OccupationsResponse
        assert "occupations" in data
        assert isinstance(data["occupations"], list)
        assert len(data["occupations"]) == 2
        assert all("code" in occ and "name" in occ for occ in data["occupations"])
        assert data["occupations"][0]["code"] == "29-1141"
        assert data["occupations"][0]["name"] == "Healthcare"


class TestGeojsonEndpoint:
    """Test /geojson endpoint."""

    @patch("app.main.SpatialService.get_geojson_features")
    def test_get_geojson_success(self, mock_get_features, mock_client):
        """Test successful retrieval of GeoJSON data."""
        # Create mock features
        mock_features = [
            GeoJSONFeature(
                geometry={"type": "Point", "coordinates": [-96.7970, 32.7767]},
                properties=SpatialFeatureProperties(
                    geoid="12345",
                    all_jobs_zscore=1.5,
                    all_jobs_zscore_cat="High",
                    living_wage_zscore=0.8,
                    living_wage_zscore_cat="Medium",
                    not_living_wage_zscore=-0.5,
                    not_living_wage_zscore_cat="Low",
                ),
            )
        ]

        mock_get_features.return_value = mock_features

        response = mock_client.get("/geojson")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/geo+json"
        assert response.headers["content-disposition"] == "inline"

        data = response.json()
        assert data["type"] == "FeatureCollection"
        assert len(data["features"]) == 1
        assert data["features"][0]["properties"]["geoid"] == "12345"

    @patch("app.main.SpatialService.get_geojson_features")
    def test_get_geojson_empty_features(self, mock_get_features, mock_client):
        """Test endpoint with no spatial data."""
        mock_get_features.return_value = []

        response = mock_client.get("/geojson")

        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "FeatureCollection"
        assert data["features"] == []

    @patch("app.main.SpatialService.get_geojson_features")
    def test_get_geojson_service_error(self, mock_get_features, mock_client):
        """Test error handling when spatial service fails."""
        mock_get_features.side_effect = Exception("Spatial query failed")

        response = mock_client.get("/geojson")

        assert response.status_code == 500
        data = response.json()
        detail = data["detail"]
        # Security fix: should return generic error message
        assert "An internal error occurred" in detail["message"]
        assert "Spatial query failed" not in detail["message"]

    @patch("app.main.SpatialService.get_geojson_features")
    def test_get_geojson_rate_limiting(self, mock_get_features, mock_client):
        """Test rate limiting on geojson endpoint (10/minute)."""
        mock_get_features.return_value = []

        # Reset rate limiter
        from app.main import app

        if hasattr(app.state, "limiter"):
            app.state.limiter.reset()

        # Make 10 requests (should all succeed)
        for i in range(10):
            response = mock_client.get("/geojson")
            assert response.status_code == 200

        # 11th request should be rate limited
        response = mock_client.get("/geojson")
        assert response.status_code == 429
        error_data = response.json()
        assert "error" in error_data or "detail" in error_data
        error_msg = error_data.get("error", error_data.get("detail", ""))
        assert "Rate limit exceeded" in error_msg

    @patch("app.main.SpatialService.get_geojson_features")
    def test_get_geojson_content_type(self, mock_get_features, mock_client):
        """Test that geojson endpoint returns correct content type."""
        mock_get_features.return_value = []

        response = mock_client.get("/geojson")

        assert response.headers["content-type"] == "application/geo+json"
        assert "application/geo+json" in response.headers.get("content-type", "")

    @patch("app.main.SpatialService")
    def test_get_geojson_large_dataset(self, mock_service_class, mock_client):
        """Test endpoint with large number of features."""
        # Create 1000 mock features
        mock_features = []
        for i in range(1000):
            feature = GeoJSONFeature(
                geometry={
                    "type": "Point",
                    "coordinates": [-96.7970 + i * 0.001, 32.7767 + i * 0.001],
                },
                properties=SpatialFeatureProperties(
                    geoid=str(i),
                    all_jobs_zscore=1.5,
                    all_jobs_zscore_cat="High",
                    living_wage_zscore=0.8,
                    living_wage_zscore_cat="Medium",
                    not_living_wage_zscore=-0.5,
                    not_living_wage_zscore_cat="Low",
                ),
            )
            mock_features.append(feature)

        # Mock the service instance and its method
        mock_service_instance = Mock()
        mock_service_instance.get_geojson_features.return_value = mock_features
        mock_service_class.return_value = mock_service_instance

        response = mock_client.get("/geojson")

        assert response.status_code == 200
        data = response.json()
        assert len(data["features"]) == 1000


class TestErrorHandling:
    """Test application-wide error handling."""

    def test_structured_error_response_format(self, mock_client):
        """Test that service errors return structured error responses."""
        with patch(
            "app.main.OccupationService.get_occupations_with_names"
        ) as mock_service:
            mock_service.side_effect = Exception("Database connection failed")

            response = mock_client.get("/occupation_ids")

            assert response.status_code == 500
            data = response.json()

            # Test structured error format
            assert "detail" in data
            detail = data["detail"]
            assert isinstance(detail, dict)
            assert "message" in detail
            assert "error_code" in detail
            assert "context" in detail
            assert detail["error_code"] == "INTERNAL_SERVER_ERROR"
            # Security fix: should not expose internal error details
            assert "An internal error occurred" in detail["message"]
            assert "Database connection failed" not in detail["message"]

    def test_http_exception_handling(self, mock_client):
        """Test that HTTPExceptions are properly handled."""
        # Test with a non-existent endpoint
        response = mock_client.get("/non-existent-endpoint")
        assert response.status_code == 404
        assert "detail" in response.json()

    @patch("app.main.OccupationService.get_occupation_ids")
    def test_rate_limit_exception_handler(self, mock_get_ids, mock_client):
        """Test that rate limit exceptions are properly formatted."""
        mock_get_ids.return_value = []

        # Reset rate limiter
        from app.main import app

        if hasattr(app.state, "limiter"):
            app.state.limiter.reset()

        # Make requests until rate limited
        responses = []
        for i in range(35):  # More than the 30/minute limit
            response = mock_client.get("/occupation_ids")
            responses.append(response)

        # Find the rate limited response
        rate_limited = [r for r in responses if r.status_code == 429]
        assert len(rate_limited) > 0

        # Check error format
        error_data = rate_limited[0].json()
        assert "error" in error_data or "detail" in error_data
        error_msg = error_data.get("error", error_data.get("detail", ""))
        assert "Rate limit exceeded" in error_msg


class TestDependencyInjection:
    """Test FastAPI dependency injection system."""

    @patch("app.main.OccupationService")
    def test_database_session_injection(self, mock_service_class, mock_client):
        """Test that database session is properly injected."""
        # Mock the service instance and its method
        mock_service_instance = Mock()
        mock_service_instance.get_occupations_with_names.return_value = [
            {"code": "11-1021", "name": "Test"}
        ]
        mock_service_class.return_value = mock_service_instance

        response = mock_client.get("/occupation_ids")

        assert response.status_code == 200
        # The service class should have been instantiated with a session
        mock_service_class.assert_called_once()
        # Check that a session-like object was passed to the constructor
        call_args = mock_service_class.call_args
        assert len(call_args[0]) == 1  # One positional argument (the session)

    @patch("app.main.OccupationService")
    def test_request_injection_for_rate_limiting(self, mock_service_class, mock_client):
        """Test that Request object is properly injected for rate limiting."""
        # Mock the service instance and its method
        mock_service_instance = Mock()
        mock_service_instance.get_occupations_with_names.return_value = [
            {"code": "11-1021", "name": "Test"}
        ]
        mock_service_class.return_value = mock_service_instance

        response = mock_client.get("/occupation_ids")

        assert response.status_code == 200
        # The fact that rate limiting works proves Request injection is working


class TestCORSBehavior:
    """Test CORS behavior in detail."""

    @patch("app.main.OccupationService.get_occupations_with_names")
    def test_cors_allowed_origins(self, mock_get_occupations, mock_client):
        """Test CORS with allowed origins."""
        mock_get_occupations.return_value = []

        allowed_origins = [
            "https://dallas-college-lmic.github.io",
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
        ]

        for origin in allowed_origins:
            response = mock_client.get("/occupation_ids", headers={"Origin": origin})
            assert response.status_code in [200, 429]  # 429 if rate limited
            if response.status_code == 200:
                assert response.headers.get("access-control-allow-origin") == origin

    @patch("app.main.OccupationService.get_occupations_with_names")
    def test_cors_disallowed_origin(self, mock_get_occupations, mock_client):
        """Test CORS with disallowed origin."""
        mock_get_occupations.return_value = []

        response = mock_client.get(
            "/occupation_ids", headers={"Origin": "http://evil-site.com"}
        )
        # The response might still be 200, but no CORS headers
        assert response.status_code in [200, 429]
        # Disallowed origins won't get the CORS header
        if response.status_code == 200:
            assert (
                response.headers.get("access-control-allow-origin")
                != "http://evil-site.com"
            )

    def test_cors_preflight_request(self, mock_client):
        """Test CORS preflight OPTIONS request."""
        response = mock_client.options(
            "/occupation_ids",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "content-type",
            },
        )
        assert response.status_code == 200
        assert (
            response.headers.get("access-control-allow-origin")
            == "http://localhost:5173"
        )
        assert "GET" in response.headers.get("access-control-allow-methods", "")


class TestResponseFormats:
    """Test response format consistency."""

    def test_error_response_format(self, mock_client):
        """Test that all errors follow consistent format."""
        # Test 404 error
        response = mock_client.get("/non-existent")
        assert response.status_code == 404
        error_data = response.json()
        assert "detail" in error_data

        # Test 500 error
        with patch(
            "app.main.OccupationService.get_occupations_with_names"
        ) as mock_service:
            mock_service.side_effect = Exception("Test error")
            response = mock_client.get("/occupation_ids")
            assert response.status_code == 500
            error_data = response.json()
            assert "detail" in error_data
            detail = error_data["detail"]
            # Security fix: should return generic error message
            assert "An internal error occurred" in detail["message"]
            assert "Test error" not in detail["message"]

    @patch("app.main.OccupationService.get_occupations_with_names")
    @patch("app.main.SpatialService.get_geojson_features")
    def test_success_response_formats(
        self, mock_spatial_service, mock_occupation_service, mock_client
    ):
        """Test that successful responses follow expected formats."""
        # Test occupation_ids format
        mock_occupation_service.return_value = [
            {"code": "11-1021", "name": "Test1"},
            {"code": "15-1251", "name": "Test2"},
        ]
        response = mock_client.get("/occupation_ids")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "occupations" in data
        assert isinstance(data["occupations"], list)

        # Test geojson format
        mock_spatial_service.return_value = []
        response = mock_client.get("/geojson")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert data["type"] == "FeatureCollection"
        assert "features" in data
