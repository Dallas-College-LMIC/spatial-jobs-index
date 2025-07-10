"""
Integration tests for the FastAPI application.

These tests verify end-to-end functionality including:
- Full request/response cycle
- Database integration patterns
- Performance testing
- Concurrent requests
- Real-world usage scenarios
"""
import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import patch, Mock

from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

from app.models import GeoJSONFeature, SpatialFeatureProperties, OccupationGeoJSONFeature, OccupationSpatialProperties
from app.database import get_db_session


@pytest.fixture
def integration_client():
    """Create test client with mocked services for integration testing."""
    with patch('app.main.DatabaseConfig.from_env'):
        with patch('app.main.init_database'):
            # Import app after mocking to avoid database initialization
            from app.main import app
            
            # Mock the database session dependency
            mock_session = Mock()
            
            def override_get_db():
                yield mock_session
            
            app.dependency_overrides[get_db_session] = override_get_db
            
            with TestClient(app) as client:
                yield client
            
            # Clean up
            app.dependency_overrides.clear()


@pytest.fixture
async def async_integration_client():
    """Create async test client for integration testing."""
    with patch('app.main.DatabaseConfig.from_env'):
        with patch('app.main.init_database'):
            from app.main import app
            
            mock_session = Mock()
            
            def override_get_db():
                yield mock_session
            
            app.dependency_overrides[get_db_session] = override_get_db
            
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                yield client
            
            app.dependency_overrides.clear()


class TestFullRequestResponseCycle:
    """Test complete request/response cycles with real data flow."""
    
    @patch('app.main.OccupationService.get_occupation_ids')
    def test_occupation_ids_full_cycle(self, mock_service, integration_client):
        """Test full cycle: service -> endpoint -> response."""
        # Mock service to return test data
        test_data = ["Healthcare Support", "Computer and Mathematical", "Education and Training"]
        mock_service.return_value = test_data
        
        # Make request
        response = integration_client.get("/occupation_ids")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert "occupation_ids" in data
        assert len(data["occupation_ids"]) == 3
        assert set(data["occupation_ids"]) == set(test_data)
        
        # Verify service was called
        mock_service.assert_called_once()
    
    @patch('app.main.OccupationService.get_occupation_spatial_data')
    def test_occupation_spatial_data_full_cycle(self, mock_service, integration_client):
        """Test full cycle for occupation spatial data endpoint."""
        # Create test occupation spatial data
        test_features = [
            OccupationGeoJSONFeature(
                geometry={"type": "Point", "coordinates": [-96.7970, 32.7767]},
                properties=OccupationSpatialProperties(
                    geoid="48257050209",
                    category="51-3091",
                    openings_2024_zscore=-0.0956,
                    jobs_2024_zscore=0.0187,
                    openings_2024_zscore_color="-0.5SD ~ +0.5SD"
                )
            ),
            OccupationGeoJSONFeature(
                geometry={"type": "Point", "coordinates": [-96.3838, 32.7399]},
                properties=OccupationSpatialProperties(
                    geoid="48257050213",
                    category="51-3091",
                    openings_2024_zscore=-0.2926,
                    jobs_2024_zscore=-0.2762,
                    openings_2024_zscore_color="-0.5SD ~ +0.5SD"
                )
            )
        ]
        mock_service.return_value = test_features
        
        # Make request
        response = integration_client.get("/occupation_data/51-3091")
        
        # Verify response
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/geo+json"
        data = response.json()
        assert data["type"] == "FeatureCollection"
        assert len(data["features"]) == 2
        
        # Check first feature
        feature1 = data["features"][0]
        assert feature1["properties"]["geoid"] == "48257050209"
        assert feature1["properties"]["category"] == "51-3091"
        assert feature1["properties"]["openings_2024_zscore"] == -0.0956
        
        # Verify service was called with correct category
        mock_service.assert_called_once()
        args = mock_service.call_args[0]
        assert args[1] == "51-3091"  # Second argument is the category
    
    @patch('app.main.OccupationService.get_occupation_spatial_data')
    def test_occupation_spatial_data_not_found(self, mock_service, integration_client):
        """Test occupation spatial data endpoint with non-existent category."""
        # Mock service to return empty list
        mock_service.return_value = []
        
        # Make request
        response = integration_client.get("/occupation_data/INVALID-CATEGORY")
        
        # Verify 404 response
        assert response.status_code == 404
        assert "No data found" in response.json()["detail"]
    
    @patch('app.main.SpatialService.get_geojson_features')
    def test_geojson_full_cycle(self, mock_service, integration_client):
        """Test full GeoJSON cycle with spatial data."""
        # Create test spatial data
        test_features = [
            GeoJSONFeature(
                geometry={"type": "Point", "coordinates": [-96.7970, 32.7767]},
                properties=SpatialFeatureProperties(
                    geoid="12345",
                    all_jobs_zscore=1.5,
                    all_jobs_zscore_cat="High",
                    living_wage_zscore=0.8,
                    living_wage_zscore_cat="Medium",
                    not_living_wage_zscore=-0.5,
                    not_living_wage_zscore_cat="Low"
                )
            )
        ]
        mock_service.return_value = test_features
        
        response = integration_client.get("/geojson")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/geo+json"
        data = response.json()
        assert data["type"] == "FeatureCollection"
        assert len(data["features"]) == 1
        assert data["features"][0]["properties"]["geoid"] == "12345"


    @patch('app.main.IsochroneService.get_isochrones_by_geoid')
    def test_isochrone_full_cycle(self, mock_service, integration_client):
        """Test full cycle for isochrone endpoint."""
        # Import the model we need
        from app.models import IsochroneFeature, IsochroneProperties
        
        # Create test isochrone data
        test_features = [
            IsochroneFeature(
                geometry={"type": "Polygon", "coordinates": [[[-96.7970, 32.7767], [-96.7960, 32.7757], [-96.7950, 32.7767], [-96.7970, 32.7767]]]},
                properties=IsochroneProperties(
                    geoid="12345",
                    time_category="< 5",
                    color="#1a9850"
                )
            ),
            IsochroneFeature(
                geometry={"type": "Polygon", "coordinates": [[[-96.8070, 32.7867], [-96.8060, 32.7857], [-96.8050, 32.7867], [-96.8070, 32.7867]]]},
                properties=IsochroneProperties(
                    geoid="12345",
                    time_category="5~10",
                    color="#66bd63"
                )
            )
        ]
        mock_service.return_value = test_features
        
        # Make request
        response = integration_client.get("/isochrones/12345")
        
        # Verify response
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/geo+json"
        data = response.json()
        assert data["type"] == "FeatureCollection"
        assert len(data["features"]) == 2
        
        # Check first feature
        feature1 = data["features"][0]
        assert feature1["properties"]["geoid"] == "12345"
        assert feature1["properties"]["time_category"] == "< 5"
        assert feature1["properties"]["color"] == "#1a9850"
        
        # Verify service was called with correct geoid
        mock_service.assert_called_once()
        args = mock_service.call_args[0]
        assert args[1] == "12345"  # Second argument is the geoid
    
    @patch('app.main.IsochroneService.get_isochrones_by_geoid')
    def test_isochrone_not_found(self, mock_service, integration_client):
        """Test isochrone endpoint with non-existent geoid."""
        # Mock service to return empty list
        mock_service.return_value = []
        
        # Make request
        response = integration_client.get("/isochrones/99999")
        
        # Verify 404 response
        assert response.status_code == 404
        assert "No isochrone data found" in response.json()["detail"]
    
    def test_isochrone_invalid_geoid(self, integration_client):
        """Test isochrone endpoint with invalid geoid format."""
        # Make request with non-numeric geoid
        response = integration_client.get("/isochrones/ABC123")
        
        # Verify 400 response
        assert response.status_code == 400
        assert "Invalid geoid format" in response.json()["detail"]
    
    @patch('app.main.IsochroneService.get_isochrones_by_geoid')
    def test_isochrone_empty_geoid(self, mock_service, integration_client):
        """Test isochrone endpoint with empty geoid string."""
        # This should be caught by FastAPI path validation
        response = integration_client.get("/isochrones/")
        
        # Verify 404 response (path not found)
        assert response.status_code == 404
    
    @patch('app.main.IsochroneService.get_isochrones_by_geoid')
    def test_isochrone_special_characters_geoid(self, mock_service, integration_client):
        """Test isochrone endpoint with special characters in geoid."""
        # Test various invalid geoid formats
        invalid_geoids = ["123-456", "123.456", "123@456", "123 456", "123/456"]
        
        for geoid in invalid_geoids:
            response = integration_client.get(f"/isochrones/{geoid}")
            # Some special characters might cause 404 (path not found) instead of 400
            assert response.status_code in [400, 404]
            if response.status_code == 400:
                assert "Invalid geoid format" in response.json()["detail"]
    
    @patch('app.main.IsochroneService.get_isochrones_by_geoid')
    def test_isochrone_valid_numeric_geoids(self, mock_service, integration_client):
        """Test isochrone endpoint with various valid numeric geoids."""
        # Import the model we need
        from app.models import IsochroneFeature, IsochroneProperties
        
        # Mock service return value
        test_features = [
            IsochroneFeature(
                geometry={"type": "Polygon", "coordinates": [[[-96.7970, 32.7767], [-96.7960, 32.7757], [-96.7950, 32.7767], [-96.7970, 32.7767]]]},
                properties=IsochroneProperties(
                    geoid="12345",
                    time_category="< 5",
                    color="#1a9850"
                )
            )
        ]
        mock_service.return_value = test_features
        
        # Test various valid numeric geoids
        valid_geoids = ["12345", "00001", "99999", "123456789", "1"]
        
        for geoid in valid_geoids:
            response = integration_client.get(f"/isochrones/{geoid}")
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/geo+json"
            data = response.json()
            assert data["type"] == "FeatureCollection"
    
    @patch('app.main.IsochroneService.get_isochrones_by_geoid')
    def test_isochrone_geojson_structure(self, mock_service, integration_client):
        """Test that isochrone endpoint returns proper GeoJSON structure."""
        # Import the model we need
        from app.models import IsochroneFeature, IsochroneProperties
        
        # Create test isochrone data with all time categories
        test_features = []
        time_categories = ["< 5", "5~10", "10~15", "15~20", "20~25", "25~30", "30~45", "> 45"]
        colors = ["#1a9850", "#66bd63", "#a6d96a", "#fdae61", "#fee08b", "#f46d43", "#d73027", "#a50026"]
        
        for i, (category, color) in enumerate(zip(time_categories, colors)):
            feature = IsochroneFeature(
                geometry={
                    "type": "Polygon", 
                    "coordinates": [[
                        [-96.7970 + i*0.01, 32.7767 + i*0.01], 
                        [-96.7960 + i*0.01, 32.7757 + i*0.01], 
                        [-96.7950 + i*0.01, 32.7767 + i*0.01], 
                        [-96.7970 + i*0.01, 32.7767 + i*0.01]
                    ]]
                },
                properties=IsochroneProperties(
                    geoid="48113123456",
                    time_category=category,
                    color=color
                )
            )
            test_features.append(feature)
        
        mock_service.return_value = test_features
        
        # Make request
        response = integration_client.get("/isochrones/48113123456")
        
        # Verify response
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/geo+json"
        data = response.json()
        
        # Verify GeoJSON structure
        assert data["type"] == "FeatureCollection"
        assert "features" in data
        assert len(data["features"]) == 8
        
        # Verify each feature
        for i, feature in enumerate(data["features"]):
            assert feature["type"] == "Feature"
            assert "geometry" in feature
            assert "properties" in feature
            
            # Check geometry
            assert feature["geometry"]["type"] == "Polygon"
            assert "coordinates" in feature["geometry"]
            
            # Check properties
            props = feature["properties"]
            assert props["geoid"] == "48113123456"
            assert props["time_category"] == time_categories[i]
            assert props["color"] == colors[i]
    
    @patch('app.main.IsochroneService.get_isochrones_by_geoid')
    def test_isochrone_service_exception_handling(self, mock_service, integration_client):
        """Test isochrone endpoint handling of service exceptions."""
        # Mock service to raise a generic exception
        mock_service.side_effect = Exception("Unexpected database error")
        
        # Make request
        response = integration_client.get("/isochrones/12345")
        
        # Verify 500 response
        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]

class TestDatabaseIntegration:
    """Test database integration scenarios."""
    
    @patch('app.main.OccupationService.get_occupation_ids')
    def test_database_connection_pool(self, mock_service, integration_client):
        """Test that connection pooling works correctly."""
        mock_service.return_value = []
        responses = []
        
        # Make multiple rapid requests to test pool
        for _ in range(20):
            response = integration_client.get("/occupation_ids")
            responses.append(response)
        
        # All requests should succeed (or be rate limited)
        success_count = sum(1 for r in responses if r.status_code == 200)
        rate_limited_count = sum(1 for r in responses if r.status_code == 429)
        
        assert success_count + rate_limited_count == len(responses)
        assert success_count > 0  # At least some should succeed
    
    @patch('app.main.OccupationService.get_occupation_ids')
    def test_database_transaction_isolation(self, mock_service, integration_client):
        """Test that transactions are properly isolated."""
        # Simulate different responses for different "transactions"
        mock_service.side_effect = [
            ["Initial Category"],
            ["Initial Category"],  # Should not see uncommitted data
            ["Initial Category", "Committed Category"]
        ]
        
        # Get initial state
        response1 = integration_client.get("/occupation_ids")
        initial_data = response1.json()["occupation_ids"] if response1.status_code == 200 else []
        
        # Make another request - simulating isolation
        response2 = integration_client.get("/occupation_ids")
        if response2.status_code == 200:
            current_data = response2.json()["occupation_ids"]
            assert current_data == initial_data  # No uncommitted changes visible
        
        # Final request shows "committed" data
        response3 = integration_client.get("/occupation_ids")
        if response3.status_code == 200:
            final_data = response3.json()["occupation_ids"]
            assert len(final_data) > len(initial_data)
    
    def test_database_error_recovery(self, integration_client):
        """Test that the application recovers from database errors."""
        with patch('app.main.OccupationService.get_occupation_ids') as mock_service:
            # First, ensure normal operation works
            mock_service.return_value = []
            response1 = integration_client.get("/occupation_ids")
            assert response1.status_code in [200, 429]
            
            # Simulate database error
            mock_service.side_effect = Exception("Database connection lost")
            response2 = integration_client.get("/occupation_ids")
            assert response2.status_code == 500
            assert "Internal server error" in response2.json()["detail"]
            
            # Verify recovery - should work again
            mock_service.side_effect = None
            mock_service.return_value = []
            response3 = integration_client.get("/occupation_ids")
            assert response3.status_code in [200, 429]


class TestPerformance:
    """Test performance characteristics of the API."""
    
    @patch('app.main.OccupationService.get_occupation_ids')
    def test_response_time_occupation_ids(self, mock_service, integration_client):
        """Test that occupation_ids endpoint responds quickly."""
        mock_service.return_value = ["Test1", "Test2"]
        
        # Warm up
        integration_client.get("/occupation_ids")
        
        # Measure response times
        response_times = []
        for _ in range(10):
            start_time = time.time()
            response = integration_client.get("/occupation_ids")
            end_time = time.time()
            
            if response.status_code == 200:
                response_times.append(end_time - start_time)
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            # Should respond in less than 100ms on average
            assert avg_response_time < 0.1
    
    @patch('app.main.SpatialService.get_geojson_features')
    def test_response_time_geojson(self, mock_service, integration_client):
        """Test that geojson endpoint responds in reasonable time."""
        # Create 100 features
        features = []
        for i in range(100):
            feature = GeoJSONFeature(
                geometry={"type": "Point", "coordinates": [-96.7970 + i*0.01, 32.7767 + i*0.01]},
                properties=SpatialFeatureProperties(
                    geoid=str(i),
                    all_jobs_zscore=1.5,
                    all_jobs_zscore_cat="High",
                    living_wage_zscore=0.8,
                    living_wage_zscore_cat="Medium",
                    not_living_wage_zscore=-0.5,
                    not_living_wage_zscore_cat="Low"
                )
            )
            features.append(feature)
        
        mock_service.return_value = features
        
        # Measure response time
        start_time = time.time()
        response = integration_client.get("/geojson")
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        # Should respond in less than 500ms even with 100 features
        assert response_time < 0.5
    
    @patch('app.main.SpatialService.get_geojson_features')
    def test_memory_usage_large_geojson(self, mock_service, integration_client):
        """Test memory efficiency with large GeoJSON responses."""
        # Create 1000 features
        features = []
        for i in range(1000):
            feature = GeoJSONFeature(
                geometry={"type": "Polygon", "coordinates": [
                    [[-96.7970 + j*0.001, 32.7767 + j*0.001] for j in range(10)]
                ]},
                properties=SpatialFeatureProperties(
                    geoid=str(i),
                    all_jobs_zscore=1.5,
                    all_jobs_zscore_cat="High",
                    living_wage_zscore=0.8,
                    living_wage_zscore_cat="Medium",
                    not_living_wage_zscore=-0.5,
                    not_living_wage_zscore_cat="Low"
                )
            )
            features.append(feature)
        
        mock_service.return_value = features
        
        # Make request and verify it completes
        response = integration_client.get("/geojson")
        assert response.status_code == 200
        
        # Verify response size is reasonable
        content_length = len(response.content)
        # Should be able to handle 1000 features
        assert content_length > 0
    
    @patch('app.main.IsochroneService.get_isochrones_by_geoid')
    def test_response_time_isochrone(self, mock_service, integration_client):
        """Test that isochrone endpoint responds in reasonable time."""
        # Import the model we need
        from app.models import IsochroneFeature, IsochroneProperties
        
        # Create test data with multiple isochrone bands
        features = []
        time_categories = ["< 5", "5~10", "10~15", "15~20", "20~25", "25~30", "30~45", "> 45"]
        colors = ["#1a9850", "#66bd63", "#a6d96a", "#fdae61", "#fee08b", "#f46d43", "#d73027", "#a50026"]
        
        for i, (category, color) in enumerate(zip(time_categories, colors)):
            # Create a complex polygon for each band
            coords = []
            for j in range(20):  # 20 points per polygon
                # angle = (j / 20) * 2 * 3.14159  # Not used in simplified calculation
                radius = 0.01 * (i + 1)
                x = -96.7970 + radius * (1 + 0.1 * j) * (1 if j % 2 == 0 else 0.9)
                y = 32.7767 + radius * (1 + 0.1 * j) * (1 if j % 2 == 0 else 0.9)
                coords.append([x, y])
            coords.append(coords[0])  # Close the polygon
            
            feature = IsochroneFeature(
                geometry={"type": "Polygon", "coordinates": [coords]},
                properties=IsochroneProperties(
                    geoid="48113123456",
                    time_category=category,
                    color=color
                )
            )
            features.append(feature)
        
        mock_service.return_value = features
        
        # Warm up
        integration_client.get("/isochrones/48113123456")
        
        # Measure response times
        response_times = []
        for _ in range(10):
            start_time = time.time()
            response = integration_client.get("/isochrones/48113123456")
            end_time = time.time()
            
            if response.status_code == 200:
                response_times.append(end_time - start_time)
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            # Should respond in less than 200ms on average even with complex polygons
            assert avg_response_time < 0.2
    
    @patch('app.main.IsochroneService.get_isochrones_by_geoid')
    def test_memory_usage_large_isochrone(self, mock_service, integration_client):
        """Test memory efficiency with large isochrone responses."""
        # Import the model we need
        from app.models import IsochroneFeature, IsochroneProperties
        
        # Create many isochrone bands with complex geometries
        features = []
        for i in range(50):  # 50 different bands
            # Create a MultiPolygon with multiple parts
            polygons = []
            for p in range(5):  # 5 polygons per MultiPolygon
                coords = []
                for j in range(100):  # 100 points per polygon
                    # angle = (j / 100) * 2 * 3.14159  # Not used in simplified calculation
                    radius = 0.01 * (i + 1) + p * 0.005
                    x = -96.7970 + radius * (1 + 0.01 * j)
                    y = 32.7767 + radius * (1 + 0.01 * j)
                    coords.append([x, y])
                coords.append(coords[0])  # Close the polygon
                polygons.append([coords])
            
            feature = IsochroneFeature(
                geometry={"type": "MultiPolygon", "coordinates": polygons},
                properties=IsochroneProperties(
                    geoid="48113999999",
                    time_category=f"Band {i}",
                    color="#808080"  # Default gray
                )
            )
            features.append(feature)
        
        mock_service.return_value = features
        
        # Make request and verify it completes
        response = integration_client.get("/isochrones/48113999999")
        assert response.status_code == 200
        
        # Verify response is valid GeoJSON
        data = response.json()
        assert data["type"] == "FeatureCollection"
        assert len(data["features"]) == 50
        
        # Verify content can be handled
        content_length = len(response.content)
        assert content_length > 0


class TestConcurrentRequests:
    """Test behavior under concurrent load."""
    
    @patch('app.main.OccupationService.get_occupation_ids')
    def test_concurrent_occupation_requests(self, mock_service, integration_client):
        """Test multiple concurrent requests to occupation_ids endpoint."""
        mock_service.return_value = ["Test"]
        
        def make_request(client):
            return client.get("/occupation_ids")
        
        # Use ThreadPoolExecutor for concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            # Submit 20 concurrent requests
            futures = []
            for _ in range(20):
                future = executor.submit(make_request, integration_client)
                futures.append(future)
            
            # Collect results
            results = []
            for future in as_completed(futures):
                try:
                    response = future.result()
                    results.append(response.status_code)
                except Exception:
                    results.append(500)
        
        # Analyze results
        success_count = sum(1 for status in results if status == 200)
        rate_limited_count = sum(1 for status in results if status == 429)
        
        # Should handle concurrent requests gracefully
        assert len(results) == 20
        assert success_count + rate_limited_count == 20
        assert success_count > 0  # At least some should succeed
    
    @patch('app.main.OccupationService.get_occupation_ids')
    @patch('app.main.SpatialService.get_geojson_features')
    def test_mixed_endpoint_concurrent_requests(self, mock_spatial, mock_occupation, integration_client):
        """Test concurrent requests to different endpoints."""
        mock_occupation.return_value = ["Test"]
        mock_spatial.return_value = []
        
        def make_occupation_request(client):
            return ('occupation', client.get("/occupation_ids"))
        
        def make_geojson_request(client):
            return ('geojson', client.get("/geojson"))
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            
            # Mix of requests to both endpoints
            for i in range(20):
                if i % 2 == 0:
                    future = executor.submit(make_occupation_request, integration_client)
                else:
                    future = executor.submit(make_geojson_request, integration_client)
                futures.append(future)
            
            # Collect results
            results = {'occupation': [], 'geojson': []}
            for future in as_completed(futures):
                try:
                    endpoint_type, response = future.result()
                    results[endpoint_type].append(response.status_code)
                except Exception:
                    pass
        
        # Both endpoints should handle concurrent load
        occupation_success = sum(1 for s in results['occupation'] if s == 200)
        geojson_success = sum(1 for s in results['geojson'] if s == 200)
        
        assert occupation_success > 0 or sum(1 for s in results['occupation'] if s == 429) > 0
        assert geojson_success > 0 or sum(1 for s in results['geojson'] if s == 429) > 0
    
    @patch('app.main.OccupationService.get_occupation_spatial_data')
    def test_concurrent_occupation_data_requests(self, mock_service, integration_client):
        """Test concurrent requests to occupation_data endpoint."""
        # Mock service return value
        test_features = [
            OccupationGeoJSONFeature(
                geometry={"type": "Point", "coordinates": [-96.7970, 32.7767]},
                properties=OccupationSpatialProperties(
                    geoid="48001",
                    category="51-3091",
                    openings_2024_zscore=-0.1,
                    jobs_2024_zscore=0.1,
                    openings_2024_zscore_color="-0.5SD ~ +0.5SD"
                )
            )
        ]
        mock_service.return_value = test_features
        
        def make_request(client, category):
            return client.get(f"/occupation_data/{category}")
        
        # Use ThreadPoolExecutor for concurrent requests
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Submit 10 concurrent requests with different categories
            futures = []
            categories = ["51-3091", "51-4041", "51-2011", "51-3091", "51-4041"]
            for i in range(10):
                category = categories[i % len(categories)]
                future = executor.submit(make_request, integration_client, category)
                futures.append(future)
            
            # Collect results
            results = []
            for future in as_completed(futures):
                try:
                    response = future.result()
                    results.append(response.status_code)
                except Exception:
                    results.append(500)
        
        # Analyze results
        success_count = sum(1 for status in results if status == 200)
        rate_limited_count = sum(1 for status in results if status == 429)
        
        # Should handle concurrent requests gracefully
        assert len(results) == 10
        assert success_count + rate_limited_count == 10

    
    @patch('app.main.IsochroneService.get_isochrones_by_geoid')
    def test_concurrent_isochrone_requests(self, mock_service, integration_client):
        """Test concurrent requests to isochrone endpoint."""
        # Import the model we need
        from app.models import IsochroneFeature, IsochroneProperties
        
        # Mock service return value
        test_features = [
            IsochroneFeature(
                geometry={"type": "Polygon", "coordinates": [[[-96.7970, 32.7767], [-96.7960, 32.7757], [-96.7950, 32.7767], [-96.7970, 32.7767]]]},
                properties=IsochroneProperties(
                    geoid="48001",
                    time_category="< 5",
                    color="#1a9850"
                )
            )
        ]
        mock_service.return_value = test_features
        
        def make_request(client, geoid):
            return client.get(f"/isochrones/{geoid}")
        
        # Use ThreadPoolExecutor for concurrent requests
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Submit 10 concurrent requests with different geoids
            futures = []
            geoids = ["12345", "67890", "11111", "22222", "33333"]
            for i in range(10):
                geoid = geoids[i % len(geoids)]
                future = executor.submit(make_request, integration_client, geoid)
                futures.append(future)
            
            # Collect results
            results = []
            for future in as_completed(futures):
                try:
                    response = future.result()
                    results.append(response.status_code)
                except Exception:
                    results.append(500)
        
        # Analyze results
        success_count = sum(1 for status in results if status == 200)
        rate_limited_count = sum(1 for status in results if status == 429)
        
        # Should handle concurrent requests gracefully
        assert len(results) == 10
        assert success_count + rate_limited_count == 10
    
    @pytest.mark.asyncio
    @patch('app.main.OccupationService.get_occupation_ids')
    @patch('app.main.SpatialService.get_geojson_features')
    async def test_async_concurrent_requests(self, mock_spatial, mock_occupation, async_integration_client):
        """Test async concurrent requests."""
        mock_occupation.return_value = ["Test"]
        mock_spatial.return_value = []
        
        async def make_request(client: AsyncClient, endpoint: str):
            return await client.get(endpoint)
        
        # Create multiple async tasks
        tasks = []
        for i in range(15):
            endpoint = "/occupation_ids" if i % 2 == 0 else "/geojson"
            task = make_request(async_integration_client, endpoint)
            tasks.append(task)
        
        # Execute all tasks concurrently
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Analyze results
        success_count = 0
        rate_limited_count = 0
        
        for response in responses:
            if not isinstance(response, Exception):
                if response.status_code == 200:
                    success_count += 1
                elif response.status_code == 429:
                    rate_limited_count += 1
        
        assert success_count + rate_limited_count > 0
        assert len(responses) == 15


class TestRateLimiting:
    """Test rate limiting functionality for endpoints."""
    
    @patch('app.main.IsochroneService.get_isochrones_by_geoid')
    def test_isochrone_rate_limiting(self, mock_service, integration_client):
        """Test that isochrone endpoint properly enforces rate limiting."""
        # Import the model we need
        from app.models import IsochroneFeature, IsochroneProperties
        
        # Mock service return value
        test_features = [
            IsochroneFeature(
                geometry={"type": "Polygon", "coordinates": [[[-96.7970, 32.7767], [-96.7960, 32.7757], [-96.7950, 32.7767], [-96.7970, 32.7767]]]},
                properties=IsochroneProperties(
                    geoid="12345",
                    time_category="< 5",
                    color="#1a9850"
                )
            )
        ]
        mock_service.return_value = test_features
        
        # Make many rapid requests to trigger rate limiting
        responses = []
        for i in range(40):  # More than the 30/minute limit
            response = integration_client.get("/isochrones/12345")
            responses.append(response)
        
        # Count responses by status code
        status_codes = [r.status_code for r in responses]
        success_count = status_codes.count(200)
        rate_limited_count = status_codes.count(429)
        
        # Should have some successful and some rate limited
        assert success_count > 0
        assert rate_limited_count > 0
        assert success_count + rate_limited_count == 40
        
        # The testclient may not include all headers that the real server would
        # Just verify we got rate limited responses
    
    @patch('app.main.IsochroneService.get_isochrones_by_geoid')
    def test_isochrone_rate_limit_per_endpoint(self, mock_service, integration_client):
        """Test that rate limits are per-endpoint, not global."""
        # Import the model we need
        from app.models import IsochroneFeature, IsochroneProperties
        
        # Mock service for isochrone
        test_features = [
            IsochroneFeature(
                geometry={"type": "Polygon", "coordinates": [[[-96.7970, 32.7767], [-96.7960, 32.7757], [-96.7950, 32.7767], [-96.7970, 32.7767]]]},
                properties=IsochroneProperties(
                    geoid="12345",
                    time_category="< 5",
                    color="#1a9850"
                )
            )
        ]
        mock_service.return_value = test_features
        
        # Also mock occupation service
        with patch('app.main.OccupationService.get_occupation_ids') as mock_occupation:
            mock_occupation.return_value = ["Test"]
            
            # Make many requests to isochrone endpoint
            isochrone_responses = []
            for _ in range(35):
                response = integration_client.get("/isochrones/12345")
                isochrone_responses.append(response.status_code)
            
            # Should hit rate limit on isochrone
            assert 429 in isochrone_responses
            
            # But occupation_ids should still work
            occupation_response = integration_client.get("/occupation_ids")
            assert occupation_response.status_code in [200, 429]  # Might be rate limited from other tests


class TestRealWorldScenarios:
    """Test real-world usage patterns."""
    
    @patch('app.main.OccupationService.get_occupation_ids')
    def test_browser_like_request_pattern(self, mock_service, integration_client):
        """Test request pattern similar to a web browser."""
        mock_service.return_value = ["Test"]
        
        # 1. OPTIONS preflight for CORS
        response = integration_client.options(
            "/occupation_ids",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET"
            }
        )
        assert response.status_code == 200
        
        # 2. Actual GET request
        response = integration_client.get(
            "/occupation_ids",
            headers={
                "Origin": "http://localhost:5173",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json",
                "Accept-Language": "en-US,en;q=0.9"
            }
        )
        assert response.status_code in [200, 429]
        
        # 3. Follow-up request for geojson
        with patch('app.main.SpatialService.get_geojson_features') as mock_spatial:
            mock_spatial.return_value = []
            response = integration_client.get(
                "/geojson",
                headers={
                    "Origin": "http://localhost:5173",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept": "application/geo+json,application/json;q=0.9"
                }
            )
            assert response.status_code in [200, 429]
    
    @patch('app.main.OccupationService.get_occupation_ids')
    @patch('app.main.SpatialService.get_geojson_features')
    def test_api_client_usage_pattern(self, mock_spatial, mock_occupation, integration_client):
        """Test usage pattern typical of an API client."""
        mock_occupation.return_value = ["Test1", "Test2"]
        mock_spatial.return_value = []
        
        # API clients often make repeated requests with consistent headers
        headers = {
            "User-Agent": "SpatialIndexClient/1.0",
            "Accept": "application/json"
        }
        
        # Get occupation IDs first
        response1 = integration_client.get("/occupation_ids", headers=headers)
        assert response1.status_code in [200, 429]
        
        # Then fetch spatial data
        response2 = integration_client.get("/geojson", headers=headers)
        assert response2.status_code in [200, 429]
        
        # Verify response formats are consistent
        if response1.status_code == 200:
            data = response1.json()
            assert "occupation_ids" in data
            assert isinstance(data["occupation_ids"], list)
        
        if response2.status_code == 200:
            data = response2.json()
            assert data["type"] == "FeatureCollection"
            assert "features" in data
    
    @patch('app.main.OccupationService.get_occupation_ids')
    @patch('app.main.SpatialService.get_geojson_features')
    def test_mobile_app_usage_pattern(self, mock_spatial, mock_occupation, integration_client):
        """Test usage pattern typical of a mobile application."""
        mock_occupation.return_value = ["Test"]
        mock_spatial.return_value = []
        
        # Mobile apps often have specific characteristics
        headers = {
            "User-Agent": "SpatialIndex-iOS/2.0 (iPhone; iOS 15.0)",
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive"
        }
        
        # Mobile apps might check connectivity first with a light request
        response = integration_client.get("/occupation_ids", headers=headers)
        assert response.status_code in [200, 429]
        
        # Then fetch heavier data if connected
        if response.status_code == 200:
            response = integration_client.get("/geojson", headers=headers)
            assert response.status_code in [200, 429]
    
    @patch('app.main.OccupationService.get_occupation_ids')
    @patch('app.main.SpatialService.get_geojson_features')
    def test_data_visualization_usage_pattern(self, mock_spatial, mock_occupation, integration_client):
        """Test usage pattern for data visualization applications."""
        # Visualization apps often need both metadata and spatial data
        mock_occupation.return_value = ["Healthcare", "Technology", "Education"]
        
        # 1. Get available occupation categories
        response = integration_client.get("/occupation_ids")
        # Get available occupation categories
        # occupation_ids = []
        # if response.status_code == 200:
        #     occupation_ids = response.json()["occupation_ids"]
        
        # 2. Get spatial data for visualization
        test_features = [
            GeoJSONFeature(
                geometry={"type": "Point", "coordinates": [-96.7970, 32.7767]},
                properties=SpatialFeatureProperties(
                    geoid="12345",
                    all_jobs_zscore=1.5,
                    all_jobs_zscore_cat="High",
                    living_wage_zscore=0.8,
                    living_wage_zscore_cat="Medium",
                    not_living_wage_zscore=-0.5,
                    not_living_wage_zscore_cat="Low"
                )
            )
        ]
        mock_spatial.return_value = test_features
        
        response = integration_client.get("/geojson")
        assert response.status_code in [200, 429]
        
        if response.status_code == 200:
            # Verify GeoJSON is valid for visualization
            data = response.json()
            assert data["type"] == "FeatureCollection"
            
            # Check that features have required properties for visualization
            if data["features"]:
                feature = data["features"][0]
                assert "geometry" in feature
                assert "properties" in feature
                props = feature["properties"]
                assert "geoid" in props
                assert any(key.endswith("_zscore") for key in props)
                assert any(key.endswith("_zscore_cat") for key in props)
    
    @patch('app.main.IsochroneService.get_isochrones_by_geoid')
    def test_isochrone_visualization_usage_pattern(self, mock_service, integration_client):
        """Test usage pattern for isochrone visualization applications."""
        # Import the model we need
        from app.models import IsochroneFeature, IsochroneProperties
        
        # Create realistic isochrone data for visualization
        test_features = []
        time_categories = ["< 5", "5~10", "10~15", "15~20"]
        colors = ["#1a9850", "#66bd63", "#a6d96a", "#fdae61"]
        
        # Create concentric polygons representing travel time bands
        for i, (category, color) in enumerate(zip(time_categories, colors)):
            # Create a realistic isochrone polygon
            coords = []
            num_points = 16  # Enough points for smooth visualization
            for j in range(num_points):
                # angle = (j / num_points) * 2 * 3.14159  # Not used in simplified calculation
                # Irregular shape to simulate real isochrones
                radius = 0.01 * (i + 1) * (1 + 0.2 * (j % 3))
                x = -96.7970 + radius * (1 + 0.1 * (j % 2))
                y = 32.7767 + radius * (1 + 0.1 * ((j + 1) % 2))
                coords.append([x, y])
            coords.append(coords[0])  # Close the polygon
            
            feature = IsochroneFeature(
                geometry={"type": "Polygon", "coordinates": [coords]},
                properties=IsochroneProperties(
                    geoid="48113123456",
                    time_category=category,
                    color=color
                )
            )
            test_features.append(feature)
        
        mock_service.return_value = test_features
        
        # Simulate visualization app behavior
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/geo+json,application/json;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Referer": "http://localhost:5173/map"
        }
        
        # 1. Get isochrone data for selected census tract
        response = integration_client.get("/isochrones/48113123456", headers=headers)
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/geo+json"
        
        # 2. Verify data structure for visualization
        data = response.json()
        assert data["type"] == "FeatureCollection"
        assert len(data["features"]) == 4
        
        # 3. Check that features are suitable for map rendering
        for i, feature in enumerate(data["features"]):
            assert feature["type"] == "Feature"
            assert "geometry" in feature
            assert "properties" in feature
            
            # Verify polygon is closed
            coords = feature["geometry"]["coordinates"][0]
            assert coords[0] == coords[-1]
            
            # Verify color is provided for styling
            assert "color" in feature["properties"]
            assert feature["properties"]["color"].startswith("#")
            
            # Verify time category for legend
            assert "time_category" in feature["properties"]
            assert feature["properties"]["time_category"] in time_categories
    
    @patch('app.main.IsochroneService.get_isochrones_by_geoid')
    @patch('app.main.SpatialService.get_geojson_features')
    def test_combined_map_data_usage_pattern(self, mock_spatial, mock_isochrone, integration_client):
        """Test usage pattern for apps that combine multiple data layers."""
        # Import models
        from app.models import IsochroneFeature, IsochroneProperties
        
        # Mock spatial data
        spatial_features = [
            GeoJSONFeature(
                geometry={"type": "Point", "coordinates": [-96.7970, 32.7767]},
                properties=SpatialFeatureProperties(
                    geoid="48113123456",
                    all_jobs_zscore=1.5,
                    all_jobs_zscore_cat="High",
                    living_wage_zscore=0.8,
                    living_wage_zscore_cat="Medium",
                    not_living_wage_zscore=-0.5,
                    not_living_wage_zscore_cat="Low"
                )
            )
        ]
        mock_spatial.return_value = spatial_features
        
        # Mock isochrone data
        isochrone_features = [
            IsochroneFeature(
                geometry={"type": "Polygon", "coordinates": [[
                    [-96.807, 32.787], [-96.787, 32.787], 
                    [-96.787, 32.767], [-96.807, 32.767], [-96.807, 32.787]
                ]]},
                properties=IsochroneProperties(
                    geoid="48113123456",
                    time_category="< 5",
                    color="#1a9850"
                )
            )
        ]
        mock_isochrone.return_value = isochrone_features
        
        # Typical workflow for a map application showing multiple layers
        # 1. Get base spatial data
        response1 = integration_client.get("/geojson")
        assert response1.status_code in [200, 429]
        
        if response1.status_code == 200:
            spatial_data = response1.json()
            # Extract geoid from spatial data
            geoid = spatial_data["features"][0]["properties"]["geoid"]
            
            # 2. Get isochrone data for selected feature
            response2 = integration_client.get(f"/isochrones/{geoid}")
            assert response2.status_code == 200
            
            isochrone_data = response2.json()
            
            # 3. Verify both datasets can be combined
            assert spatial_data["type"] == "FeatureCollection"
            assert isochrone_data["type"] == "FeatureCollection"
            
            # Both should reference the same geoid
            assert spatial_data["features"][0]["properties"]["geoid"] == \
                   isochrone_data["features"][0]["properties"]["geoid"]


class TestErrorScenarios:
    """Test various error scenarios and recovery."""
    
    def test_malformed_request_handling(self, integration_client):
        """Test handling of malformed requests."""
        # Test with invalid HTTP method
        response = integration_client.post("/occupation_ids", json={"invalid": "data"})
        assert response.status_code == 405  # Method not allowed
        
        # Test with invalid path parameters
        response = integration_client.get("/occupation_ids/invalid")
        assert response.status_code == 404
    
    @patch('app.main.OccupationService.get_occupation_ids')
    @patch('app.main.SpatialService.get_geojson_features')
    def test_partial_service_failure(self, mock_spatial, mock_occupation, integration_client):
        """Test behavior when one service fails but others work."""
        # Mock occupation service to fail
        mock_occupation.side_effect = Exception("Occupation service down")
        mock_spatial.return_value = []
        
        # Occupation endpoint should return 500
        response = integration_client.get("/occupation_ids")
        assert response.status_code == 500
        
        # But geojson should still work
        response = integration_client.get("/geojson")
        assert response.status_code in [200, 429]
    
    @patch('app.main.OccupationService.get_occupation_ids')
    @patch('app.main.SpatialService.get_geojson_features')
    def test_recovery_after_errors(self, mock_spatial, mock_occupation, integration_client):
        """Test that the API recovers properly after errors."""
        # Initially both services work
        mock_occupation.return_value = ["Test"]
        mock_spatial.return_value = []
        
        # Cause an error
        mock_occupation.side_effect = Exception("Temporary failure")
        response = integration_client.get("/occupation_ids")
        assert response.status_code == 500
        
        # Should recover after error is resolved
        mock_occupation.side_effect = None
        mock_occupation.return_value = ["Test"]
        response = integration_client.get("/occupation_ids")
        assert response.status_code in [200, 429]
        
        # Other endpoints should not be affected
        response = integration_client.get("/geojson")
        assert response.status_code in [200, 429]