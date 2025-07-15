"""Integration tests for School of Study API endpoints."""

import pytest
from unittest.mock import patch
from sqlalchemy import text

from app.models import SchoolOfStudyGeoJSONFeature, SchoolOfStudySpatialProperties


@pytest.fixture
def school_test_data():
    """Sample school of study data for testing."""
    return [
        {
            "category": "BHGT",
            "geoid": "48113020100",
            "openings_zscore": 1.5,
            "jobs_zscore": 0.8,
            "color": "#FF0000",
        },
        {
            "category": "CAED",
            "geoid": "48113020200",
            "openings_zscore": -0.3,
            "jobs_zscore": 1.2,
            "color": "#00FF00",
        },
        {
            "category": "CE",
            "geoid": "48113020300",
            "openings_zscore": 0.7,
            "jobs_zscore": -0.5,
            "color": "#0000FF",
        },
        {
            "category": "EDU",
            "geoid": "48113020400",
            "openings_zscore": -1.2,
            "jobs_zscore": 0.9,
            "color": "#FFFF00",
        },
        {
            "category": "ETMS",
            "geoid": "48113020500",
            "openings_zscore": 2.1,
            "jobs_zscore": -0.8,
            "color": "#FF00FF",
        },
        {
            "category": "HS",
            "geoid": "48113020600",
            "openings_zscore": 0.4,
            "jobs_zscore": 1.7,
            "color": "#00FFFF",
        },
        {
            "category": "LPS",
            "geoid": "48113020700",
            "openings_zscore": -0.9,
            "jobs_zscore": 0.3,
            "color": "#FFA500",
        },
        {
            "category": "MIT",
            "geoid": "48113020800",
            "openings_zscore": 1.8,
            "jobs_zscore": -1.1,
            "color": "#800080",
        },
    ]


@pytest.fixture
def setup_school_data(test_session, school_test_data):
    """Setup school_of_lvl_data table with test data."""
    # Clear existing data
    test_session.execute(text("DELETE FROM school_of_lvl_data"))
    test_session.commit()

    # Insert test data with geometry
    for school in school_test_data:
        test_session.execute(
            text("""
                INSERT INTO school_of_lvl_data
                (geoid, category, openings_2024_zscore, jobs_2024_zscore, openings_2024_zscore_color, geom)
                VALUES (:geoid, :category, :openings_zscore, :jobs_zscore, :color, '{"type": "Point", "coordinates": [-96.7970, 32.7767]}')
            """),
            {
                "geoid": school["geoid"],
                "category": school["category"],
                "openings_zscore": school["openings_zscore"],
                "jobs_zscore": school["jobs_zscore"],
                "color": school["color"],
            },
        )
    test_session.commit()

    yield school_test_data

    # Cleanup
    test_session.execute(text("DELETE FROM school_of_lvl_data"))
    test_session.commit()


class TestSchoolOfStudyIdsEndpoint:
    """Integration tests for /school_of_study_ids endpoint."""

    def test_school_of_study_ids_empty_database(self, test_client, test_session):
        """Test endpoint returns empty list when no school data exists."""
        # Ensure database is empty
        test_session.execute(text("DELETE FROM school_of_lvl_data"))
        test_session.commit()

        # Make request
        response = test_client.get("/school_of_study_ids")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "school_ids" in data
        assert data["school_ids"] == []

    def test_school_of_study_ids_with_data(self, test_client, setup_school_data):
        """Test endpoint returns all distinct school categories."""
        # Make request
        response = test_client.get("/school_of_study_ids")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "school_ids" in data
        assert len(data["school_ids"]) == 8

        # Check that all expected categories are present
        expected_categories = {"BHGT", "CAED", "CE", "EDU", "ETMS", "HS", "LPS", "MIT"}
        returned_categories = set(data["school_ids"])
        assert returned_categories == expected_categories

    def test_school_of_study_ids_duplicate_categories(self, test_client, test_session):
        """Test endpoint handles duplicate categories correctly."""
        # Clear existing data first
        test_session.execute(text("DELETE FROM school_of_lvl_data"))
        test_session.commit()

        # Insert duplicate data
        test_session.execute(
            text("""
            INSERT INTO school_of_lvl_data
            (geoid, category, openings_2024_zscore, jobs_2024_zscore, openings_2024_zscore_color, geom)
            VALUES
            ('48113020100', 'ETMS', 1.5, 0.8, '#FF0000', '{"type": "Point", "coordinates": [-96.7970, 32.7767]}'),
            ('48113020200', 'ETMS', -0.3, 1.2, '#00FF00', '{"type": "Point", "coordinates": [-96.8000, 32.8000]}'),
            ('48113020300', 'BHGT', 0.7, -0.5, '#0000FF', '{"type": "Point", "coordinates": [-96.8100, 32.8100]}')
        """)
        )
        test_session.commit()

        # Make request
        response = test_client.get("/school_of_study_ids")

        # Assert - should return unique categories only
        assert response.status_code == 200
        data = response.json()
        assert "school_ids" in data
        assert len(data["school_ids"]) == 2  # Only ETMS and BHGT
        assert set(data["school_ids"]) == {"ETMS", "BHGT"}

    def test_school_of_study_ids_rate_limiting(self, test_client, setup_school_data):
        """Test that rate limiting is applied to the endpoint (30/minute)."""
        # Make many requests quickly
        responses = []
        for _ in range(35):
            response = test_client.get("/school_of_study_ids")
            responses.append(response.status_code)

        # Some requests should be rate limited (429)
        assert 429 in responses
        # But first 30 should succeed
        assert responses[:30].count(200) == 30

    def test_school_of_study_ids_response_format(self, test_client, setup_school_data):
        """Test that response format matches the expected schema."""
        # Make request
        response = test_client.get("/school_of_study_ids")

        # Validate response structure
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

        data = response.json()
        assert isinstance(data, dict)
        assert "school_ids" in data
        assert isinstance(data["school_ids"], list)

        # Validate each school ID is a string
        for school_id in data["school_ids"]:
            assert isinstance(school_id, str)
            assert len(school_id) > 0


class TestSchoolOfStudyDataEndpoint:
    """Integration tests for /school_of_study_data/{category} endpoint."""

    @patch("app.main.SchoolOfStudyService.get_school_spatial_data")
    def test_school_of_study_data_valid_category(
        self, mock_service, test_client, setup_school_data
    ):
        """Test endpoint with valid school category."""
        # Mock the spatial service to avoid PostGIS issues in SQLite
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
        mock_service.return_value = mock_features

        response = test_client.get("/school_of_study_data/ETMS")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/geo+json"
        assert response.headers["content-disposition"] == "inline"

        data = response.json()
        assert data["type"] == "FeatureCollection"
        assert "features" in data
        assert len(data["features"]) == 1

        # Validate feature structure
        feature = data["features"][0]
        assert feature["type"] == "Feature"
        assert "geometry" in feature
        assert "properties" in feature

        # Validate properties
        props = feature["properties"]
        assert props["category"] == "ETMS"
        assert "geoid" in props
        assert "openings_2024_zscore" in props
        assert "jobs_2024_zscore" in props
        assert "openings_2024_zscore_color" in props

    @patch("app.main.SchoolOfStudyService.get_school_spatial_data")
    def test_school_of_study_data_nonexistent_category(
        self, mock_service, test_client, setup_school_data
    ):
        """Test endpoint with category that doesn't exist."""
        mock_service.return_value = []  # Empty result

        response = test_client.get("/school_of_study_data/NONEXISTENT")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "No data found for school category: NONEXISTENT" in data["detail"]

    def test_school_of_study_data_empty_database(self, test_client, test_session):
        """Test endpoint with empty database."""
        # Ensure database is empty
        test_session.execute(text("DELETE FROM school_of_lvl_data"))
        test_session.commit()

        response = test_client.get("/school_of_study_data/ETMS")

        # Debug: print the response if it's not 404
        if response.status_code != 404:
            print(f"DEBUG: Status {response.status_code}, Response: {response.text}")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "No data found for school category: ETMS" in data["detail"]

    def test_school_of_study_data_multiple_features(self, test_client, test_session):
        """Test endpoint returns multiple features for same category."""
        # Insert multiple features for same category
        test_session.execute(
            text("""
            INSERT INTO school_of_lvl_data
            (geoid, category, openings_2024_zscore, jobs_2024_zscore, openings_2024_zscore_color, geom)
            VALUES
            ('48113020100', 'ETMS', 1.5, 0.8, '#FF0000', '{"type": "Point", "coordinates": [-96.7970, 32.7767]}'),
            ('48113020200', 'ETMS', -0.3, 1.2, '#00FF00', '{"type": "Point", "coordinates": [-96.8000, 32.8000]}'),
            ('48113020300', 'ETMS', 0.7, -0.5, '#0000FF', '{"type": "Point", "coordinates": [-96.8100, 32.8100]}')
        """)
        )
        test_session.commit()

        response = test_client.get("/school_of_study_data/ETMS")

        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "FeatureCollection"
        assert len(data["features"]) == 3

        # Verify all features have correct category
        for feature in data["features"]:
            assert feature["properties"]["category"] == "ETMS"

        # Verify different geoids
        geoids = [f["properties"]["geoid"] for f in data["features"]]
        assert len(set(geoids)) == 3  # All different geoids

    def test_school_of_study_data_geometry_format(self, test_client, setup_school_data):
        """Test that geometry is returned in correct GeoJSON format."""
        response = test_client.get("/school_of_study_data/ETMS")

        assert response.status_code == 200
        data = response.json()

        feature = data["features"][0]
        geometry = feature["geometry"]

        # Validate geometry structure
        assert "type" in geometry
        assert "coordinates" in geometry
        assert isinstance(geometry["coordinates"], list)
        assert len(geometry["coordinates"]) == 2  # Longitude, Latitude

    def test_school_of_study_data_rate_limiting(self, test_client, setup_school_data):
        """Test that rate limiting is applied to the endpoint (30/minute)."""
        # Make many requests quickly
        responses = []
        for _ in range(35):
            response = test_client.get("/school_of_study_data/ETMS")
            responses.append(response.status_code)

        # Some requests should be rate limited (429)
        assert 429 in responses
        # But first 30 should succeed
        assert responses[:30].count(200) == 30

    def test_school_of_study_data_null_values(self, test_client, test_session):
        """Test endpoint handles NULL values in optional fields."""
        # Insert data with NULL values
        test_session.execute(
            text("""
            INSERT INTO school_of_lvl_data
            (geoid, category, openings_2024_zscore, jobs_2024_zscore, openings_2024_zscore_color, geom)
            VALUES
            ('48113020100', 'ETMS', NULL, NULL, NULL, '{"type": "Point", "coordinates": [-96.7970, 32.7767]}')
        """)
        )
        test_session.commit()

        response = test_client.get("/school_of_study_data/ETMS")

        assert response.status_code == 200
        data = response.json()

        feature = data["features"][0]
        props = feature["properties"]

        # Verify NULL values are handled
        assert props["openings_2024_zscore"] is None
        assert props["jobs_2024_zscore"] is None
        assert props["openings_2024_zscore_color"] is None
        assert props["geoid"] == "48113020100"  # Non-null values still present
        assert props["category"] == "ETMS"

    @pytest.mark.parametrize(
        "category", ["BHGT", "CAED", "CE", "EDU", "ETMS", "HS", "LPS", "MIT"]
    )
    def test_school_of_study_data_all_valid_categories(
        self, test_client, setup_school_data, category
    ):
        """Test each valid school category individually."""
        response = test_client.get(f"/school_of_study_data/{category}")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/geo+json"

        data = response.json()
        assert data["type"] == "FeatureCollection"
        assert len(data["features"]) == 1
        assert data["features"][0]["properties"]["category"] == category

    def test_school_of_study_data_case_sensitivity(
        self, test_client, setup_school_data
    ):
        """Test that category parameter is case sensitive."""
        # Test lowercase
        response = test_client.get("/school_of_study_data/etms")
        assert response.status_code == 404

        # Test uppercase (should work)
        response = test_client.get("/school_of_study_data/ETMS")
        assert response.status_code == 200

    def test_school_of_study_data_special_characters(
        self, test_client, setup_school_data
    ):
        """Test endpoint with special characters in category."""
        # Test with URL-encoded characters
        response = test_client.get("/school_of_study_data/ET%20MS")
        assert response.status_code == 404

        # Test with invalid characters
        response = test_client.get("/school_of_study_data/ET@MS")
        assert response.status_code == 404

    def test_school_of_study_data_response_headers(
        self, test_client, setup_school_data
    ):
        """Test that response headers are set correctly."""
        response = test_client.get("/school_of_study_data/ETMS")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/geo+json"
        assert response.headers["content-disposition"] == "inline"

    def test_school_of_study_data_large_dataset(self, test_client, test_session):
        """Test endpoint with large number of features for one category."""
        # Insert 50 features for ETMS category
        for i in range(50):
            test_session.execute(
                text("""
                INSERT INTO school_of_lvl_data
                (geoid, category, openings_2024_zscore, jobs_2024_zscore, openings_2024_zscore_color, geom)
                VALUES
                (:geoid, 'ETMS', :zscore, :jobs_zscore, '#FF0000', '{"type": "Point", "coordinates": [' || :lng || ', ' || :lat || ']}')
            """),
                {
                    "geoid": f"48113{i:06d}",
                    "zscore": 1.5 + i * 0.1,
                    "jobs_zscore": 0.8 - i * 0.05,
                    "lng": -96.7970 + i * 0.001,
                    "lat": 32.7767 + i * 0.001,
                },
            )
        test_session.commit()

        response = test_client.get("/school_of_study_data/ETMS")

        assert response.status_code == 200
        data = response.json()
        assert len(data["features"]) == 50

        # Verify all features have unique geoids
        geoids = [f["properties"]["geoid"] for f in data["features"]]
        assert len(set(geoids)) == 50
