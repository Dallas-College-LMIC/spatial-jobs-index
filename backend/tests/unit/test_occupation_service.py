"""Unit tests for occupation service functionality."""
from unittest.mock import Mock
from sqlalchemy.orm import Session

from app.services import OccupationService
from app.occupation_cache import SimpleCache, cache_with_ttl, OCCUPATION_NAMES


class TestOccupationService:
    """Test cases for OccupationService class."""
    
    def test_get_occupation_ids_returns_list(self):
        """Test that get_occupation_ids returns a list of occupation codes."""
        # Mock session and result
        mock_session = Mock(spec=Session)
        mock_result = Mock()
        mock_result.fetchall.return_value = [
            ('11-1021',),
            ('15-1251',),
            ('11-1021',)  # Duplicate to test distinct
        ]
        mock_session.execute.return_value = mock_result
        
        # Call the method
        result = OccupationService.get_occupation_ids(mock_session)
        
        # Assert
        assert isinstance(result, list)
        assert '11-1021' in result
        assert '15-1251' in result
        mock_session.execute.assert_called_once()
    
    def test_get_occupations_with_names_returns_dict_list(self):
        """Test that get_occupations_with_names returns list of dicts with code and name."""
        # Mock session and result
        mock_session = Mock(spec=Session)
        mock_result = Mock()
        mock_result.fetchall.return_value = [
            ('11-1021',),
            ('15-1251',),
            ('99-9999',)
        ]
        mock_session.execute.return_value = mock_result
        
        # Clear any cache
        from app.occupation_cache import _cache
        _cache.clear()
        
        # Call the method
        result = OccupationService.get_occupations_with_names(mock_session)
        
        # Assert structure
        assert isinstance(result, list)
        assert len(result) == 3
        
        # Check each item has required fields
        for item in result:
            assert 'code' in item
            assert 'name' in item
            assert isinstance(item['code'], str)
            assert isinstance(item['name'], str)
        
        # Check specific mappings
        occupation_dict = {occ['code']: occ['name'] for occ in result}
        assert occupation_dict['11-1021'] == "General and Operations Managers"
        assert occupation_dict['15-1251'] == "Computer Programmers"
        assert occupation_dict['99-9999'] == "All Other Occupations"
    
    def test_get_occupations_with_names_unknown_code(self):
        """Test that unknown occupation codes use the code as the name."""
        # Mock session and result with unknown code
        mock_session = Mock(spec=Session)
        mock_result = Mock()
        mock_result.fetchall.return_value = [('99-0000',)]
        mock_session.execute.return_value = mock_result
        
        # Clear cache
        from app.occupation_cache import _cache
        _cache.clear()
        
        # Call the method
        result = OccupationService.get_occupations_with_names(mock_session)
        
        # Assert unknown code uses code as name
        assert len(result) == 1
        assert result[0]['code'] == '99-0000'
        assert result[0]['name'] == '99-0000'  # Should fallback to code
    
    def test_get_occupations_with_names_sorted(self):
        """Test that occupations are returned sorted by code."""
        # Mock session and result in random order
        mock_session = Mock(spec=Session)
        mock_result = Mock()
        mock_result.fetchall.return_value = [
            ('53-3032',),
            ('11-1021',),
            ('29-1141',)
        ]
        mock_session.execute.return_value = mock_result
        
        # Clear cache
        from app.occupation_cache import _cache
        _cache.clear()
        
        # Call the method
        result = OccupationService.get_occupations_with_names(mock_session)
        
        # Assert sorted by code
        codes = [occ['code'] for occ in result]
        assert codes == sorted(codes)
    
    def test_get_occupations_with_names_caching(self):
        """Test that occupation data is cached properly."""
        # Mock session and result
        mock_session = Mock(spec=Session)
        mock_result = Mock()
        mock_result.fetchall.return_value = [('11-1021',)]
        mock_session.execute.return_value = mock_result
        
        # Clear cache
        from app.occupation_cache import _cache
        _cache.clear()
        
        # First call - should hit database
        result1 = OccupationService.get_occupations_with_names(mock_session)
        assert len(result1) == 1
        assert mock_session.execute.call_count == 1
        
        # Reset mock to simulate adding more data
        mock_result.fetchall.return_value = [('11-1021',), ('15-1251',)]
        
        # Second call - should return cached data (still 1 item)
        result2 = OccupationService.get_occupations_with_names(mock_session)
        assert len(result2) == 1  # Should still be 1 due to cache
        assert result2 == result1
        # execute should still have been called only once due to caching
        assert mock_session.execute.call_count == 1
    
    def test_get_occupation_spatial_data(self):
        """Test getting spatial data for a specific occupation."""
        # Mock the query result
        mock_row1 = Mock()
        mock_row1.geoid = '12345'
        mock_row1.category = '11-1021'
        mock_row1.openings_2024_zscore = 1.0
        mock_row1.jobs_2024_zscore = 0.5
        mock_row1.openings_2024_zscore_color = 'High'
        mock_row1.geometry = '{"type": "Point", "coordinates": [-96.7, 32.7]}'
        
        mock_row2 = Mock()
        mock_row2.geoid = '12346'
        mock_row2.category = '11-1021'
        mock_row2.openings_2024_zscore = 0.8
        mock_row2.jobs_2024_zscore = 0.3
        mock_row2.openings_2024_zscore_color = 'Medium'
        mock_row2.geometry = '{"type": "Point", "coordinates": [-96.8, 32.8]}'
        
        # Mock session and result
        mock_session = Mock(spec=Session)
        mock_result = Mock()
        mock_result.fetchall.return_value = [mock_row1, mock_row2]
        mock_session.execute.return_value = mock_result
        
        # Call the method
        result = OccupationService.get_occupation_spatial_data(mock_session, '11-1021')
        
        # Assert
        assert len(result) == 2
        assert all(feature.properties.category == '11-1021' for feature in result)
        assert result[0].properties.geoid == '12345'
        assert result[0].properties.openings_2024_zscore == 1.0


class TestOccupationCache:
    """Test cases for the occupation caching functionality."""
    
    def test_simple_cache_set_and_get(self):
        """Test basic cache set and get operations."""
        cache = SimpleCache()
        
        # Set a value
        cache.set('test_key', 'test_value', ttl_seconds=60)
        
        # Get the value
        result = cache.get('test_key')
        assert result == 'test_value'
    
    def test_simple_cache_expiry(self):
        """Test that cache entries expire after TTL."""
        cache = SimpleCache()
        
        # Set a value with 0 TTL (should expire immediately)
        cache.set('test_key', 'test_value', ttl_seconds=0)
        
        # Try to get the value - should be None
        import time
        time.sleep(0.1)  # Small delay to ensure expiry
        result = cache.get('test_key')
        assert result is None
    
    def test_simple_cache_clear(self):
        """Test clearing the cache."""
        cache = SimpleCache()
        
        # Set multiple values
        cache.set('key1', 'value1', ttl_seconds=60)
        cache.set('key2', 'value2', ttl_seconds=60)
        
        # Clear cache
        cache.clear()
        
        # Both should be None
        assert cache.get('key1') is None
        assert cache.get('key2') is None
    
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


class TestOccupationNameMapping:
    """Test the static occupation name mappings."""
    
    def test_occupation_names_dict_structure(self):
        """Test that OCCUPATION_NAMES has the expected structure."""
        assert isinstance(OCCUPATION_NAMES, dict)
        assert len(OCCUPATION_NAMES) > 0
        
        # Check a few known entries
        assert OCCUPATION_NAMES.get('11-1021') == "General and Operations Managers"
        assert OCCUPATION_NAMES.get('15-1252') == "Software Developers"
        assert OCCUPATION_NAMES.get('29-1141') == "Registered Nurses"
    
    def test_all_occupation_codes_valid_format(self):
        """Test that all occupation codes follow the XX-XXXX format."""
        import re
        pattern = re.compile(r'^\d{2}-\d{4}$')
        
        for code in OCCUPATION_NAMES.keys():
            assert pattern.match(code), f"Invalid code format: {code}"
    
    def test_all_occupation_names_non_empty(self):
        """Test that all occupation names are non-empty strings."""
        for code, name in OCCUPATION_NAMES.items():
            assert isinstance(name, str)
            assert len(name) > 0, f"Empty name for code: {code}"