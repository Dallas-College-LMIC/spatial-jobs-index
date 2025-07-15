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
        # Mock session
        mock_session = Mock(spec=Session)

        # Create service instance
        service = OccupationService(mock_session)

        # Mock repository method
        service.repository.get_occupation_categories = Mock(return_value=[])

        # Call service method
        result = service.get_occupation_ids()

        # Assertions
        assert result == []
        service.repository.get_occupation_categories.assert_called_once()

    def test_get_occupation_ids_single_result(self):
        """Test get_occupation_ids with single occupation category"""
        # Mock session
        mock_session = Mock(spec=Session)

        # Create service instance
        service = OccupationService(mock_session)

        # Mock repository method
        service.repository.get_occupation_categories = Mock(
            return_value=[{"code": "Healthcare", "name": "Healthcare Services"}]
        )

        # Call service method
        result = service.get_occupation_ids()

        # Assertions
        assert result == ["Healthcare"]
        service.repository.get_occupation_categories.assert_called_once()

    def test_get_occupation_ids_multiple_results(self):
        """Test get_occupation_ids with multiple occupation categories"""
        # Mock session
        mock_session = Mock(spec=Session)

        # Create service instance
        service = OccupationService(mock_session)

        # Mock repository method
        service.repository.get_occupation_categories = Mock(
            return_value=[
                {"code": "Healthcare", "name": "Healthcare Services"},
                {"code": "Technology", "name": "Technology Services"},
                {"code": "Education", "name": "Education Services"},
                {"code": "Manufacturing", "name": "Manufacturing Services"},
            ]
        )

        # Call service method
        result = service.get_occupation_ids()

        # Assertions
        assert result == ["Healthcare", "Technology", "Education", "Manufacturing"]
        assert len(result) == 4
        service.repository.get_occupation_categories.assert_called_once()

    def test_get_occupation_ids_database_error(self):
        """Test get_occupation_ids handling database errors"""
        # Mock session
        mock_session = Mock(spec=Session)

        # Create service instance
        service = OccupationService(mock_session)

        # Mock repository method to raise error
        service.repository.get_occupation_categories = Mock(
            side_effect=SQLAlchemyError("Database connection error")
        )

        # Call service method and expect exception
        with pytest.raises(SQLAlchemyError) as exc_info:
            service.get_occupation_ids()

        assert "Database connection error" in str(exc_info.value)
        service.repository.get_occupation_categories.assert_called_once()

    def test_get_occupations_with_names_queries_occupation_codes_table(self):
        """Test get_occupations_with_names queries occupation_codes table directly"""
        # Mock session
        mock_session = Mock(spec=Session)

        # Create service instance
        service = OccupationService(mock_session)

        # Mock repository method
        service.repository.get_occupation_categories = Mock(
            return_value=[
                {"code": "11-1021", "name": "General and Operations Managers"},
                {"code": "15-1251", "name": "Computer Programmers"},
                {"code": "29-1141", "name": "Registered Nurses"},
                {
                    "code": "99-9999",
                    "name": "Unknown Occupation",
                },  # All codes should have names in occupation_codes table
            ]
        )

        # Call service method
        result = service.get_occupations_with_names()

        # Assertions
        assert len(result) == 4
        service.repository.get_occupation_categories.assert_called_once()

        # Verify the format: List[Dict[str, str]] with 'code' and 'name' keys
        for item in result:
            assert isinstance(item, dict)
            assert "code" in item
            assert "name" in item
            assert isinstance(item["code"], str)
            assert isinstance(item["name"], str)

        # Check specific mappings
        occupation_dict = {occ["code"]: occ["name"] for occ in result}
        assert occupation_dict["11-1021"] == "General and Operations Managers"
        assert occupation_dict["15-1251"] == "Computer Programmers"
        assert occupation_dict["29-1141"] == "Registered Nurses"
        assert occupation_dict["99-9999"] == "Unknown Occupation"

    def test_get_occupations_with_names_empty_occupation_codes_table(self):
        """Test get_occupations_with_names when occupation_codes table is empty"""
        # Mock session
        mock_session = Mock(spec=Session)

        # Create service instance
        service = OccupationService(mock_session)

        # Mock repository method
        service.repository.get_occupation_categories = Mock(return_value=[])

        # Call service method
        result = service.get_occupations_with_names()

        # Assertions
        assert len(result) == 0
        service.repository.get_occupation_categories.assert_called_once()

    def test_get_occupations_with_names_with_empty_names(self):
        """Test get_occupations_with_names with some occupation codes having empty names"""
        # Mock session
        mock_session = Mock(spec=Session)

        # Create service instance
        service = OccupationService(mock_session)

        # Mock repository method - note that repository should handle empty names
        service.repository.get_occupation_categories = Mock(
            return_value=[
                {"code": "11-1021", "name": "General and Operations Managers"},
                {
                    "code": "15-1251",
                    "name": "15-1251",
                },  # Empty string name handled by repository
                {"code": "53-3032", "name": "Heavy and Tractor-Trailer Truck Drivers"},
                {
                    "code": "99-0000",
                    "name": "99-0000",
                },  # Whitespace-only name handled by repository
            ]
        )

        # Call service method
        result = service.get_occupations_with_names()

        # Assertions
        assert len(result) == 4

        # Check mappings
        occupation_dict = {occ["code"]: occ["name"] for occ in result}
        assert occupation_dict["11-1021"] == "General and Operations Managers"
        assert occupation_dict["53-3032"] == "Heavy and Tractor-Trailer Truck Drivers"
        # Empty names should use code as name
        assert occupation_dict["15-1251"] == "15-1251"
        assert occupation_dict["99-0000"] == "99-0000"

    def test_get_occupations_with_names_sorted_by_code(self):
        """Test get_occupations_with_names returns results sorted by occupation code"""
        # Mock session
        mock_session = Mock(spec=Session)

        # Create service instance
        service = OccupationService(mock_session)

        # Mock repository method - repository returns sorted results
        service.repository.get_occupation_categories = Mock(
            return_value=[
                {"code": "11-1021", "name": "General and Operations Managers"},
                {"code": "15-1251", "name": "Computer Programmers"},
                {"code": "29-1141", "name": "Registered Nurses"},
                {"code": "53-3032", "name": "Truck Drivers"},
            ]
        )

        # Call service method
        result = service.get_occupations_with_names()

        # Assertions
        assert len(result) == 4

        # Check sorting
        codes = [occ["code"] for occ in result]
        assert codes == sorted(codes)
        assert codes == ["11-1021", "15-1251", "29-1141", "53-3032"]

    def test_get_occupations_with_names_database_error(self):
        """Test get_occupations_with_names handling database error on occupation_codes query"""
        # Mock session
        mock_session = Mock(spec=Session)

        # Create service instance
        service = OccupationService(mock_session)

        # Mock repository method to raise error
        service.repository.get_occupation_categories = Mock(
            side_effect=SQLAlchemyError("Connection timeout")
        )

        # Call service method and expect exception
        with pytest.raises(SQLAlchemyError) as exc_info:
            service.get_occupations_with_names()

        assert "Connection timeout" in str(exc_info.value)
        service.repository.get_occupation_categories.assert_called_once()

    def test_get_occupations_with_names_null_occupation_name(self):
        """Test get_occupations_with_names handles null occupation names gracefully"""
        # Mock session
        mock_session = Mock(spec=Session)

        # Create service instance
        service = OccupationService(mock_session)

        # Mock repository method - repository handles null names
        service.repository.get_occupation_categories = Mock(
            return_value=[
                {"code": "11-1021", "name": "General and Operations Managers"},
                {
                    "code": "15-1251",
                    "name": "15-1251",
                },  # Repository returns code as name for null
            ]
        )

        # Call service method
        result = service.get_occupations_with_names()

        # Assertions
        assert len(result) == 2
        assert result[0]["code"] == "11-1021"
        assert result[0]["name"] == "General and Operations Managers"
        assert result[1]["code"] == "15-1251"
        assert (
            result[1]["name"] == "15-1251"
        )  # Should fall back to code when name is None

    def test_get_occupations_with_names_duplicate_codes_in_table(self):
        """Test get_occupations_with_names handles duplicate codes in occupation_codes table"""
        # Mock session
        mock_session = Mock(spec=Session)

        # Create service instance
        service = OccupationService(mock_session)

        # Mock repository method - repository returns all entries including duplicates
        service.repository.get_occupation_categories = Mock(
            return_value=[
                {"code": "11-1021", "name": "General Managers"},
                {"code": "11-1021", "name": "Operations Managers"},  # Duplicate code
                {"code": "15-1251", "name": "Programmers"},
            ]
        )

        # Call service method
        result = service.get_occupations_with_names()

        # Assertions
        # The service returns all rows, including duplicates
        assert len(result) == 3
        assert result[0]["code"] == "11-1021"
        assert result[0]["name"] == "General Managers"
        assert result[1]["code"] == "11-1021"
        assert result[1]["name"] == "Operations Managers"
        assert result[2]["code"] == "15-1251"
        assert result[2]["name"] == "Programmers"

    def test_get_occupation_spatial_data_empty_result(self):
        """Test get_occupation_spatial_data with no matching category"""
        # Mock session
        mock_session = Mock(spec=Session)

        # Create service instance
        service = OccupationService(mock_session)

        # Mock repository method
        service.repository.get_spatial_data_by_category = Mock(return_value=[])

        # Call service method
        result = service.get_occupation_spatial_data("51-3091")

        # Assertions
        assert result == []
        service.repository.get_spatial_data_by_category.assert_called_once_with(
            "51-3091"
        )

    def test_get_occupation_spatial_data_with_results(self):
        """Test get_occupation_spatial_data with matching occupation data"""
        # Mock GeoJSON geometries
        point_geom1 = {"type": "Point", "coordinates": [-96.7970, 32.7767]}
        point_geom2 = {"type": "Point", "coordinates": [-96.3838, 32.7399]}

        # Mock session
        mock_session = Mock(spec=Session)

        # Create service instance
        service = OccupationService(mock_session)

        # Mock repository method
        service.repository.get_spatial_data_by_category = Mock(
            return_value=[
                {
                    "geometry": point_geom1,
                    "properties": {
                        "geoid": "48257050209",
                        "category": "51-3091",
                        "openings_2024_zscore": -0.0956,
                        "jobs_2024_zscore": 0.0187,
                        "openings_2024_zscore_color": "-0.5SD ~ +0.5SD",
                    },
                },
                {
                    "geometry": point_geom2,
                    "properties": {
                        "geoid": "48257050213",
                        "category": "51-3091",
                        "openings_2024_zscore": -0.2926,
                        "jobs_2024_zscore": -0.2762,
                        "openings_2024_zscore_color": "-0.5SD ~ +0.5SD",
                    },
                },
            ]
        )

        # Call service method
        result = service.get_occupation_spatial_data("51-3091")

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
        # Mock session
        mock_session = Mock(spec=Session)

        # Create service instance
        service = OccupationService(mock_session)

        # Mock repository method
        service.repository.get_spatial_data_by_category = Mock(
            return_value=[
                {
                    "geometry": {"type": "Point", "coordinates": [-96.5, 32.5]},
                    "properties": {
                        "geoid": "48113999999",
                        "category": "51-4041",
                        "openings_2024_zscore": None,
                        "jobs_2024_zscore": 0.5,
                        "openings_2024_zscore_color": None,
                    },
                }
            ]
        )

        # Call service method
        result = service.get_occupation_spatial_data("51-4041")

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
        return {"type": "Point", "coordinates": [-96.7970, 32.7767]}

    @pytest.fixture
    def sample_geojson_polygon(self):
        """Sample GeoJSON polygon geometry"""
        return {
            "type": "Polygon",
            "coordinates": [
                [
                    [-96.8, 32.8],
                    [-96.7, 32.8],
                    [-96.7, 32.7],
                    [-96.8, 32.7],
                    [-96.8, 32.8],
                ]
            ],
        }

    def test_get_geojson_features_empty_result(self):
        """Test get_geojson_features with empty database result"""
        # Mock session
        mock_session = Mock(spec=Session)

        # Create service instance
        service = SpatialService(mock_session)

        # Mock repository method
        service.repository.get_all_wage_data = Mock(return_value=[])

        # Call service method
        result = service.get_geojson_features()

        # Assertions
        assert result == []
        service.repository.get_all_wage_data.assert_called_once()

    def test_get_geojson_features_single_result(self, sample_geojson_point):
        """Test get_geojson_features with single spatial feature"""
        # Mock session
        mock_session = Mock(spec=Session)

        # Create service instance
        service = SpatialService(mock_session)

        # Mock repository method
        service.repository.get_all_wage_data = Mock(
            return_value=[
                {
                    "geometry": sample_geojson_point,
                    "properties": {
                        "geoid": "48113123456",
                        "all_jobs_zscore": 1.5,
                        "all_jobs_zscore_cat": "High",
                        "living_wage_zscore": 0.8,
                        "living_wage_zscore_cat": "Medium",
                        "not_living_wage_zscore": -0.5,
                        "not_living_wage_zscore_cat": "Low",
                    },
                }
            ]
        )

        # Call service method
        result = service.get_geojson_features()

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

    def test_get_geojson_features_multiple_results(
        self, sample_geojson_point, sample_geojson_polygon
    ):
        """Test get_geojson_features with multiple spatial features"""
        # Mock session
        mock_session = Mock(spec=Session)

        # Create service instance
        service = SpatialService(mock_session)

        # Mock repository method
        service.repository.get_all_wage_data = Mock(
            return_value=[
                {
                    "geometry": sample_geojson_point,
                    "properties": {
                        "geoid": "48113123456",
                        "all_jobs_zscore": 1.5,
                        "all_jobs_zscore_cat": "High",
                        "living_wage_zscore": 0.8,
                        "living_wage_zscore_cat": "Medium",
                        "not_living_wage_zscore": -0.5,
                        "not_living_wage_zscore_cat": "Low",
                    },
                },
                {
                    "geometry": sample_geojson_polygon,
                    "properties": {
                        "geoid": "48113789012",
                        "all_jobs_zscore": -1.2,
                        "all_jobs_zscore_cat": "Low",
                        "living_wage_zscore": 2.1,
                        "living_wage_zscore_cat": "High",
                        "not_living_wage_zscore": 0.0,
                        "not_living_wage_zscore_cat": "Medium",
                    },
                },
            ]
        )

        # Call service method
        result = service.get_geojson_features()

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
        # Mock session
        mock_session = Mock(spec=Session)

        # Create service instance
        service = SpatialService(mock_session)

        # Mock repository method
        service.repository.get_all_wage_data = Mock(
            return_value=[
                {
                    "geometry": sample_geojson_point,
                    "properties": {
                        "geoid": "48113999999",
                        "all_jobs_zscore": None,
                        "all_jobs_zscore_cat": None,
                        "living_wage_zscore": 1.0,
                        "living_wage_zscore_cat": "Medium",
                        "not_living_wage_zscore": None,
                        "not_living_wage_zscore_cat": None,
                    },
                }
            ]
        )

        # Call service method
        result = service.get_geojson_features()

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
        # Mock session
        mock_session = Mock(spec=Session)

        # Create service instance
        service = SpatialService(mock_session)

        # Mock repository method to raise error
        service.repository.get_all_wage_data = Mock(
            side_effect=SQLAlchemyError("Database connection timeout")
        )

        # Call service method and expect exception
        with pytest.raises(SQLAlchemyError) as exc_info:
            service.get_geojson_features()

        assert "Database connection timeout" in str(exc_info.value)
        service.repository.get_all_wage_data.assert_called_once()

    def test_get_geojson_features_invalid_geometry_json(self):
        """Test get_geojson_features with invalid geometry JSON"""
        # Mock session
        mock_session = Mock(spec=Session)

        # Create service instance
        service = SpatialService(mock_session)

        # Mock repository method to raise JSON decode error
        service.repository.get_all_wage_data = Mock(
            side_effect=json.JSONDecodeError("Expecting value", "invalid json {{", 0)
        )

        # Call service method and expect JSON decode error
        with pytest.raises(json.JSONDecodeError):
            service.get_geojson_features()

    def test_get_geojson_features_large_dataset(self, sample_geojson_point):
        """Test get_geojson_features with large dataset performance"""
        # Mock session
        mock_session = Mock(spec=Session)

        # Create service instance
        service = SpatialService(mock_session)

        # Create 1000 mock feature dictionaries
        mock_features = []
        for i in range(1000):
            mock_features.append(
                {
                    "geometry": sample_geojson_point,
                    "properties": {
                        "geoid": f"4811300{i:04d}",
                        "all_jobs_zscore": float(i % 5 - 2),  # Values from -2 to 2
                        "all_jobs_zscore_cat": [
                            "Low",
                            "Medium-Low",
                            "Medium",
                            "Medium-High",
                            "High",
                        ][i % 5],
                        "living_wage_zscore": float((i + 1) % 5 - 2),
                        "living_wage_zscore_cat": [
                            "Low",
                            "Medium-Low",
                            "Medium",
                            "Medium-High",
                            "High",
                        ][(i + 1) % 5],
                        "not_living_wage_zscore": float((i + 2) % 5 - 2),
                        "not_living_wage_zscore_cat": [
                            "Low",
                            "Medium-Low",
                            "Medium",
                            "Medium-High",
                            "High",
                        ][(i + 2) % 5],
                    },
                }
            )

        # Mock repository method
        service.repository.get_all_wage_data = Mock(return_value=mock_features)

        # Call service method
        result = service.get_geojson_features()

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
                [
                    [
                        [102.0, 2.0],
                        [103.0, 2.0],
                        [103.0, 3.0],
                        [102.0, 3.0],
                        [102.0, 2.0],
                    ]
                ],
                [
                    [
                        [100.0, 0.0],
                        [101.0, 0.0],
                        [101.0, 1.0],
                        [100.0, 1.0],
                        [100.0, 0.0],
                    ],
                    [
                        [100.2, 0.2],
                        [100.8, 0.2],
                        [100.8, 0.8],
                        [100.2, 0.8],
                        [100.2, 0.2],
                    ],
                ],
            ],
        }

        # Mock session
        mock_session = Mock(spec=Session)

        # Create service instance
        service = SpatialService(mock_session)

        # Mock repository method
        service.repository.get_all_wage_data = Mock(
            return_value=[
                {
                    "geometry": complex_geometry,
                    "properties": {
                        "geoid": "48113222222",
                        "all_jobs_zscore": 0.0,
                        "all_jobs_zscore_cat": "Medium",
                        "living_wage_zscore": 0.0,
                        "living_wage_zscore_cat": "Medium",
                        "not_living_wage_zscore": 0.0,
                        "not_living_wage_zscore_cat": "Medium",
                    },
                }
            ]
        )

        # Call service method
        result = service.get_geojson_features()

        # Assertions
        assert len(result) == 1
        feature = result[0]
        assert feature.geometry == complex_geometry
        assert feature.geometry["type"] == "MultiPolygon"
        assert len(feature.geometry["coordinates"]) == 2

    def test_get_geojson_features_edge_case_zscore_values(self, sample_geojson_point):
        """Test get_geojson_features with edge case z-score values"""
        # Mock session
        mock_session = Mock(spec=Session)

        # Create service instance
        service = SpatialService(mock_session)

        # Mock repository method
        service.repository.get_all_wage_data = Mock(
            return_value=[
                {
                    "geometry": sample_geojson_point,
                    "properties": {
                        "geoid": "48113333333",
                        "all_jobs_zscore": 999.999,  # Very high z-score
                        "all_jobs_zscore_cat": "Extremely High",
                        "living_wage_zscore": -999.999,  # Very low z-score
                        "living_wage_zscore_cat": "Extremely Low",
                        "not_living_wage_zscore": 0.0000001,  # Very small positive
                        "not_living_wage_zscore_cat": "Near Zero",
                    },
                }
            ]
        )

        # Call service method
        result = service.get_geojson_features()

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
            "coordinates": [
                [
                    [-96.8, 32.8],
                    [-96.7, 32.8],
                    [-96.7, 32.7],
                    [-96.8, 32.7],
                    [-96.8, 32.8],
                ]
            ],
        }

    def test_get_isochrones_by_geoid_empty_result(self):
        """Test get_isochrones_by_geoid with no matching geoid"""
        # Mock session
        mock_session = Mock(spec=Session)

        # Create service instance
        service = IsochroneService(mock_session)

        # Mock repository method
        service.repository.get_isochrones_by_geoid = Mock(return_value=[])

        # Call service method
        result = service.get_isochrones_by_geoid("12345")

        # Assertions
        assert result == []
        service.repository.get_isochrones_by_geoid.assert_called_once_with("12345")

    def test_get_isochrones_by_geoid_single_band(self, sample_isochrone_polygon):
        """Test get_isochrones_by_geoid with single travel time band"""
        # Mock session
        mock_session = Mock(spec=Session)

        # Create service instance
        service = IsochroneService(mock_session)

        # Mock repository method
        service.repository.get_isochrones_by_geoid = Mock(
            return_value=[
                {
                    "geometry": sample_isochrone_polygon,
                    "properties": {
                        "geoid": "48113123456",
                        "time_category": "< 5",
                        "color": "#1a9850",  # Color for "< 5" category
                    },
                }
            ]
        )

        # Call service method
        result = service.get_isochrones_by_geoid("48113123456")

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
        # Mock session
        mock_session = Mock(spec=Session)

        # Create service instance
        service = IsochroneService(mock_session)

        # Time categories and their colors
        time_categories = [
            "< 5",
            "5~10",
            "10~15",
            "15~20",
            "20~25",
            "25~30",
            "30~45",
            "> 45",
        ]

        # Create mock return data
        mock_features = []
        for i, category in enumerate(time_categories):
            # Create slightly different polygons for each band
            polygon = {
                "type": "Polygon",
                "coordinates": [
                    [
                        [-96.8 + i * 0.01, 32.8 + i * 0.01],
                        [-96.7 + i * 0.01, 32.8 + i * 0.01],
                        [-96.7 + i * 0.01, 32.7 + i * 0.01],
                        [-96.8 + i * 0.01, 32.7 + i * 0.01],
                        [-96.8 + i * 0.01, 32.8 + i * 0.01],
                    ]
                ],
            }
            mock_features.append(
                {
                    "geometry": polygon,
                    "properties": {
                        "geoid": "48113999999",
                        "time_category": category,
                        "color": IsochroneService.TIME_CATEGORY_COLORS[category],
                    },
                }
            )

        # Mock repository method
        service.repository.get_isochrones_by_geoid = Mock(return_value=mock_features)

        # Call service method
        result = service.get_isochrones_by_geoid("48113999999")

        # Assertions
        assert len(result) == 8

        # Check each feature
        for i, feature in enumerate(result):
            assert isinstance(feature, IsochroneFeature)
            assert feature.properties.geoid == "48113999999"
            assert feature.properties.time_category == time_categories[i]
            assert (
                feature.properties.color
                == IsochroneService.TIME_CATEGORY_COLORS[time_categories[i]]
            )

        # Verify specific colors
        assert result[0].properties.color == "#1a9850"  # < 5
        assert result[1].properties.color == "#66bd63"  # 5~10
        assert result[2].properties.color == "#a6d96a"  # 10~15
        assert result[3].properties.color == "#fdae61"  # 15~20
        assert result[4].properties.color == "#fee08b"  # 20~25
        assert result[5].properties.color == "#f46d43"  # 25~30
        assert result[6].properties.color == "#d73027"  # 30~45
        assert result[7].properties.color == "#a50026"  # > 45

    def test_get_isochrones_by_geoid_unknown_time_category(
        self, sample_isochrone_polygon
    ):
        """Test get_isochrones_by_geoid with unknown time category (should use default color)"""
        # Mock session
        mock_session = Mock(spec=Session)

        # Create service instance
        service = IsochroneService(mock_session)

        # Mock repository method
        service.repository.get_isochrones_by_geoid = Mock(
            return_value=[
                {
                    "geometry": sample_isochrone_polygon,
                    "properties": {
                        "geoid": "48113111111",
                        "time_category": "Unknown Category",
                        "color": "#808080",  # Default gray color
                    },
                }
            ]
        )

        # Call service method
        result = service.get_isochrones_by_geoid("48113111111")

        # Assertions
        assert len(result) == 1
        feature = result[0]
        assert feature.properties.time_category == "Unknown Category"
        assert feature.properties.color == "#808080"  # Default gray color

    def test_get_isochrones_by_geoid_database_error(self):
        """Test get_isochrones_by_geoid handling database errors"""
        # Mock session
        mock_session = Mock(spec=Session)

        # Create service instance
        service = IsochroneService(mock_session)

        # Mock repository method to raise error
        service.repository.get_isochrones_by_geoid = Mock(
            side_effect=SQLAlchemyError("Database connection error")
        )

        # Call service method and expect exception
        with pytest.raises(SQLAlchemyError) as exc_info:
            service.get_isochrones_by_geoid("12345")

        assert "Database connection error" in str(exc_info.value)
        service.repository.get_isochrones_by_geoid.assert_called_once_with("12345")

    def test_get_isochrones_by_geoid_invalid_geometry_json(self):
        """Test get_isochrones_by_geoid with invalid geometry JSON"""
        # Mock session
        mock_session = Mock(spec=Session)

        # Create service instance
        service = IsochroneService(mock_session)

        # Mock repository method to raise JSON decode error
        service.repository.get_isochrones_by_geoid = Mock(
            side_effect=json.JSONDecodeError("Expecting value", "invalid json {{", 0)
        )

        # Call service method and expect JSON decode error
        with pytest.raises(json.JSONDecodeError):
            service.get_isochrones_by_geoid("48113222222")

    def test_get_isochrones_by_geoid_large_dataset(self):
        """Test get_isochrones_by_geoid with large number of isochrone bands"""
        # Mock session
        mock_session = Mock(spec=Session)

        # Create service instance
        service = IsochroneService(mock_session)

        # Create 100 mock features
        mock_features = []
        categories = [
            "< 5",
            "5~10",
            "10~15",
            "15~20",
            "20~25",
            "25~30",
            "30~45",
            "> 45",
        ]

        for i in range(100):
            # Create geometry
            polygon = {
                "type": "Polygon",
                "coordinates": [
                    [
                        [-96.8 + (i % 10) * 0.01, 32.8 + (i // 10) * 0.01],
                        [-96.7 + (i % 10) * 0.01, 32.8 + (i // 10) * 0.01],
                        [-96.7 + (i % 10) * 0.01, 32.7 + (i // 10) * 0.01],
                        [-96.8 + (i % 10) * 0.01, 32.7 + (i // 10) * 0.01],
                        [-96.8 + (i % 10) * 0.01, 32.8 + (i // 10) * 0.01],
                    ]
                ],
            }
            time_category = categories[i % 8]
            mock_features.append(
                {
                    "geometry": polygon,
                    "properties": {
                        "geoid": "48113000000",
                        "time_category": time_category,
                        "color": IsochroneService.TIME_CATEGORY_COLORS.get(
                            time_category, "#808080"
                        ),
                    },
                }
            )

        # Mock repository method
        service.repository.get_isochrones_by_geoid = Mock(return_value=mock_features)

        # Call service method
        result = service.get_isochrones_by_geoid("48113000000")

        # Assertions
        assert len(result) == 100
        assert all(isinstance(feature, IsochroneFeature) for feature in result)
        assert all(feature.properties.geoid == "48113000000" for feature in result)

        # Verify color mapping is correct for all features
        for feature in result:
            expected_color = IsochroneService.TIME_CATEGORY_COLORS.get(
                feature.properties.time_category, "#808080"
            )
            assert feature.properties.color == expected_color

    def test_get_isochrones_by_geoid_complex_multipolygon_geometry(self):
        """Test get_isochrones_by_geoid with complex MultiPolygon geometry"""
        # Complex MultiPolygon GeoJSON (representing disconnected isochrone areas)
        complex_geometry = {
            "type": "MultiPolygon",
            "coordinates": [
                [
                    [
                        [102.0, 2.0],
                        [103.0, 2.0],
                        [103.0, 3.0],
                        [102.0, 3.0],
                        [102.0, 2.0],
                    ]
                ],
                [
                    [
                        [100.0, 0.0],
                        [101.0, 0.0],
                        [101.0, 1.0],
                        [100.0, 1.0],
                        [100.0, 0.0],
                    ],
                    [
                        [100.2, 0.2],
                        [100.8, 0.2],
                        [100.8, 0.8],
                        [100.2, 0.8],
                        [100.2, 0.2],
                    ],
                ],
            ],
        }

        # Mock session
        mock_session = Mock(spec=Session)

        # Create service instance
        service = IsochroneService(mock_session)

        # Mock repository method
        service.repository.get_isochrones_by_geoid = Mock(
            return_value=[
                {
                    "geometry": complex_geometry,
                    "properties": {
                        "geoid": "48113333333",
                        "time_category": "10~15",
                        "color": "#a6d96a",  # Color for "10~15" category
                    },
                }
            ]
        )

        # Call service method
        result = service.get_isochrones_by_geoid("48113333333")

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
            "> 45": "#a50026",
        }

        assert IsochroneService.TIME_CATEGORY_COLORS == expected_colors
        assert len(IsochroneService.TIME_CATEGORY_COLORS) == 8
