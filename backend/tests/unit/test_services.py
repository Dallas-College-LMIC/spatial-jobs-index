"""
Unit tests for the services module in app/services.py.

This module tests the business logic layer of the spatial jobs index API,
including OccupationService and SpatialService classes. Tests use mocking
to simulate database queries and focus on verifying business logic behavior.

Test coverage includes:
- OccupationService.get_occupation_ids() with various data scenarios
- SpatialService.get_geojson_features() with geometry handling and conversions
- Error handling for database exceptions
- Edge cases like null values, empty results, and large datasets
"""
import pytest
from unittest.mock import Mock
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import json

from app.services import OccupationService, SpatialService
from app.models import GeoJSONFeature, OccupationGeoJSONFeature


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