"""Integration tests for the updated occupation endpoint."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text


class TestOccupationEndpoint:
    """Integration tests for /occupation_ids endpoint with new response format."""
    
    def test_occupation_ids_empty_database(self, test_client, test_session):
        """Test endpoint returns empty list when no occupations exist."""
        # Ensure database is empty
        test_session.execute(text("DELETE FROM occupation_lvl_data"))
        test_session.commit()
        
        # Make request
        response = test_client.get("/occupation_ids")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "occupations" in data
        assert data["occupations"] == []
    
    def test_occupation_ids_with_data(self, test_client, test_session):
        """Test endpoint returns occupation codes and names."""
        # Insert test data
        test_session.execute(text("""
            INSERT INTO occupation_lvl_data (geoid, category, openings_2024_zscore, jobs_2024_zscore)
            VALUES 
            ('12345', '11-1021', 1.0, 0.5),
            ('12346', '15-1251', 0.8, 0.3),
            ('12347', '29-1141', 0.6, 0.2),
            ('12348', '99-0001', 0.4, 0.1)  -- Unknown code
        """))
        test_session.commit()
        
        # Clear cache to ensure fresh data
        from app.occupation_cache import _cache
        _cache.clear()
        
        # Make request
        response = test_client.get("/occupation_ids")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "occupations" in data
        assert len(data["occupations"]) == 4
        
        # Check structure
        for occupation in data["occupations"]:
            assert "code" in occupation
            assert "name" in occupation
            assert isinstance(occupation["code"], str)
            assert isinstance(occupation["name"], str)
        
        # Check specific mappings
        occupation_dict = {occ["code"]: occ["name"] for occ in data["occupations"]}
        assert occupation_dict["11-1021"] == "General and Operations Managers"
        assert occupation_dict["15-1251"] == "Computer Programmers"
        assert occupation_dict["29-1141"] == "Registered Nurses"
        assert occupation_dict["99-0001"] == "99-0001"  # Unknown code uses code as name
    
    def test_occupation_ids_sorted(self, test_client, test_session):
        """Test that occupations are returned sorted by code."""
        # Insert test data in random order
        test_session.execute(text("""
            INSERT INTO occupation_lvl_data (geoid, category, openings_2024_zscore, jobs_2024_zscore)
            VALUES 
            ('12345', '53-3032', 1.0, 0.5),
            ('12346', '11-1021', 0.8, 0.3),
            ('12347', '29-1141', 0.6, 0.2),
            ('12348', '15-1251', 0.4, 0.1)
        """))
        test_session.commit()
        
        # Clear cache
        from app.occupation_cache import _cache
        _cache.clear()
        
        # Make request
        response = test_client.get("/occupation_ids")
        
        # Assert sorted
        assert response.status_code == 200
        data = response.json()
        codes = [occ["code"] for occ in data["occupations"]]
        assert codes == sorted(codes)
    
    def test_occupation_ids_caching_behavior(self, test_client, test_session):
        """Test that occupation data is cached appropriately."""
        # Insert initial data
        test_session.execute(text("""
            INSERT INTO occupation_lvl_data (geoid, category, openings_2024_zscore, jobs_2024_zscore)
            VALUES ('12345', '11-1021', 1.0, 0.5)
        """))
        test_session.commit()
        
        # Clear cache
        from app.occupation_cache import _cache
        _cache.clear()
        
        # First request
        response1 = test_client.get("/occupation_ids")
        assert response1.status_code == 200
        data1 = response1.json()
        assert len(data1["occupations"]) == 1
        
        # Add more data
        test_session.execute(text("""
            INSERT INTO occupation_lvl_data (geoid, category, openings_2024_zscore, jobs_2024_zscore)
            VALUES ('12346', '15-1251', 0.8, 0.3)
        """))
        test_session.commit()
        
        # Second request - should return cached data
        response2 = test_client.get("/occupation_ids")
        assert response2.status_code == 200
        data2 = response2.json()
        assert len(data2["occupations"]) == 1  # Still 1 due to cache
        assert data2 == data1
    
    def test_occupation_ids_rate_limiting(self, test_client, test_session):
        """Test that rate limiting is applied to the endpoint."""
        # Clear cache
        from app.occupation_cache import _cache
        _cache.clear()
        
        # Make many requests quickly (rate limit is 30/minute)
        responses = []
        for _ in range(35):
            response = test_client.get("/occupation_ids")
            responses.append(response.status_code)
        
        # Some requests should be rate limited (429)
        assert 429 in responses
        # But first 30 should succeed
        assert responses[:30].count(200) == 30
    
    def test_occupation_ids_with_duplicates(self, test_client, test_session):
        """Test that duplicate occupation codes are handled correctly."""
        # Insert data with duplicate categories
        test_session.execute(text("""
            INSERT INTO occupation_lvl_data (geoid, category, openings_2024_zscore, jobs_2024_zscore)
            VALUES 
            ('12345', '11-1021', 1.0, 0.5),
            ('12346', '11-1021', 0.8, 0.3),  -- Same category
            ('12347', '15-1251', 0.6, 0.2)
        """))
        test_session.commit()
        
        # Clear cache
        from app.occupation_cache import _cache
        _cache.clear()
        
        # Make request
        response = test_client.get("/occupation_ids")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["occupations"]) == 2  # Only 2 unique categories
        
        codes = [occ["code"] for occ in data["occupations"]]
        assert "11-1021" in codes
        assert "15-1251" in codes
        assert codes.count("11-1021") == 1  # No duplicates
    
    def test_occupation_ids_response_format_validation(self, test_client, test_session):
        """Test that response format matches the expected schema."""
        # Insert test data
        test_session.execute(text("""
            INSERT INTO occupation_lvl_data (geoid, category, openings_2024_zscore, jobs_2024_zscore)
            VALUES ('12345', '11-1021', 1.0, 0.5)
        """))
        test_session.commit()
        
        # Clear cache
        from app.occupation_cache import _cache
        _cache.clear()
        
        # Make request
        response = test_client.get("/occupation_ids")
        
        # Validate response structure
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        data = response.json()
        assert isinstance(data, dict)
        assert "occupations" in data
        assert isinstance(data["occupations"], list)
        
        if data["occupations"]:
            occupation = data["occupations"][0]
            assert isinstance(occupation, dict)
            assert set(occupation.keys()) == {"code", "name"}
            assert isinstance(occupation["code"], str)
            assert isinstance(occupation["name"], str)
    
    @pytest.mark.parametrize("code,expected_name", [
        ("11-1021", "General and Operations Managers"),
        ("15-1252", "Software Developers"),
        ("29-1141", "Registered Nurses"),
        ("33-3051", "Police and Sheriff's Patrol Officers"),
        ("41-2031", "Retail Salespersons"),
        ("49-3023", "Automotive Service Technicians and Mechanics"),
        ("53-3032", "Heavy and Tractor-Trailer Truck Drivers"),
        ("99-9999", "All Other Occupations"),
    ])
    def test_occupation_name_mappings(self, test_client, test_session, code, expected_name):
        """Test specific occupation code to name mappings."""
        # Insert test data
        test_session.execute(text("""
            INSERT INTO occupation_lvl_data (geoid, category, openings_2024_zscore, jobs_2024_zscore)
            VALUES (:geoid, :category, :zscore1, :zscore2)
        """), {"geoid": "12345", "category": code, "zscore1": 1.0, "zscore2": 0.5})
        test_session.commit()
        
        # Clear cache
        from app.occupation_cache import _cache
        _cache.clear()
        
        # Make request
        response = test_client.get("/occupation_ids")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        occupation = next((occ for occ in data["occupations"] if occ["code"] == code), None)
        assert occupation is not None
        assert occupation["name"] == expected_name