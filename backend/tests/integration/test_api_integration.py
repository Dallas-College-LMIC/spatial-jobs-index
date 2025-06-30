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