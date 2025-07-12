"""
Unit tests for the services module in app/services.py.

This module tests the business logic layer of the spatial jobs index API,
including OccupationService, SpatialService, and IsochroneService classes. Tests use mocking
to simulate database queries and focus on verifying business logic behavior.

Test coverage includes:
- OccupationService.get_occupation_ids() with various data scenarios
- SpatialService.get_geojson_features() with geometry handling and conversions
- IsochroneService.get_isochrones_by_geoid() with travel time bands and color mapping
- Error handling for database exceptions
- Edge cases like null values, empty results, and large datasets
"""
import pytest
from unittest.mock import Mock
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import json

from app.services import OccupationService, SpatialService, IsochroneService
from app.models import GeoJSONFeature, OccupationGeoJSONFeature, IsochroneFeature


class TestOccupationService:
    """Test cases for OccupationService"""

    def test_get_occupation_ids_empty_result(self):
        """Test get_occupation_ids with empty database result"""
        # Mock session and result
        mock_session = Mock(spec=Session)
        mock_result = Mock()
        mock_result.fetchall.return_value = []
        mock_session.execute.return_value = mock_result

        # Call service method
        result = OccupationService.get_occupation_ids(mock_session)

        # Assertions
        assert result == []
        mock_session.execute.assert_called_once()
        mock_result.fetchall.assert_called_once()

    def test_get_occupation_ids_single_result(self):
        """Test get_occupation_ids with single occupation category"""
        # Mock session and result
        mock_session = Mock(spec=Session)
        mock_result = Mock()
        mock_result.fetchall.return_value = [("Healthcare",)]
        mock_session.execute.return_value = mock_result

        # Call service method
        result = OccupationService.get_occupation_ids(mock_session)

        # Assertions
        assert result == ["Healthcare"]
        mock_session.execute.assert_called_once()
        mock_result.fetchall.assert_called_once()

    def test_get_occupation_ids_multiple_results(self):
        """Test get_occupation_ids with multiple occupation categories"""
        # Mock session and result
        mock_session = Mock(spec=Session)
        mock_result = Mock()
        mock_result.fetchall.return_value = [
            ("Healthcare",),
            ("Technology",),
            ("Education",),
            ("Manufacturing",)
        ]
        mock_session.execute.return_value = mock_result

        # Call service method
        result = OccupationService.get_occupation_ids(mock_session)

        # Assertions
        assert result == ["Healthcare", "Technology", "Education", "Manufacturing"]
        assert len(result) == 4
        mock_session.execute.assert_called_once()
        mock_result.fetchall.assert_called_once()

    def test_get_occupation_ids_database_error(self):
        """Test get_occupation_ids handling database errors"""
        # Mock session to raise SQLAlchemyError
        mock_session = Mock(spec=Session)
        mock_session.execute.side_effect = SQLAlchemyError("Database connection error")

        # Call service method and expect exception
        with pytest.raises(SQLAlchemyError) as exc_info:
            OccupationService.get_occupation_ids(mock_session)

        assert "Database connection error" in str(exc_info.value)
        mock_session.execute.assert_called_once()

    def test_get_occupations_with_names_queries_occupation_codes_table(self):
        """Test get_occupations_with_names queries occupation_codes table directly"""
        # Mock session
        mock_session = Mock(spec=Session)

        # Mock result returns tuples of (occupation_code, occupation_name) from occupation_codes table
        mock_result = Mock()
        mock_result.fetchall.return_value = [
            ("11-1021", "General and Operations Managers"),
            ("15-1251", "Computer Programmers"),
            ("29-1141", "Registered Nurses"),
            ("99-9999", "Unknown Occupation")  # All codes should have names in occupation_codes table
        ]

        mock_session.execute.return_value = mock_result

        # Call service method
        result = OccupationService.get_occupations_with_names(mock_session)

        # Assertions
        assert len(result) == 4
        assert mock_session.execute.call_count == 1  # Only one query now

        # Verify the format: List[Dict[str, str]] with 'code' and 'name' keys
        for item in result:
            assert isinstance(item, dict)
            assert 'code' in item
            assert 'name' in item
            assert isinstance(item['code'], str)
            assert isinstance(item['name'], str)

        # Check specific mappings
        occupation_dict = {occ['code']: occ['name'] for occ in result}
        assert occupation_dict['11-1021'] == "General and Operations Managers"
        assert occupation_dict['15-1251'] == "Computer Programmers"
        assert occupation_dict['29-1141'] == "Registered Nurses"
        assert occupation_dict['99-9999'] == "Unknown Occupation"

    def test_get_occupations_with_names_empty_occupation_codes_table(self):
        """Test get_occupations_with_names when occupation_codes table is empty"""
        # Mock session
        mock_session = Mock(spec=Session)

        # Query returns empty result from occupation_codes table
        mock_result = Mock()
        mock_result.fetchall.return_value = []

        mock_session.execute.return_value = mock_result

        # Call service method
        result = OccupationService.get_occupations_with_names(mock_session)

        # Assertions
        assert len(result) == 0
        assert mock_session.execute.call_count == 1

    def test_get_occupations_with_names_with_empty_names(self):
        """Test get_occupations_with_names with some occupation codes having empty names"""
        # Mock session
        mock_session = Mock(spec=Session)

        # Query returns tuples with some empty/None names
        mock_result = Mock()
        mock_result.fetchall.return_value = [
            ("11-1021", "General and Operations Managers"),
            ("15-1251", ""),  # Empty string name
            ("53-3032", "Heavy and Tractor-Trailer Truck Drivers"),
            ("99-0000", "   ")  # Whitespace-only name
        ]

        mock_session.execute.return_value = mock_result

        # Call service method
        result = OccupationService.get_occupations_with_names(mock_session)

        # Assertions
        assert len(result) == 4

        # Check mappings
        occupation_dict = {occ['code']: occ['name'] for occ in result}
        assert occupation_dict['11-1021'] == "General and Operations Managers"
        assert occupation_dict['53-3032'] == "Heavy and Tractor-Trailer Truck Drivers"
        # Empty names should use code as name
        assert occupation_dict['15-1251'] == "15-1251"
        assert occupation_dict['99-0000'] == "99-0000"

    def test_get_occupations_with_names_sorted_by_code(self):
        """Test get_occupations_with_names returns results sorted by occupation code"""
        # Mock session
        mock_session = Mock(spec=Session)

        # Query returns sorted results (simulating ORDER BY in the SQL query)
        mock_result = Mock()
        mock_result.fetchall.return_value = [
            ("11-1021", "General and Operations Managers"),
            ("15-1251", "Computer Programmers"),
            ("29-1141", "Registered Nurses"),
            ("53-3032", "Truck Drivers")
        ]

        mock_session.execute.return_value = mock_result

        # Call service method
        result = OccupationService.get_occupations_with_names(mock_session)

        # Assertions
        assert len(result) == 4

        # Check sorting
        codes = [occ['code'] for occ in result]
        assert codes == sorted(codes)
        assert codes == ["11-1021", "15-1251", "29-1141", "53-3032"]

    def test_get_occupations_with_names_database_error(self):
        """Test get_occupations_with_names handling database error on occupation_codes query"""
        # Mock session to raise error on execute
        mock_session = Mock(spec=Session)
        mock_session.execute.side_effect = SQLAlchemyError("Connection timeout")

        # Call service method and expect exception
        with pytest.raises(SQLAlchemyError) as exc_info:
            OccupationService.get_occupations_with_names(mock_session)

        assert "Connection timeout" in str(exc_info.value)
        assert mock_session.execute.call_count == 1

    def test_get_occupations_with_names_null_occupation_name(self):
        """Test get_occupations_with_names handles null occupation names gracefully"""
        # Mock session
        mock_session = Mock(spec=Session)

        # Query returns one null name
        mock_result = Mock()
        mock_result.fetchall.return_value = [
            ("11-1021", "General and Operations Managers"),
            ("15-1251", None)  # Null name
        ]

        mock_session.execute.return_value = mock_result

        # Call service method
        result = OccupationService.get_occupations_with_names(mock_session)

        # Assertions
        assert len(result) == 2
        assert result[0]['code'] == "11-1021"
        assert result[0]['name'] == "General and Operations Managers"
        assert result[1]['code'] == "15-1251"
        assert result[1]['name'] == "15-1251"  # Should fall back to code when name is None


    def test_get_occupations_with_names_duplicate_codes_in_table(self):
        """Test get_occupations_with_names handles duplicate codes in occupation_codes table"""
        # Mock session
        mock_session = Mock(spec=Session)

        # Query returns duplicate entries (should handle all of them)
        mock_result = Mock()
        mock_result.fetchall.return_value = [
            ("11-1021", "General Managers"),
            ("11-1021", "Operations Managers"),  # Duplicate code
            ("15-1251", "Programmers")
        ]

        mock_session.execute.return_value = mock_result

        # Call service method
        result = OccupationService.get_occupations_with_names(mock_session)

        # Assertions
        # The service returns all rows, including duplicates
        assert len(result) == 3
        assert result[0]['code'] == "11-1021"
        assert result[0]['name'] == "General Managers"
        assert result[1]['code'] == "11-1021"
        assert result[1]['name'] == "Operations Managers"
        assert result[2]['code'] == "15-1251"
        assert result[2]['name'] == "Programmers"

    def test_get_occupation_spatial_data_empty_result(self):
        """Test get_occupation_spatial_data with no matching category"""
        # Mock session and result
        mock_session = Mock(spec=Session)
        mock_result = Mock()
        mock_result.fetchall.return_value = []
        mock_session.execute.return_value = mock_result

        # Call service method
        result = OccupationService.get_occupation_spatial_data(mock_session, '51-3091')

        # Assertions
        assert result == []
        mock_session.execute.assert_called_once()
        mock_result.fetchall.assert_called_once()

    def test_get_occupation_spatial_data_with_results(self):
        """Test get_occupation_spatial_data with matching occupation data"""
        # Mock GeoJSON geometries
        point_geom1 = {"type": "Point", "coordinates": [-96.7970, 32.7767]}
        point_geom2 = {"type": "Point", "coordinates": [-96.3838, 32.7399]}

        # Mock row data
        mock_row1 = Mock()
        mock_row1.geoid = "48257050209"
        mock_row1.category = "51-3091"
        mock_row1.openings_2024_zscore = -0.0956
        mock_row1.jobs_2024_zscore = 0.0187
        mock_row1.openings_2024_zscore_color = "-0.5SD ~ +0.5SD"
        mock_row1.geometry = json.dumps(point_geom1)

        mock_row2 = Mock()
        mock_row2.geoid = "48257050213"
        mock_row2.category = "51-3091"
        mock_row2.openings_2024_zscore = -0.2926
        mock_row2.jobs_2024_zscore = -0.2762
        mock_row2.openings_2024_zscore_color = "-0.5SD ~ +0.5SD"
        mock_row2.geometry = json.dumps(point_geom2)

        # Mock session and result
        mock_session = Mock(spec=Session)
        mock_result = Mock()
        mock_result.fetchall.return_value = [mock_row1, mock_row2]
        mock_session.execute.return_value = mock_result

        # Call service method
        result = OccupationService.get_occupation_spatial_data(mock_session, '51-3091')

        # Assertions
        assert len(result) == 2
        assert all(isinstance(feature, OccupationGeoJSONFeature) for feature in result)

        # Check first feature
        feature1 = result[0]
        assert feature1.properties.geoid == "48257050209"
        assert feature1.properties.category == "51-3091"
        assert feature1.properties.openings_2024_zscore == -0.0956
        assert feature1.properties.jobs_2024_zscore == 0.0187
        assert feature1.properties.openings_2024_zscore_color == "-0.5SD ~ +0.5SD"
        assert feature1.geometry == point_geom1

        # Check second feature
        feature2 = result[1]
        assert feature2.properties.geoid == "48257050213"
        assert feature2.properties.openings_2024_zscore == -0.2926
        assert feature2.properties.jobs_2024_zscore == -0.2762

    def test_get_occupation_spatial_data_with_null_values(self):
        """Test get_occupation_spatial_data with null z-score values"""
        # Mock row data with null values
        mock_row = Mock()
        mock_row.geoid = "48113999999"
        mock_row.category = "51-4041"
        mock_row.openings_2024_zscore = None
        mock_row.jobs_2024_zscore = 0.5
        mock_row.openings_2024_zscore_color = None
        mock_row.geometry = json.dumps({"type": "Point", "coordinates": [-96.5, 32.5]})

        # Mock session and result
        mock_session = Mock(spec=Session)
        mock_result = Mock()
        mock_result.fetchall.return_value = [mock_row]
        mock_session.execute.return_value = mock_result

        # Call service method
        result = OccupationService.get_occupation_spatial_data(mock_session, '51-4041')

        # Assertions
        assert len(result) == 1
        feature = result[0]
        assert feature.properties.openings_2024_zscore is None
        assert feature.properties.jobs_2024_zscore == 0.5
        assert feature.properties.openings_2024_zscore_color is None


class TestSpatialService:
    """Test cases for SpatialService"""

    @pytest.fixture
    def sample_geojson_point(self):
        """Sample GeoJSON point geometry"""
        return {
            "type": "Point",
            "coordinates": [-96.7970, 32.7767]
        }

    @pytest.fixture
    def sample_geojson_polygon(self):
        """Sample GeoJSON polygon geometry"""
        return {
            "type": "Polygon",
            "coordinates": [[
                [-96.8, 32.8],
                [-96.7, 32.8],
                [-96.7, 32.7],
                [-96.8, 32.7],
                [-96.8, 32.8]
            ]]
        }

    def test_get_geojson_features_empty_result(self):
        """Test get_geojson_features with empty database result"""
        # Mock session and result
        mock_session = Mock(spec=Session)
        mock_result = Mock()
        mock_result.fetchall.return_value = []
        mock_session.execute.return_value = mock_result

        # Call service method
        result = SpatialService.get_geojson_features(mock_session)

        # Assertions
        assert result == []
        mock_session.execute.assert_called_once()
        mock_result.fetchall.assert_called_once()

    def test_get_geojson_features_single_result(self, sample_geojson_point):
        """Test get_geojson_features with single spatial feature"""
        # Mock row data
        mock_row = Mock()
        mock_row.geoid = "48113123456"
        mock_row.all_jobs_zscore = 1.5
        mock_row.all_jobs_zscore_cat = "High"
        mock_row.living_wage_zscore = 0.8
        mock_row.living_wage_zscore_cat = "Medium"
        mock_row.not_living_wage_zscore = -0.5
        mock_row.not_living_wage_zscore_cat = "Low"
        mock_row.geometry = json.dumps(sample_geojson_point)

        # Mock session and result
        mock_session = Mock(spec=Session)
        mock_result = Mock()
        mock_result.fetchall.return_value = [mock_row]
        mock_session.execute.return_value = mock_result

        # Call service method
        result = SpatialService.get_geojson_features(mock_session)

        # Assertions
        assert len(result) == 1
        feature = result[0]
        assert isinstance(feature, GeoJSONFeature)
        assert feature.type == "Feature"
        assert feature.geometry == sample_geojson_point
        assert feature.properties.geoid == "48113123456"
        assert feature.properties.all_jobs_zscore == 1.5
        assert feature.properties.all_jobs_zscore_cat == "High"
        assert feature.properties.living_wage_zscore == 0.8
        assert feature.properties.living_wage_zscore_cat == "Medium"
        assert feature.properties.not_living_wage_zscore == -0.5
        assert feature.properties.not_living_wage_zscore_cat == "Low"

    def test_get_geojson_features_multiple_results(self, sample_geojson_point, sample_geojson_polygon):
        """Test get_geojson_features with multiple spatial features"""
        # Mock row data
        mock_row1 = Mock()
        mock_row1.geoid = "48113123456"
        mock_row1.all_jobs_zscore = 1.5
        mock_row1.all_jobs_zscore_cat = "High"
        mock_row1.living_wage_zscore = 0.8
        mock_row1.living_wage_zscore_cat = "Medium"
        mock_row1.not_living_wage_zscore = -0.5
        mock_row1.not_living_wage_zscore_cat = "Low"
        mock_row1.geometry = json.dumps(sample_geojson_point)

        mock_row2 = Mock()
        mock_row2.geoid = "48113789012"
        mock_row2.all_jobs_zscore = -1.2
        mock_row2.all_jobs_zscore_cat = "Low"
        mock_row2.living_wage_zscore = 2.1
        mock_row2.living_wage_zscore_cat = "High"
        mock_row2.not_living_wage_zscore = 0.0
        mock_row2.not_living_wage_zscore_cat = "Medium"
        mock_row2.geometry = json.dumps(sample_geojson_polygon)

        # Mock session and result
        mock_session = Mock(spec=Session)
        mock_result = Mock()
        mock_result.fetchall.return_value = [mock_row1, mock_row2]
        mock_session.execute.return_value = mock_result

        # Call service method
        result = SpatialService.get_geojson_features(mock_session)

        # Assertions
        assert len(result) == 2

        # Check first feature
        feature1 = result[0]
        assert feature1.geometry == sample_geojson_point
        assert feature1.properties.geoid == "48113123456"

        # Check second feature
        feature2 = result[1]
        assert feature2.geometry == sample_geojson_polygon
        assert feature2.properties.geoid == "48113789012"
        assert feature2.properties.all_jobs_zscore == -1.2
        assert feature2.properties.living_wage_zscore == 2.1

    def test_get_geojson_features_with_null_values(self, sample_geojson_point):
        """Test get_geojson_features with null z-score values"""
        # Mock row data with null values
        mock_row = Mock()
        mock_row.geoid = "48113999999"
        mock_row.all_jobs_zscore = None
        mock_row.all_jobs_zscore_cat = None
        mock_row.living_wage_zscore = 1.0
        mock_row.living_wage_zscore_cat = "Medium"
        mock_row.not_living_wage_zscore = None
        mock_row.not_living_wage_zscore_cat = None
        mock_row.geometry = json.dumps(sample_geojson_point)

        # Mock session and result
        mock_session = Mock(spec=Session)
        mock_result = Mock()
        mock_result.fetchall.return_value = [mock_row]
        mock_session.execute.return_value = mock_result

        # Call service method
        result = SpatialService.get_geojson_features(mock_session)

        # Assertions
        assert len(result) == 1
        feature = result[0]
        assert feature.properties.all_jobs_zscore is None
        assert feature.properties.all_jobs_zscore_cat is None
        assert feature.properties.living_wage_zscore == 1.0
        assert feature.properties.living_wage_zscore_cat == "Medium"
        assert feature.properties.not_living_wage_zscore is None
        assert feature.properties.not_living_wage_zscore_cat is None

    def test_get_geojson_features_database_error(self):
        """Test get_geojson_features handling database errors"""
        # Mock session to raise SQLAlchemyError
        mock_session = Mock(spec=Session)
        mock_session.execute.side_effect = SQLAlchemyError("Database connection timeout")

        # Call service method and expect exception
        with pytest.raises(SQLAlchemyError) as exc_info:
            SpatialService.get_geojson_features(mock_session)

        assert "Database connection timeout" in str(exc_info.value)
        mock_session.execute.assert_called_once()

    def test_get_geojson_features_invalid_geometry_json(self):
        """Test get_geojson_features with invalid geometry JSON"""
        # Mock row data with invalid JSON
        mock_row = Mock()
        mock_row.geoid = "48113111111"
        mock_row.all_jobs_zscore = 0.5
        mock_row.all_jobs_zscore_cat = "Medium"
        mock_row.living_wage_zscore = 0.5
        mock_row.living_wage_zscore_cat = "Medium"
        mock_row.not_living_wage_zscore = 0.5
        mock_row.not_living_wage_zscore_cat = "Medium"
        mock_row.geometry = "invalid json {{"

        # Mock session and result
        mock_session = Mock(spec=Session)
        mock_result = Mock()
        mock_result.fetchall.return_value = [mock_row]
        mock_session.execute.return_value = mock_result

        # Call service method and expect JSON decode error
        with pytest.raises(json.JSONDecodeError):
            SpatialService.get_geojson_features(mock_session)

    def test_get_geojson_features_large_dataset(self, sample_geojson_point):
        """Test get_geojson_features with large dataset performance"""
        # Create 1000 mock rows
        mock_rows = []
        for i in range(1000):
            mock_row = Mock()
            mock_row.geoid = f"4811300{i:04d}"
            mock_row.all_jobs_zscore = float(i % 5 - 2)  # Values from -2 to 2
            mock_row.all_jobs_zscore_cat = ["Low", "Medium-Low", "Medium", "Medium-High", "High"][i % 5]
            mock_row.living_wage_zscore = float((i + 1) % 5 - 2)
            mock_row.living_wage_zscore_cat = ["Low", "Medium-Low", "Medium", "Medium-High", "High"][(i + 1) % 5]
            mock_row.not_living_wage_zscore = float((i + 2) % 5 - 2)
            mock_row.not_living_wage_zscore_cat = ["Low", "Medium-Low", "Medium", "Medium-High", "High"][(i + 2) % 5]
            mock_row.geometry = json.dumps(sample_geojson_point)
            mock_rows.append(mock_row)

        # Mock session and result
        mock_session = Mock(spec=Session)
        mock_result = Mock()
        mock_result.fetchall.return_value = mock_rows
        mock_session.execute.return_value = mock_result

        # Call service method
        result = SpatialService.get_geojson_features(mock_session)

        # Assertions
        assert len(result) == 1000
        assert all(isinstance(feature, GeoJSONFeature) for feature in result)
        assert result[0].properties.geoid == "48113000000"
        assert result[999].properties.geoid == "48113000999"

    def test_get_geojson_features_complex_geometry(self):
        """Test get_geojson_features with complex MultiPolygon geometry"""
        # Complex MultiPolygon GeoJSON
        complex_geometry = {
            "type": "MultiPolygon",
            "coordinates": [
                [[[102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0]]],
                [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]],
                 [[100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2]]]
            ]
        }

        # Mock row data
        mock_row = Mock()
        mock_row.geoid = "48113222222"
        mock_row.all_jobs_zscore = 0.0
        mock_row.all_jobs_zscore_cat = "Medium"
        mock_row.living_wage_zscore = 0.0
        mock_row.living_wage_zscore_cat = "Medium"
        mock_row.not_living_wage_zscore = 0.0
        mock_row.not_living_wage_zscore_cat = "Medium"
        mock_row.geometry = json.dumps(complex_geometry)

        # Mock session and result
        mock_session = Mock(spec=Session)
        mock_result = Mock()
        mock_result.fetchall.return_value = [mock_row]
        mock_session.execute.return_value = mock_result

        # Call service method
        result = SpatialService.get_geojson_features(mock_session)

        # Assertions
        assert len(result) == 1
        feature = result[0]
        assert feature.geometry == complex_geometry
        assert feature.geometry["type"] == "MultiPolygon"
        assert len(feature.geometry["coordinates"]) == 2

    def test_get_geojson_features_edge_case_zscore_values(self, sample_geojson_point):
        """Test get_geojson_features with edge case z-score values"""
        # Mock row data with extreme values
        mock_row = Mock()
        mock_row.geoid = "48113333333"
        mock_row.all_jobs_zscore = 999.999  # Very high z-score
        mock_row.all_jobs_zscore_cat = "Extremely High"
        mock_row.living_wage_zscore = -999.999  # Very low z-score
        mock_row.living_wage_zscore_cat = "Extremely Low"
        mock_row.not_living_wage_zscore = 0.0000001  # Very small positive
        mock_row.not_living_wage_zscore_cat = "Near Zero"
        mock_row.geometry = json.dumps(sample_geojson_point)

        # Mock session and result
        mock_session = Mock(spec=Session)
        mock_result = Mock()
        mock_result.fetchall.return_value = [mock_row]
        mock_session.execute.return_value = mock_result

        # Call service method
        result = SpatialService.get_geojson_features(mock_session)

        # Assertions
        assert len(result) == 1
        feature = result[0]
        assert feature.properties.all_jobs_zscore == 999.999
        assert feature.properties.living_wage_zscore == -999.999
        assert feature.properties.not_living_wage_zscore == 0.0000001


class TestIsochroneService:
    """Test cases for IsochroneService"""

    @pytest.fixture
    def sample_isochrone_polygon(self):
        """Sample GeoJSON polygon geometry for isochrone"""
        return {
            "type": "Polygon",
            "coordinates": [[
                [-96.8, 32.8],
                [-96.7, 32.8],
                [-96.7, 32.7],
                [-96.8, 32.7],
                [-96.8, 32.8]
            ]]
        }

    def test_get_isochrones_by_geoid_empty_result(self):
        """Test get_isochrones_by_geoid with no matching geoid"""
        # Mock session and result
        mock_session = Mock(spec=Session)
        mock_result = Mock()
        mock_result.fetchall.return_value = []
        mock_session.execute.return_value = mock_result

        # Call service method
        result = IsochroneService.get_isochrones_by_geoid(mock_session, '12345')

        # Assertions
        assert result == []
        mock_session.execute.assert_called_once()
        # Verify the geoid parameter was passed correctly
        args, kwargs = mock_session.execute.call_args
        assert args[1] == {"geoid": "12345"}  # Second argument is the params dict

    def test_get_isochrones_by_geoid_single_band(self, sample_isochrone_polygon):
        """Test get_isochrones_by_geoid with single travel time band"""
        # Mock row data
        mock_row = Mock()
        mock_row.geoid = "48113123456"
        mock_row.traveltime_category = "< 5"
        mock_row.geometry = json.dumps(sample_isochrone_polygon)

        # Mock session and result
        mock_session = Mock(spec=Session)
        mock_result = Mock()
        mock_result.fetchall.return_value = [mock_row]
        mock_session.execute.return_value = mock_result

        # Call service method
        result = IsochroneService.get_isochrones_by_geoid(mock_session, '48113123456')

        # Assertions
        assert len(result) == 1
        feature = result[0]
        assert isinstance(feature, IsochroneFeature)
        assert feature.type == "Feature"
        assert feature.geometry == sample_isochrone_polygon
        assert feature.properties.geoid == "48113123456"
        assert feature.properties.time_category == "< 5"
        assert feature.properties.color == "#1a9850"  # Color for "< 5" category

    def test_get_isochrones_by_geoid_multiple_bands(self, sample_isochrone_polygon):
        """Test get_isochrones_by_geoid with multiple travel time bands"""
        # Mock row data for different time categories
        mock_rows = []
        time_categories = ["< 5", "5~10", "10~15", "15~20", "20~25", "25~30", "30~45", "> 45"]

        for i, category in enumerate(time_categories):
            mock_row = Mock()
            mock_row.geoid = "48113999999"
            mock_row.traveltime_category = category
            # Create slightly different polygons for each band
            polygon = {
                "type": "Polygon",
                "coordinates": [[
                    [-96.8 + i*0.01, 32.8 + i*0.01],
                    [-96.7 + i*0.01, 32.8 + i*0.01],
                    [-96.7 + i*0.01, 32.7 + i*0.01],
                    [-96.8 + i*0.01, 32.7 + i*0.01],
                    [-96.8 + i*0.01, 32.8 + i*0.01]
                ]]
            }
            mock_row.geometry = json.dumps(polygon)
            mock_rows.append(mock_row)

        # Mock session and result
        mock_session = Mock(spec=Session)
        mock_result = Mock()
        mock_result.fetchall.return_value = mock_rows
        mock_session.execute.return_value = mock_result

        # Call service method
        result = IsochroneService.get_isochrones_by_geoid(mock_session, '48113999999')

        # Assertions
        assert len(result) == 8

        # Check each feature
        for i, feature in enumerate(result):
            assert isinstance(feature, IsochroneFeature)
            assert feature.properties.geoid == "48113999999"
            assert feature.properties.time_category == time_categories[i]
            assert feature.properties.color == IsochroneService.TIME_CATEGORY_COLORS[time_categories[i]]

        # Verify specific colors
        assert result[0].properties.color == "#1a9850"  # < 5
        assert result[1].properties.color == "#66bd63"  # 5~10
        assert result[2].properties.color == "#a6d96a"  # 10~15
        assert result[3].properties.color == "#fdae61"  # 15~20
        assert result[4].properties.color == "#fee08b"  # 20~25
        assert result[5].properties.color == "#f46d43"  # 25~30
        assert result[6].properties.color == "#d73027"  # 30~45
        assert result[7].properties.color == "#a50026"  # > 45

    def test_get_isochrones_by_geoid_unknown_time_category(self, sample_isochrone_polygon):
        """Test get_isochrones_by_geoid with unknown time category (should use default color)"""
        # Mock row data with unknown category
        mock_row = Mock()
        mock_row.geoid = "48113111111"
        mock_row.traveltime_category = "Unknown Category"
        mock_row.geometry = json.dumps(sample_isochrone_polygon)

        # Mock session and result
        mock_session = Mock(spec=Session)
        mock_result = Mock()
        mock_result.fetchall.return_value = [mock_row]
        mock_session.execute.return_value = mock_result

        # Call service method
        result = IsochroneService.get_isochrones_by_geoid(mock_session, '48113111111')

        # Assertions
        assert len(result) == 1
        feature = result[0]
        assert feature.properties.time_category == "Unknown Category"
        assert feature.properties.color == "#808080"  # Default gray color

    def test_get_isochrones_by_geoid_database_error(self):
        """Test get_isochrones_by_geoid handling database errors"""
        # Mock session to raise SQLAlchemyError
        mock_session = Mock(spec=Session)
        mock_session.execute.side_effect = SQLAlchemyError("Database connection error")

        # Call service method and expect exception
        with pytest.raises(SQLAlchemyError) as exc_info:
            IsochroneService.get_isochrones_by_geoid(mock_session, '12345')

        assert "Database connection error" in str(exc_info.value)
        mock_session.execute.assert_called_once()

    def test_get_isochrones_by_geoid_invalid_geometry_json(self):
        """Test get_isochrones_by_geoid with invalid geometry JSON"""
        # Mock row data with invalid JSON
        mock_row = Mock()
        mock_row.geoid = "48113222222"
        mock_row.traveltime_category = "< 5"
        mock_row.geometry = "invalid json {{"

        # Mock session and result
        mock_session = Mock(spec=Session)
        mock_result = Mock()
        mock_result.fetchall.return_value = [mock_row]
        mock_session.execute.return_value = mock_result

        # Call service method and expect JSON decode error
        with pytest.raises(json.JSONDecodeError):
            IsochroneService.get_isochrones_by_geoid(mock_session, '48113222222')

    def test_get_isochrones_by_geoid_large_dataset(self):
        """Test get_isochrones_by_geoid with large number of isochrone bands"""
        # Create 100 mock rows (simulating multiple geoids with multiple bands each)
        mock_rows = []
        for i in range(100):
            mock_row = Mock()
            mock_row.geoid = "48113000000"
            # Rotate through time categories
            categories = ["< 5", "5~10", "10~15", "15~20", "20~25", "25~30", "30~45", "> 45"]
            mock_row.traveltime_category = categories[i % 8]

            # Create geometry
            polygon = {
                "type": "Polygon",
                "coordinates": [[
                    [-96.8 + (i % 10)*0.01, 32.8 + (i // 10)*0.01],
                    [-96.7 + (i % 10)*0.01, 32.8 + (i // 10)*0.01],
                    [-96.7 + (i % 10)*0.01, 32.7 + (i // 10)*0.01],
                    [-96.8 + (i % 10)*0.01, 32.7 + (i // 10)*0.01],
                    [-96.8 + (i % 10)*0.01, 32.8 + (i // 10)*0.01]
                ]]
            }
            mock_row.geometry = json.dumps(polygon)
            mock_rows.append(mock_row)

        # Mock session and result
        mock_session = Mock(spec=Session)
        mock_result = Mock()
        mock_result.fetchall.return_value = mock_rows
        mock_session.execute.return_value = mock_result

        # Call service method
        result = IsochroneService.get_isochrones_by_geoid(mock_session, '48113000000')

        # Assertions
        assert len(result) == 100
        assert all(isinstance(feature, IsochroneFeature) for feature in result)
        assert all(feature.properties.geoid == "48113000000" for feature in result)

        # Verify color mapping is correct for all features
        for feature in result:
            expected_color = IsochroneService.TIME_CATEGORY_COLORS.get(
                feature.properties.time_category,
                "#808080"
            )
            assert feature.properties.color == expected_color

    def test_get_isochrones_by_geoid_complex_multipolygon_geometry(self):
        """Test get_isochrones_by_geoid with complex MultiPolygon geometry"""
        # Complex MultiPolygon GeoJSON (representing disconnected isochrone areas)
        complex_geometry = {
            "type": "MultiPolygon",
            "coordinates": [
                [[[102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0]]],
                [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]],
                 [[100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2]]]
            ]
        }

        # Mock row data
        mock_row = Mock()
        mock_row.geoid = "48113333333"
        mock_row.traveltime_category = "10~15"
        mock_row.geometry = json.dumps(complex_geometry)

        # Mock session and result
        mock_session = Mock(spec=Session)
        mock_result = Mock()
        mock_result.fetchall.return_value = [mock_row]
        mock_session.execute.return_value = mock_result

        # Call service method
        result = IsochroneService.get_isochrones_by_geoid(mock_session, '48113333333')

        # Assertions
        assert len(result) == 1
        feature = result[0]
        assert feature.geometry == complex_geometry
        assert feature.geometry["type"] == "MultiPolygon"
        assert len(feature.geometry["coordinates"]) == 2
        assert feature.properties.time_category == "10~15"
        assert feature.properties.color == "#a6d96a"

    def test_time_category_colors_mapping(self):
        """Test that TIME_CATEGORY_COLORS constant has expected values"""
        expected_colors = {
            "< 5": "#1a9850",
            "5~10": "#66bd63",
            "10~15": "#a6d96a",
            "15~20": "#fdae61",
            "20~25": "#fee08b",
            "25~30": "#f46d43",
            "30~45": "#d73027",
            "> 45": "#a50026"
        }

        assert IsochroneService.TIME_CATEGORY_COLORS == expected_colors
        assert len(IsochroneService.TIME_CATEGORY_COLORS) == 8
