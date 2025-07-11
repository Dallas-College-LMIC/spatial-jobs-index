"""
Example tests for API endpoints demonstrating test infrastructure usage.
"""
import pytest
from unittest.mock import patch

from app.services import OccupationService, SpatialService
from tests.factories import create_sample_occupation_data, create_sample_spatial_data


class TestOccupationEndpoints:
    """Example tests for occupation-related endpoints."""
    
    @pytest.mark.api
    def test_get_occupation_ids_with_mock(self, test_client):
        """Test /occupation_ids endpoint with mocked service."""
        # Mock the service method to avoid database issues with SQLite
        with patch.object(OccupationService, 'get_occupations_with_names') as mock_get_names:
            mock_get_names.return_value = [
                {"code": "31-0000", "name": "Healthcare Support"},
                {"code": "15-0000", "name": "Computer and Mathematical"},
                {"code": "25-0000", "name": "Education and Training"}
            ]
            
            response = test_client.get("/occupation_ids")
            
            assert response.status_code == 200
            data = response.json()
            assert "occupations" in data
            assert len(data["occupations"]) == 3
            assert any(occ["name"] == "Healthcare Support" for occ in data["occupations"])
    
    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires PostgreSQL with jsi_data schema")
    def test_get_occupation_ids_integration(self, test_client, test_session):
        """Integration test for /occupation_ids endpoint."""
        # This test would work with a real PostgreSQL database
        # Create test data
        create_sample_occupation_data(test_session, count=5)
        
        response = test_client.get("/occupation_ids")
        
        assert response.status_code == 200
        data = response.json()
        assert "occupation_ids" in data
        assert len(data["occupation_ids"]) == 5


class TestSpatialEndpoints:
    """Example tests for spatial data endpoints."""
    
    @pytest.mark.api
    def test_get_geojson_with_mock(self, test_client, mock_geojson_data):
        """Test /geojson endpoint with mocked service."""
        # Mock the service method
        from app.models import GeoJSONFeature, SpatialFeatureProperties
        with patch.object(SpatialService, 'get_geojson_features') as mock_get_features:
            # Create GeoJSONFeature objects from mock data
            features = []
            for feature in mock_geojson_data["features"]:
                geojson_feature = GeoJSONFeature(
                    geometry=feature["geometry"],
                    properties=SpatialFeatureProperties(
                        geoid=feature["properties"]["geoid"],
                        all_jobs_zscore=feature["properties"]["all_jobs_zscore"],
                        all_jobs_zscore_cat=feature["properties"]["all_jobs_zscore_cat"],
                        living_wage_zscore=feature["properties"]["living_wage_zscore"],
                        living_wage_zscore_cat=feature["properties"]["living_wage_zscore_cat"],
                        not_living_wage_zscore=feature["properties"]["not_living_wage_zscore"],
                        not_living_wage_zscore_cat=feature["properties"]["not_living_wage_zscore_cat"]
                    )
                )
                features.append(geojson_feature)
            
            mock_get_features.return_value = features
            
            response = test_client.get("/geojson")
            
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/geo+json"
            
            data = response.json()
            assert data["type"] == "FeatureCollection"
            assert "features" in data
            assert len(data["features"]) > 0
    
    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires PostgreSQL with PostGIS")
    def test_get_geojson_integration(self, test_client, test_session):
        """Integration test for /geojson endpoint."""
        # This test would work with a real PostgreSQL database with PostGIS
        # Create test spatial data
        create_sample_spatial_data(test_session, count=10)
        
        response = test_client.get("/geojson")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/geo+json"
        
        data = response.json()
        assert data["type"] == "FeatureCollection"
        assert len(data["features"]) == 10


class TestRateLimiting:
    """Example tests for rate limiting functionality."""
    
    @pytest.mark.api
    @pytest.mark.slow
    def test_rate_limiting(self, test_client):
        """Test that rate limiting works."""
        # Mock the service to avoid database calls
        with patch.object(OccupationService, 'get_occupation_ids') as mock_get_ids:
            mock_get_ids.return_value = ["Test Occupation"]
            
            # The rate limit is 30/minute, so 31 requests should trigger it
            responses = []
            for i in range(31):
                response = test_client.get("/occupation_ids")
                responses.append(response)
            
            # Check that we got rate limited
            rate_limited = any(r.status_code == 429 for r in responses)
            assert rate_limited, "Rate limiting should have been triggered"


class TestErrorHandling:
    """Example tests for error handling."""
    
    @pytest.mark.api
    def test_database_error_handling(self, test_client):
        """Test handling of database errors."""
        with patch.object(OccupationService, 'get_occupations_with_names') as mock_get_names:
            mock_get_names.side_effect = Exception("Database connection error")
            
            response = test_client.get("/occupation_ids")
            
            assert response.status_code == 500
            error_data = response.json()
            assert "detail" in error_data
            assert "Internal server error" in error_data["detail"]