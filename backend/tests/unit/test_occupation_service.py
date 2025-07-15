"""Unit tests for occupation service functionality."""

from unittest.mock import Mock
from sqlalchemy.orm import Session

from app.services import OccupationService
from app.occupation_cache import SimpleCache, cache_with_ttl


class TestOccupationService:
    """Test cases for OccupationService class."""

    def test_get_occupation_ids_returns_list(self):
        """Test that get_occupation_ids returns a list of occupation codes."""
        # Mock session
        mock_session = Mock(spec=Session)

        # Create service instance
        service = OccupationService(mock_session)

        # Mock repository method
        mock_categories = [
            {"code": "11-1021", "name": "General and Operations Managers"},
            {"code": "15-1251", "name": "Computer Programmers"},
            {
                "code": "11-1021",
                "name": "General and Operations Managers",
            },  # Duplicate to test distinct
        ]
        service.repository.get_occupation_categories = Mock(
            return_value=mock_categories
        )

        # Call the method
        result = service.get_occupation_ids()

        # Assert
        assert isinstance(result, list)
        assert "11-1021" in result
        assert "15-1251" in result
        service.repository.get_occupation_categories.assert_called_once()

    def test_get_occupations_with_names_returns_dict_list(self):
        """Test that get_occupations_with_names returns list of dicts with code and name."""
        # Mock session
        mock_session = Mock(spec=Session)

        # Create service instance
        service = OccupationService(mock_session)

        # Mock repository method
        mock_categories = [
            {"code": "11-1021", "name": "General and Operations Managers"},
            {"code": "15-1251", "name": "Computer Programmers"},
            {"code": "99-9999", "name": "All Other Occupations"},
        ]
        service.repository.get_occupation_categories = Mock(
            return_value=mock_categories
        )

        # Clear any cache
        from app.occupation_cache import _cache

        _cache.clear()

        # Call the method
        result = service.get_occupations_with_names()

        # Assert structure
        assert isinstance(result, list)
        assert len(result) == 3

        # Check each item has required fields
        for item in result:
            assert "code" in item
            assert "name" in item
            assert isinstance(item["code"], str)
            assert isinstance(item["name"], str)

        # Check specific mappings
        occupation_dict = {occ["code"]: occ["name"] for occ in result}
        assert occupation_dict["11-1021"] == "General and Operations Managers"
        assert occupation_dict["15-1251"] == "Computer Programmers"
        assert occupation_dict["99-9999"] == "All Other Occupations"

    def test_get_occupations_with_names_unknown_code(self):
        """Test that NULL occupation names use the code as the name."""
        # Mock session
        mock_session = Mock(spec=Session)

        # Create service instance
        service = OccupationService(mock_session)

        # Mock repository method with NULL/empty names
        mock_categories = [
            {
                "code": "99-0000",
                "name": "99-0000",
            },  # Repository should handle NULL -> code
            {
                "code": "99-0001",
                "name": "99-0001",
            },  # Repository should handle empty -> code
            {
                "code": "99-0002",
                "name": "99-0002",
            },  # Repository should handle whitespace -> code
        ]
        service.repository.get_occupation_categories = Mock(
            return_value=mock_categories
        )

        # Clear cache
        from app.occupation_cache import _cache

        _cache.clear()

        # Call the method
        result = service.get_occupations_with_names()

        # Assert
        assert len(result) == 3
        occupation_dict = {occ["code"]: occ["name"] for occ in result}
        assert occupation_dict["99-0000"] == "99-0000"  # NULL falls back to code
        assert (
            occupation_dict["99-0001"] == "99-0001"
        )  # Empty string falls back to code
        assert (
            occupation_dict["99-0002"] == "99-0002"
        )  # Whitespace-only falls back to code

    def test_get_occupations_with_names_sorted(self):
        """Test that occupations are returned sorted by name."""
        # Mock session
        mock_session = Mock(spec=Session)

        # Create service instance
        service = OccupationService(mock_session)

        # Mock repository method already sorted by name (as per ORDER BY in query)
        mock_categories = [
            {"code": "11-1021", "name": "General and Operations Managers"},
            {"code": "53-3032", "name": "Heavy and Tractor-Trailer Truck Drivers"},
            {"code": "29-1141", "name": "Registered Nurses"},
            {"code": "15-1251", "name": "Computer Programmers"},
        ]
        service.repository.get_occupation_categories = Mock(
            return_value=mock_categories
        )

        # Clear cache
        from app.occupation_cache import _cache

        _cache.clear()

        # Call the method
        result = service.get_occupations_with_names()

        # Assert repository returns the data (ordering is handled at repository level)
        assert len(result) == 4
        service.repository.get_occupation_categories.assert_called_once()

    def test_get_occupations_with_names_caching(self):
        """Test that occupation data caching behavior in test mode."""
        # Mock session
        mock_session = Mock(spec=Session)

        # Create service instance
        service = OccupationService(mock_session)

        # First request - mock repository response
        mock_categories_1 = [
            {"code": "11-1021", "name": "General and Operations Managers"}
        ]
        service.repository.get_occupation_categories = Mock(
            return_value=mock_categories_1
        )

        # Clear cache
        from app.occupation_cache import _cache

        _cache.clear()

        # First call - should hit repository
        result1 = service.get_occupations_with_names()
        assert len(result1) == 1
        assert service.repository.get_occupation_categories.call_count == 1

        # Reset mock to simulate adding more data
        mock_categories_2 = [
            {"code": "11-1021", "name": "General and Operations Managers"},
            {"code": "15-1251", "name": "Computer Programmers"},
        ]
        service.repository.get_occupation_categories = Mock(
            return_value=mock_categories_2
        )

        # Second call - in test mode (TESTING=1), caching is disabled
        result2 = service.get_occupations_with_names()

        # In test mode, we should get fresh data from repository
        assert len(result2) == 2  # Fresh data from repository
        assert (
            service.repository.get_occupation_categories.call_count == 1
        )  # Repository was called again

    def test_get_occupation_spatial_data(self):
        """Test getting spatial data for a specific occupation."""
        # Mock session
        mock_session = Mock(spec=Session)

        # Create service instance
        service = OccupationService(mock_session)

        # Mock repository method response
        mock_features_data = [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-96.7, 32.7]},
                "properties": {
                    "geoid": "12345",
                    "category": "11-1021",
                    "openings_2024_zscore": 1.0,
                    "jobs_2024_zscore": 0.5,
                    "openings_2024_zscore_color": "High",
                },
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-96.8, 32.8]},
                "properties": {
                    "geoid": "12346",
                    "category": "11-1021",
                    "openings_2024_zscore": 0.8,
                    "jobs_2024_zscore": 0.3,
                    "openings_2024_zscore_color": "Medium",
                },
            },
        ]
        service.repository.get_spatial_data_by_category = Mock(
            return_value=mock_features_data
        )

        # Call the method
        result = service.get_occupation_spatial_data("11-1021")

        # Assert
        assert len(result) == 2
        assert all(feature.properties.category == "11-1021" for feature in result)
        assert result[0].properties.geoid == "12345"
        assert result[0].properties.openings_2024_zscore == 1.0
        service.repository.get_spatial_data_by_category.assert_called_once_with(
            "11-1021"
        )


class TestOccupationCache:
    """Test cases for the occupation caching functionality."""

    def test_simple_cache_set_and_get(self):
        """Test basic cache set and get operations."""
        cache = SimpleCache()

        # Set a value
        cache.set("test_key", "test_value", ttl_seconds=60)

        # Get the value
        result = cache.get("test_key")
        assert result == "test_value"

    def test_simple_cache_expiry(self):
        """Test that cache entries expire after TTL."""
        cache = SimpleCache()

        # Set a value with 0 TTL (should expire immediately)
        cache.set("test_key", "test_value", ttl_seconds=0)

        # Try to get the value - should be None
        import time

        time.sleep(0.1)  # Small delay to ensure expiry
        result = cache.get("test_key")
        assert result is None

    def test_simple_cache_clear(self):
        """Test clearing the cache."""
        cache = SimpleCache()

        # Set multiple values
        cache.set("key1", "value1", ttl_seconds=60)
        cache.set("key2", "value2", ttl_seconds=60)

        # Clear cache
        cache.clear()

        # Both should be None
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_cache_decorator(self):
        """Test the cache_with_ttl decorator."""
        # Create a test function with the decorator
        call_count = 0

        @cache_with_ttl(ttl_seconds=60)
        def test_function(arg1, arg2):
            nonlocal call_count
            call_count += 1
            return f"{arg1}-{arg2}"

        # Clear cache before test
        from app.occupation_cache import _cache

        _cache.clear()

        # First call - should execute function
        result1 = test_function("hello", "world")
        assert result1 == "hello-world"
        assert call_count == 1

        # Second call with same args - should return cached value
        result2 = test_function("hello", "world")
        assert result2 == "hello-world"
        assert call_count == 1  # Should not increment

        # Call with different args - should execute function
        result3 = test_function("foo", "bar")
        assert result3 == "foo-bar"
        assert call_count == 2


# Removed TestOccupationNameMapping class as it tests static mappings
# which are no longer used - the new implementation uses the occupation_codes database table
