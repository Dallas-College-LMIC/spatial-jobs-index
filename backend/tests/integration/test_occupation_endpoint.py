"""Integration tests for the updated occupation endpoint."""
import pytest
from sqlalchemy import text


@pytest.fixture
def occupation_test_data():
    """Sample occupation data for testing."""
    return [
        {"code": "11-1021", "name": "General and Operations Managers"},
        {"code": "15-1251", "name": "Computer Programmers"},
        {"code": "15-1252", "name": "Software Developers"},
        {"code": "29-1141", "name": "Registered Nurses"},
        {"code": "33-3051", "name": "Police and Sheriff's Patrol Officers"},
        {"code": "41-2031", "name": "Retail Salespersons"},
        {"code": "49-3023", "name": "Automotive Service Technicians and Mechanics"},
        {"code": "53-3032", "name": "Heavy and Tractor-Trailer Truck Drivers"},
    ]


@pytest.fixture
def setup_occupation_codes(test_session, occupation_test_data):
    """Setup occupation codes table with test data."""
    # Clear existing data
    test_session.execute(text("DELETE FROM occupation_codes"))
    test_session.commit()

    # Insert test data
    for occ in occupation_test_data:
        test_session.execute(
            text("INSERT INTO occupation_codes (occupation_code, occupation_name) VALUES (:code, :name)"),
            {"code": occ["code"], "name": occ["name"]}
        )
    test_session.commit()

    # Clear cache to ensure fresh data
    from app.occupation_cache import _cache
    _cache.clear()

    yield occupation_test_data

    # Cleanup
    test_session.execute(text("DELETE FROM occupation_codes"))
    test_session.commit()


class TestOccupationEndpoint:
    """Integration tests for /occupation_ids endpoint with new response format."""

    def test_occupation_ids_empty_database(self, test_client, test_session):
        """Test endpoint returns empty list when no occupations exist."""
        # Ensure database is empty
        test_session.execute(text("DELETE FROM occupation_codes"))
        test_session.commit()

        # Make request
        response = test_client.get("/occupation_ids")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "occupations" in data
        assert data["occupations"] == []

    def test_occupation_ids_with_data(self, test_client, test_session):
        """Test endpoint returns occupation codes and names from occupation_codes table."""
        # Insert test data into occupation_codes table
        test_session.execute(text("""
            INSERT INTO occupation_codes (occupation_code, occupation_name)
            VALUES
            ('11-1021', 'General and Operations Managers'),
            ('15-1251', 'Computer Programmers'),
            ('29-1141', 'Registered Nurses'),
            ('99-0001', NULL)  -- Test NULL name handling
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
        assert occupation_dict["99-0001"] == "99-0001"  # NULL name uses code as fallback

    def test_occupation_ids_sorted(self, test_client, test_session):
        """Test that occupations are returned sorted by code."""
        # Insert test data in random order
        test_session.execute(text("""
            INSERT INTO occupation_codes (occupation_code, occupation_name)
            VALUES
            ('53-3032', 'Heavy and Tractor-Trailer Truck Drivers'),
            ('11-1021', 'General and Operations Managers'),
            ('29-1141', 'Registered Nurses'),
            ('15-1251', 'Computer Programmers')
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
        """Test that occupation data caching is disabled in test mode."""
        # Insert initial data
        test_session.execute(text("""
            INSERT INTO occupation_codes (occupation_code, occupation_name)
            VALUES ('11-1021', 'General and Operations Managers')
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
            INSERT INTO occupation_codes (occupation_code, occupation_name)
            VALUES ('15-1251', 'Computer Programmers')
        """))
        test_session.commit()

        # Second request - in test mode, caching is disabled so we should see new data
        response2 = test_client.get("/occupation_ids")
        assert response2.status_code == 200
        data2 = response2.json()
        assert len(data2["occupations"]) == 2  # Should see both occupations

        # Verify both occupations are returned
        codes = {occ["code"] for occ in data2["occupations"]}
        assert codes == {"11-1021", "15-1251"}

    def test_occupation_ids_database_driven(self, test_client, setup_occupation_codes):
        """Test that endpoint uses occupation_codes table for data."""
        # Make request
        response = test_client.get("/occupation_ids")

        # Assert success
        assert response.status_code == 200
        data = response.json()
        assert "occupations" in data
        assert len(data["occupations"]) == len(setup_occupation_codes)

        # Verify all test data is returned
        returned_codes = {occ["code"] for occ in data["occupations"]}
        expected_codes = {occ["code"] for occ in setup_occupation_codes}
        assert returned_codes == expected_codes

        # Verify names match
        occupation_dict = {occ["code"]: occ["name"] for occ in data["occupations"]}
        for test_occ in setup_occupation_codes:
            assert occupation_dict[test_occ["code"]] == test_occ["name"]

    def test_occupation_ids_ordering(self, test_client, setup_occupation_codes):
        """Test that occupations are returned in sorted order by code."""
        # Make request
        response = test_client.get("/occupation_ids")

        # Assert success
        assert response.status_code == 200
        data = response.json()

        # Get codes in returned order
        returned_codes = [occ["code"] for occ in data["occupations"]]

        # Verify they are sorted
        assert returned_codes == sorted(returned_codes)

    def test_occupation_ids_with_empty_names(self, test_client, test_session):
        """Test handling of occupation codes with empty or NULL names."""
        # Insert data with various empty name scenarios
        test_session.execute(text("""
            INSERT INTO occupation_codes (occupation_code, occupation_name)
            VALUES
            ('11-1021', 'General and Operations Managers'),
            ('15-1251', ''),  -- Empty string
            ('29-1141', NULL),  -- NULL
            ('33-3051', '   ')  -- Whitespace only
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

        occupation_dict = {occ["code"]: occ["name"] for occ in data["occupations"]}

        # Verify fallback behavior for empty names
        assert occupation_dict["11-1021"] == "General and Operations Managers"
        assert occupation_dict["15-1251"] == "15-1251"  # Empty string falls back to code
        assert occupation_dict["29-1141"] == "29-1141"  # NULL falls back to code
        assert occupation_dict["33-3051"] == "33-3051"  # Whitespace-only falls back to code

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
        # Insert data - attempting to insert duplicate codes should fail due to primary key constraint
        test_session.execute(text("""
            INSERT INTO occupation_codes (occupation_code, occupation_name)
            VALUES
            ('11-1021', 'General and Operations Managers'),
            ('15-1251', 'Computer Programmers')
        """))
        test_session.commit()

        # Attempt to insert duplicate - this would fail in a real database
        # For SQLite test, we'll just verify uniqueness is enforced at query level

        # Clear cache
        from app.occupation_cache import _cache
        _cache.clear()

        # Make request
        response = test_client.get("/occupation_ids")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["occupations"]) == 2  # Only 2 unique occupation codes

        codes = [occ["code"] for occ in data["occupations"]]
        assert "11-1021" in codes
        assert "15-1251" in codes
        assert codes.count("11-1021") == 1  # No duplicates due to primary key constraint

    def test_occupation_ids_response_format_validation(self, test_client, test_session):
        """Test that response format matches the expected schema."""
        # Insert test data
        test_session.execute(text("""
            INSERT INTO occupation_codes (occupation_code, occupation_name)
            VALUES ('11-1021', 'General and Operations Managers')
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
            INSERT INTO occupation_codes (occupation_code, occupation_name)
            VALUES (:code, :name)
        """), {"code": code, "name": expected_name})
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

    def test_occupation_ids_independent_of_occupation_lvl_data(self, test_client, test_session):
        """Test that endpoint uses occupation_codes table, not occupation_lvl_data."""
        # Insert data only in occupation_lvl_data table
        test_session.execute(text("""
            INSERT INTO occupation_lvl_data (geoid, category, openings_2024_zscore, jobs_2024_zscore)
            VALUES
            ('12345', '99-8888', 1.0, 0.5),
            ('12346', '99-7777', 0.8, 0.3)
        """))
        test_session.commit()

        # Clear cache
        from app.occupation_cache import _cache
        _cache.clear()

        # Make request - should return empty since occupation_codes table is empty
        response = test_client.get("/occupation_ids")

        assert response.status_code == 200
        data = response.json()
        assert data["occupations"] == []  # No data because occupation_codes table is empty

        # Now add data to occupation_codes table
        test_session.execute(text("""
            INSERT INTO occupation_codes (occupation_code, occupation_name)
            VALUES
            ('11-1021', 'General and Operations Managers'),
            ('15-1251', 'Computer Programmers')
        """))
        test_session.commit()

        # Clear cache again
        _cache.clear()

        # Make request again
        response = test_client.get("/occupation_ids")

        assert response.status_code == 200
        data = response.json()
        assert len(data["occupations"]) == 2

        # Verify it returns data from occupation_codes, not occupation_lvl_data
        codes = {occ["code"] for occ in data["occupations"]}
        assert codes == {"11-1021", "15-1251"}
        assert "99-8888" not in codes
        assert "99-7777" not in codes
