"""Unit tests for School of Study API endpoints."""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import SchoolOfStudyGeoJSONFeature, SchoolOfStudySpatialProperties


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


class TestSchoolOfStudyIdsEndpoint:
    """Test /school_of_study_ids endpoint."""

    @patch("app.main.SchoolOfStudyService.get_school_ids")
    def test_get_school_of_study_ids_success(self, mock_get_school_ids, mock_client):
        """Test successful retrieval of school of study IDs."""
        mock_school_ids = ["BHGT", "CAED", "CE", "EDU", "ETMS", "HS", "LPS", "MIT"]
        mock_get_school_ids.return_value = mock_school_ids

        response = mock_client.get("/school_of_study_ids")

        assert response.status_code == 200
        data = response.json()
        assert "school_ids" in data
        assert len(data["school_ids"]) == 8
        assert data["school_ids"] == mock_school_ids
        mock_get_school_ids.assert_called_once()

    @patch("app.main.SchoolOfStudyService.get_school_ids")
    def test_get_school_of_study_ids_empty_list(self, mock_get_school_ids, mock_client):
        """Test endpoint with empty school IDs list."""
        mock_get_school_ids.return_value = []

        response = mock_client.get("/school_of_study_ids")

        assert response.status_code == 200
        data = response.json()
        assert data["school_ids"] == []

    @patch("app.main.SchoolOfStudyService.get_school_ids")
    def test_get_school_of_study_ids_service_error(
        self, mock_get_school_ids, mock_client
    ):
        """Test error handling when service raises exception."""
        mock_get_school_ids.side_effect = Exception("Database connection failed")

        response = mock_client.get("/school_of_study_ids")

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        # Security fix: should return generic error message
        assert "An internal error occurred" in data["detail"]
        assert "Database connection failed" not in data["detail"]

    @patch("app.main.SchoolOfStudyService.get_school_ids")
    def test_get_school_of_study_ids_rate_limiting(
        self, mock_get_school_ids, mock_client
    ):
        """Test rate limiting on school_of_study_ids endpoint (30/minute)."""
        mock_get_school_ids.return_value = ["ETMS", "BHGT"]

        # Reset rate limiter
        from app.main import app

        if hasattr(app.state, "limiter"):
            app.state.limiter.reset()

        # Make 30 requests (should all succeed)
        for i in range(30):
            response = mock_client.get("/school_of_study_ids")
            assert response.status_code == 200

        # 31st request should be rate limited
        response = mock_client.get("/school_of_study_ids")
        assert response.status_code == 429
        error_data = response.json()
        assert "error" in error_data or "detail" in error_data
        error_msg = error_data.get("error", error_data.get("detail", ""))
        assert "Rate limit exceeded" in error_msg

    @patch("app.main.SchoolOfStudyService.get_school_ids")
    def test_get_school_of_study_ids_response_model_validation(
        self, mock_get_school_ids, mock_client
    ):
        """Test that response follows the correct Pydantic model."""
        mock_school_ids = ["ETMS", "BHGT", "CE"]
        mock_get_school_ids.return_value = mock_school_ids

        response = mock_client.get("/school_of_study_ids")

        assert response.status_code == 200
        data = response.json()

        # Validate the response structure matches SchoolOfStudyIdsResponse
        assert "school_ids" in data
        assert isinstance(data["school_ids"], list)
        assert len(data["school_ids"]) == 3
        assert all(isinstance(school_id, str) for school_id in data["school_ids"])
        assert data["school_ids"] == ["ETMS", "BHGT", "CE"]

    @patch("app.main.SchoolOfStudyService.get_school_ids")
    def test_get_school_of_study_ids_caching_behavior(
        self, mock_get_school_ids, mock_client
    ):
        """Test caching behavior (24-hour cache)."""
        # This test verifies that the endpoint can handle caching
        # The actual caching logic would be implemented in the service layer
        mock_school_ids = ["ETMS", "BHGT"]
        mock_get_school_ids.return_value = mock_school_ids

        # First request
        response1 = mock_client.get("/school_of_study_ids")
        assert response1.status_code == 200

        # Second request - should work regardless of caching
        response2 = mock_client.get("/school_of_study_ids")
        assert response2.status_code == 200

        # Both responses should be identical
        assert response1.json() == response2.json()


class TestSchoolOfStudyDataEndpoint:
    """Test /school_of_study_data/{category} endpoint."""

    @patch("app.main.SchoolOfStudyService.get_school_spatial_data")
    def test_get_school_of_study_data_success(self, mock_get_spatial_data, mock_client):
        """Test successful retrieval of school spatial data."""
        # Create mock features
        mock_features = [
            SchoolOfStudyGeoJSONFeature(
                geometry={"type": "Point", "coordinates": [-96.7970, 32.7767]},
                properties=SchoolOfStudySpatialProperties(
                    geoid="48113020100",
                    category="ETMS",
                    openings_2024_zscore=1.5,
                    jobs_2024_zscore=0.8,
                    openings_2024_zscore_color="#FF0000",
                ),
            )
        ]

        mock_get_spatial_data.return_value = mock_features

        response = mock_client.get("/school_of_study_data/ETMS")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/geo+json"
        assert response.headers["content-disposition"] == "inline"

        data = response.json()
        assert data["type"] == "FeatureCollection"
        assert len(data["features"]) == 1
        assert data["features"][0]["properties"]["geoid"] == "48113020100"
        assert data["features"][0]["properties"]["category"] == "ETMS"
        mock_get_spatial_data.assert_called_once()

    @patch("app.main.SchoolOfStudyService.get_school_spatial_data")
    def test_get_school_of_study_data_valid_categories(
        self, mock_get_spatial_data, mock_client
    ):
        """Test endpoint with all valid school categories."""
        valid_categories = ["BHGT", "CAED", "CE", "EDU", "ETMS", "HS", "LPS", "MIT"]

        mock_features = [
            SchoolOfStudyGeoJSONFeature(
                geometry={"type": "Point", "coordinates": [-96.7970, 32.7767]},
                properties=SchoolOfStudySpatialProperties(
                    geoid="48113020100",
                    category="TEST",
                    openings_2024_zscore=1.0,
                    jobs_2024_zscore=0.5,
                    openings_2024_zscore_color="#00FF00",
                ),
            )
        ]
        mock_get_spatial_data.return_value = mock_features

        for category in valid_categories:
            response = mock_client.get(f"/school_of_study_data/{category}")
            assert response.status_code == 200
            data = response.json()
            assert data["type"] == "FeatureCollection"

    @patch("app.main.SchoolOfStudyService.get_school_spatial_data")
    def test_get_school_of_study_data_not_found(
        self, mock_get_spatial_data, mock_client
    ):
        """Test endpoint with category that has no data."""
        mock_get_spatial_data.return_value = []

        response = mock_client.get("/school_of_study_data/NONEXISTENT")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "No data found for school category: NONEXISTENT" in data["detail"]

    @patch("app.main.SchoolOfStudyService.get_school_spatial_data")
    def test_get_school_of_study_data_invalid_category(
        self, mock_get_spatial_data, mock_client
    ):
        """Test endpoint with invalid category handling."""
        mock_get_spatial_data.return_value = []

        response = mock_client.get("/school_of_study_data/INVALID")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "No data found for school category: INVALID" in data["detail"]

    @patch("app.main.SchoolOfStudyService.get_school_spatial_data")
    def test_get_school_of_study_data_service_error(
        self, mock_get_spatial_data, mock_client
    ):
        """Test error handling when spatial service fails."""
        mock_get_spatial_data.side_effect = Exception("Spatial query failed")

        response = mock_client.get("/school_of_study_data/ETMS")

        assert response.status_code == 500
        data = response.json()
        # Security fix: should return generic error message
        assert "An internal error occurred" in data["detail"]
        assert "Spatial query failed" not in data["detail"]

    @patch("app.main.SchoolOfStudyService.get_school_spatial_data")
    def test_get_school_of_study_data_rate_limiting(
        self, mock_get_spatial_data, mock_client
    ):
        """Test rate limiting on school_of_study_data endpoint (30/minute)."""
        mock_features = [
            SchoolOfStudyGeoJSONFeature(
                geometry={"type": "Point", "coordinates": [-96.7970, 32.7767]},
                properties=SchoolOfStudySpatialProperties(
                    geoid="48113020100",
                    category="ETMS",
                    openings_2024_zscore=1.0,
                    jobs_2024_zscore=0.5,
                    openings_2024_zscore_color="#00FF00",
                ),
            )
        ]
        mock_get_spatial_data.return_value = mock_features

        # Reset rate limiter
        from app.main import app

        if hasattr(app.state, "limiter"):
            app.state.limiter.reset()

        # Make 30 requests (should all succeed)
        for i in range(30):
            response = mock_client.get("/school_of_study_data/ETMS")
            assert response.status_code == 200

        # 31st request should be rate limited
        response = mock_client.get("/school_of_study_data/ETMS")
        assert response.status_code == 429
        error_data = response.json()
        assert "error" in error_data or "detail" in error_data
        error_msg = error_data.get("error", error_data.get("detail", ""))
        assert "Rate limit exceeded" in error_msg

    @patch("app.main.SchoolOfStudyService.get_school_spatial_data")
    def test_get_school_of_study_data_content_type(
        self, mock_get_spatial_data, mock_client
    ):
        """Test that endpoint returns correct content type."""
        mock_features = []
        mock_get_spatial_data.return_value = mock_features

        response = mock_client.get("/school_of_study_data/ETMS")

        # Should be 404 for empty features, but test content type on error
        assert response.status_code == 404

        # Test with data
        mock_features = [
            SchoolOfStudyGeoJSONFeature(
                geometry={"type": "Point", "coordinates": [-96.7970, 32.7767]},
                properties=SchoolOfStudySpatialProperties(
                    geoid="48113020100",
                    category="ETMS",
                    openings_2024_zscore=1.0,
                    jobs_2024_zscore=0.5,
                    openings_2024_zscore_color="#00FF00",
                ),
            )
        ]
        mock_get_spatial_data.return_value = mock_features

        response = mock_client.get("/school_of_study_data/ETMS")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/geo+json"
        assert "application/geo+json" in response.headers.get("content-type", "")

    @patch("app.main.SchoolOfStudyService.get_school_spatial_data")
    def test_get_school_of_study_data_empty_features(
        self, mock_get_spatial_data, mock_client
    ):
        """Test endpoint with no spatial data for category."""
        mock_get_spatial_data.return_value = []

        response = mock_client.get("/school_of_study_data/ETMS")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "No data found for school category: ETMS" in data["detail"]

    @patch("app.main.SchoolOfStudyService.get_school_spatial_data")
    def test_get_school_of_study_data_large_dataset(
        self, mock_get_spatial_data, mock_client
    ):
        """Test endpoint with large number of features."""
        # Create 100 mock features
        mock_features = []
        for i in range(100):
            feature = SchoolOfStudyGeoJSONFeature(
                geometry={
                    "type": "Point",
                    "coordinates": [-96.7970 + i * 0.001, 32.7767 + i * 0.001],
                },
                properties=SchoolOfStudySpatialProperties(
                    geoid=f"4811302{i:04d}",
                    category="ETMS",
                    openings_2024_zscore=1.5,
                    jobs_2024_zscore=0.8,
                    openings_2024_zscore_color="#FF0000",
                ),
            )
            mock_features.append(feature)

        mock_get_spatial_data.return_value = mock_features

        response = mock_client.get("/school_of_study_data/ETMS")

        assert response.status_code == 200
        data = response.json()
        assert len(data["features"]) == 100

    @patch("app.main.SchoolOfStudyService.get_school_spatial_data")
    def test_get_school_of_study_data_response_format(
        self, mock_get_spatial_data, mock_client
    ):
        """Test that response format matches GeoJSON specification."""
        mock_features = [
            SchoolOfStudyGeoJSONFeature(
                geometry={"type": "Point", "coordinates": [-96.7970, 32.7767]},
                properties=SchoolOfStudySpatialProperties(
                    geoid="48113020100",
                    category="ETMS",
                    openings_2024_zscore=1.5,
                    jobs_2024_zscore=0.8,
                    openings_2024_zscore_color="#FF0000",
                ),
            )
        ]

        mock_get_spatial_data.return_value = mock_features

        response = mock_client.get("/school_of_study_data/ETMS")

        assert response.status_code == 200
        data = response.json()

        # Validate GeoJSON structure
        assert data["type"] == "FeatureCollection"
        assert "features" in data
        assert isinstance(data["features"], list)

        if data["features"]:
            feature = data["features"][0]
            assert feature["type"] == "Feature"
            assert "geometry" in feature
            assert "properties" in feature

            # Validate properties structure
            props = feature["properties"]
            required_props = [
                "geoid",
                "category",
                "openings_2024_zscore",
                "jobs_2024_zscore",
                "openings_2024_zscore_color",
            ]
            for prop in required_props:
                assert prop in props
