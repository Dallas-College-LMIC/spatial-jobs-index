"""Unit tests for models in app/models.py and app/database.py."""

import pytest
from unittest.mock import patch, MagicMock
import os
from geoalchemy2 import WKTElement
from sqlalchemy import Column

from app.models import (
    OccupationLvlData,
    TTIClone,
    OccupationCode,
    OccupationIdsResponse,
    SpatialFeatureProperties,
    GeoJSONFeature,
    GeoJSONFeatureCollection,
)
from app.database import DatabaseConfig


class TestDatabaseConfig:
    """Test cases for DatabaseConfig model."""

    def test_valid_database_config(self):
        """Test creating DatabaseConfig with valid data."""
        config = DatabaseConfig(
            username="testuser",
            password="testpass",
            url="localhost:5432",
            database="testdb"
        )
        assert config.username == "testuser"
        assert config.password == "testpass"
        assert config.url == "localhost:5432"
        assert config.database == "testdb"

    def test_database_url_property(self):
        """Test database_url property generates correct URL."""
        config = DatabaseConfig(
            username="user",
            password="pass@123",
            url="db.example.com:5432",
            database="mydb"
        )
        expected_url = "postgresql://user:pass@123@db.example.com:5432/mydb"
        assert config.database_url == expected_url

    def test_from_env_success(self):
        """Test creating DatabaseConfig from environment variables."""
        env_vars = {
            'USERNAME': 'envuser',
            'PASS': 'envpass',
            'URL': 'envhost:5432',
            'DB': 'envdb'
        }
        with patch.dict(os.environ, env_vars):
            config = DatabaseConfig.from_env()
            assert config.username == 'envuser'
            assert config.password == 'envpass'
            assert config.url == 'envhost:5432'
            assert config.database == 'envdb'

    def test_from_env_missing_variables(self):
        """Test from_env raises error when environment variables are missing."""
        # Test with all variables missing
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(RuntimeError) as exc_info:
                DatabaseConfig.from_env()
            assert "Missing required environment variables: USERNAME, PASS, URL, DB" in str(exc_info.value)

        # Test with partial variables
        with patch.dict(os.environ, {'USERNAME': 'user', 'DB': 'db'}, clear=True):
            with pytest.raises(RuntimeError) as exc_info:
                DatabaseConfig.from_env()
            assert "Missing required environment variables: PASS, URL" in str(exc_info.value)

    def test_database_config_validation_errors(self):
        """Test DatabaseConfig validation with invalid types."""
        with pytest.raises(ValueError):
            DatabaseConfig(
                username=123,  # Should be string
                password="pass",
                url="localhost",
                database="db"
            )


class TestOccupationLvlData:
    """Test cases for OccupationLvlData ORM model."""

    def test_table_name_and_schema(self):
        """Test table name and schema are correctly set."""
        assert OccupationLvlData.__tablename__ == 'occupation_lvl_data'
        # During testing, __table_args__ is empty dict (no schema)
        assert OccupationLvlData.__table_args__ == {}

    def test_category_column(self):
        """Test category column properties."""
        assert hasattr(OccupationLvlData, 'category')
        assert isinstance(OccupationLvlData.category.property.columns[0], Column)
        assert OccupationLvlData.category.property.columns[0].primary_key is True
        assert OccupationLvlData.category.property.columns[0].type.python_type is str

    def test_occupation_instance_creation(self):
        """Test creating an instance of OccupationLvlData."""
        occupation = OccupationLvlData(category="Software Developer")
        assert occupation.category == "Software Developer"


class TestTTIClone:
    """Test cases for TTIClone ORM model."""

    def test_table_name_and_schema(self):
        """Test table name and schema are correctly set."""
        assert TTIClone.__tablename__ == 'tti_clone'
        # During testing, __table_args__ is empty dict (no schema)
        assert TTIClone.__table_args__ == {}

    def test_column_definitions(self):
        """Test all column definitions."""
        # Check geoid primary key
        assert hasattr(TTIClone, 'geoid')
        assert TTIClone.geoid.property.columns[0].primary_key is True
        assert TTIClone.geoid.property.columns[0].type.python_type is str

        # Check float columns
        float_columns = [
            'all_jobs_zscore', 'living_wage_zscore', 'not_living_wage_zscore'
        ]
        for col_name in float_columns:
            assert hasattr(TTIClone, col_name)
            assert TTIClone.__table__.columns[col_name].type.python_type is float

        # Check string columns
        string_columns = [
            'all_jobs_zscore_cat', 'living_wage_zscore_cat', 'not_living_wage_zscore_cat'
        ]
        for col_name in string_columns:
            assert hasattr(TTIClone, col_name)
            assert TTIClone.__table__.columns[col_name].type.python_type is str

        # Check geometry column
        assert hasattr(TTIClone, 'geom')

    def test_tti_instance_creation(self):
        """Test creating an instance of TTIClone with all fields."""
        # Mock geometry
        mock_geom = MagicMock(spec=WKTElement)

        tti = TTIClone(
            geoid="12345",
            all_jobs_zscore=1.5,
            all_jobs_zscore_cat="High",
            living_wage_zscore=-0.5,
            living_wage_zscore_cat="Low",
            not_living_wage_zscore=0.0,
            not_living_wage_zscore_cat="Medium",
            geom=mock_geom
        )

        assert tti.geoid == "12345"
        assert tti.all_jobs_zscore == 1.5
        assert tti.all_jobs_zscore_cat == "High"
        assert tti.living_wage_zscore == -0.5
        assert tti.living_wage_zscore_cat == "Low"
        assert tti.not_living_wage_zscore == 0.0
        assert tti.not_living_wage_zscore_cat == "Medium"
        assert tti.geom == mock_geom


class TestOccupationCode:
    """Test cases for OccupationCode ORM model."""

    def test_table_name_and_schema(self):
        """Test table name and schema are correctly set."""
        assert OccupationCode.__tablename__ == 'occupation_codes'
        # During testing, __table_args__ is empty dict (no schema)
        assert OccupationCode.__table_args__ == {}

    def test_column_definitions(self):
        """Test all column definitions."""
        # Check occupation_code column
        assert hasattr(OccupationCode, 'occupation_code')
        assert isinstance(OccupationCode.occupation_code.property.columns[0], Column)
        assert OccupationCode.occupation_code.property.columns[0].type.python_type is str

        # Check occupation_name column
        assert hasattr(OccupationCode, 'occupation_name')
        assert isinstance(OccupationCode.occupation_name.property.columns[0], Column)
        assert OccupationCode.occupation_name.property.columns[0].type.python_type is str

    def test_occupation_code_instance_creation(self):
        """Test creating an instance of OccupationCode."""
        occupation_code = OccupationCode(
            occupation_code="11-1021",
            occupation_name="General and Operations Managers"
        )
        assert occupation_code.occupation_code == "11-1021"
        assert occupation_code.occupation_name == "General and Operations Managers"

    def test_occupation_code_instance_with_empty_values(self):
        """Test creating an instance with empty string values."""
        occupation_code = OccupationCode(
            occupation_code="",
            occupation_name=""
        )
        assert occupation_code.occupation_code == ""
        assert occupation_code.occupation_name == ""

    def test_occupation_code_instance_with_special_characters(self):
        """Test creating an instance with special characters in the name."""
        occupation_code = OccupationCode(
            occupation_code="29-1141",
            occupation_name="Registered Nurses (RN's)"
        )
        assert occupation_code.occupation_code == "29-1141"
        assert occupation_code.occupation_name == "Registered Nurses (RN's)"


class TestOccupationIdsResponse:
    """Test cases for OccupationIdsResponse Pydantic model."""

    def test_valid_occupation_ids_response(self):
        """Test creating valid OccupationIdsResponse."""
        response = OccupationIdsResponse(
            occupation_ids=["developer", "analyst", "manager"]
        )
        assert response.occupation_ids == ["developer", "analyst", "manager"]
        assert len(response.occupation_ids) == 3

    def test_empty_occupation_list(self):
        """Test OccupationIdsResponse with empty list."""
        response = OccupationIdsResponse(occupation_ids=[])
        assert response.occupation_ids == []
        assert len(response.occupation_ids) == 0

    def test_occupation_ids_validation_error(self):
        """Test validation errors for invalid input."""
        # occupation_ids must be a list
        with pytest.raises(ValueError):
            OccupationIdsResponse(occupation_ids="not a list")

        # occupation_ids must contain strings
        with pytest.raises(ValueError):
            OccupationIdsResponse(occupation_ids=[1, 2, 3])

    def test_occupation_ids_serialization(self):
        """Test JSON serialization of OccupationIdsResponse."""
        response = OccupationIdsResponse(occupation_ids=["job1", "job2"])
        json_data = response.model_dump()
        assert json_data == {"occupation_ids": ["job1", "job2"]}

        # Test JSON string serialization
        json_str = response.model_dump_json()
        assert json_str == '{"occupation_ids":["job1","job2"]}'


class TestSpatialFeatureProperties:
    """Test cases for SpatialFeatureProperties Pydantic model."""

    def test_all_fields_provided(self):
        """Test creating SpatialFeatureProperties with all fields."""
        props = SpatialFeatureProperties(
            geoid="12345",
            all_jobs_zscore=1.5,
            all_jobs_zscore_cat="High",
            living_wage_zscore=-0.5,
            living_wage_zscore_cat="Low",
            not_living_wage_zscore=0.0,
            not_living_wage_zscore_cat="Medium"
        )

        assert props.geoid == "12345"
        assert props.all_jobs_zscore == 1.5
        assert props.all_jobs_zscore_cat == "High"
        assert props.living_wage_zscore == -0.5
        assert props.living_wage_zscore_cat == "Low"
        assert props.not_living_wage_zscore == 0.0
        assert props.not_living_wage_zscore_cat == "Medium"

    def test_only_required_field(self):
        """Test creating SpatialFeatureProperties with only required field (all fields with None)."""
        props = SpatialFeatureProperties(
            geoid="54321",
            all_jobs_zscore=None,
            all_jobs_zscore_cat=None,
            living_wage_zscore=None,
            living_wage_zscore_cat=None,
            not_living_wage_zscore=None,
            not_living_wage_zscore_cat=None
        )

        assert props.geoid == "54321"
        assert props.all_jobs_zscore is None
        assert props.all_jobs_zscore_cat is None
        assert props.living_wage_zscore is None
        assert props.living_wage_zscore_cat is None
        assert props.not_living_wage_zscore is None
        assert props.not_living_wage_zscore_cat is None

    def test_partial_optional_fields(self):
        """Test with some optional fields provided."""
        props = SpatialFeatureProperties(
            geoid="99999",
            all_jobs_zscore=2.0,
            all_jobs_zscore_cat=None,
            living_wage_zscore=None,
            living_wage_zscore_cat="Very High",
            not_living_wage_zscore=None,
            not_living_wage_zscore_cat=None
        )

        assert props.geoid == "99999"
        assert props.all_jobs_zscore == 2.0
        assert props.all_jobs_zscore_cat is None
        assert props.living_wage_zscore is None
        assert props.living_wage_zscore_cat == "Very High"

    def test_geoid_type_validation(self):
        """Test geoid must be a float."""
        # String that can be converted to float should work
        props = SpatialFeatureProperties(
            geoid="12345",
            all_jobs_zscore=None,
            all_jobs_zscore_cat=None,
            living_wage_zscore=None,
            living_wage_zscore_cat=None,
            not_living_wage_zscore=None,
            not_living_wage_zscore_cat=None
        )
        assert props.geoid == "12345"

        # Any string is valid for geoid (it's an identifier, not a number)
        # Test that we can create with various geoid formats
        props_with_leading_zero = SpatialFeatureProperties(
            geoid="01234",  # GEOID with leading zero
            all_jobs_zscore=None,
            all_jobs_zscore_cat=None,
            living_wage_zscore=None,
            living_wage_zscore_cat=None,
            not_living_wage_zscore=None,
            not_living_wage_zscore_cat=None
        )
        assert props_with_leading_zero.geoid == "01234"

    def test_zscore_type_validation(self):
        """Test z-score fields must be floats when provided."""
        with pytest.raises(ValueError):
            SpatialFeatureProperties(
                geoid="12345",
                all_jobs_zscore="not-a-float",
                all_jobs_zscore_cat=None,
                living_wage_zscore=None,
                living_wage_zscore_cat=None,
                not_living_wage_zscore=None,
                not_living_wage_zscore_cat=None
            )

    def test_serialization_with_none_values(self):
        """Test serialization handles None values correctly."""
        props = SpatialFeatureProperties(
            geoid="12345",
            all_jobs_zscore=None,
            all_jobs_zscore_cat=None,
            living_wage_zscore=None,
            living_wage_zscore_cat=None,
            not_living_wage_zscore=None,
            not_living_wage_zscore_cat=None
        )
        data = props.model_dump()

        assert data["geoid"] == "12345"
        assert data["all_jobs_zscore"] is None
        assert data["all_jobs_zscore_cat"] is None

        # Test exclude_none option
        data_no_none = props.model_dump(exclude_none=True)
        assert data_no_none == {"geoid": "12345"}


class TestGeoJSONFeature:
    """Test cases for GeoJSONFeature Pydantic model."""

    def test_valid_geojson_feature(self):
        """Test creating a valid GeoJSON feature."""
        geometry = {
            "type": "Point",
            "coordinates": [-96.7969, 32.7763]
        }
        properties = SpatialFeatureProperties(
            geoid="12345",
            all_jobs_zscore=1.0,
            all_jobs_zscore_cat=None,
            living_wage_zscore=None,
            living_wage_zscore_cat=None,
            not_living_wage_zscore=None,
            not_living_wage_zscore_cat=None
        )

        feature = GeoJSONFeature(
            geometry=geometry,
            properties=properties
        )

        assert feature.type == "Feature"
        assert feature.geometry == geometry
        assert feature.properties.geoid == "12345"
        assert feature.properties.all_jobs_zscore == 1.0

    def test_type_default_value(self):
        """Test that type field has correct default value."""
        geometry = {"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]}
        properties = SpatialFeatureProperties(
            geoid="54321",
            all_jobs_zscore=None,
            all_jobs_zscore_cat=None,
            living_wage_zscore=None,
            living_wage_zscore_cat=None,
            not_living_wage_zscore=None,
            not_living_wage_zscore_cat=None
        )

        feature = GeoJSONFeature(geometry=geometry, properties=properties)
        assert feature.type == "Feature"

    def test_type_override_attempt(self):
        """Test that type field can be overridden (though not recommended)."""
        geometry = {"type": "LineString", "coordinates": [[0, 0], [1, 1]]}
        properties = SpatialFeatureProperties(
            geoid="11111",
            all_jobs_zscore=None,
            all_jobs_zscore_cat=None,
            living_wage_zscore=None,
            living_wage_zscore_cat=None,
            not_living_wage_zscore=None,
            not_living_wage_zscore_cat=None
        )

        # Pydantic allows overriding defaults
        feature = GeoJSONFeature(
            type="CustomType",
            geometry=geometry,
            properties=properties
        )
        assert feature.type == "CustomType"

        # But the default is still "Feature" when not provided
        feature2 = GeoJSONFeature(
            geometry=geometry,
            properties=properties
        )
        assert feature2.type == "Feature"

    def test_complex_geometry(self):
        """Test with complex MultiPolygon geometry."""
        geometry = {
            "type": "MultiPolygon",
            "coordinates": [
                [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
                [[[2, 2], [3, 2], [3, 3], [2, 3], [2, 2]]]
            ]
        }
        properties = SpatialFeatureProperties(
            geoid="99999",
            all_jobs_zscore=2.5,
            all_jobs_zscore_cat="Very High",
            living_wage_zscore=None,
            living_wage_zscore_cat=None,
            not_living_wage_zscore=None,
            not_living_wage_zscore_cat=None
        )

        feature = GeoJSONFeature(geometry=geometry, properties=properties)
        assert feature.geometry["type"] == "MultiPolygon"
        assert len(feature.geometry["coordinates"]) == 2

    def test_geojson_serialization(self):
        """Test serialization to GeoJSON format."""
        geometry = {"type": "Point", "coordinates": [100.0, 0.0]}
        properties = SpatialFeatureProperties(
            geoid="12345",
            all_jobs_zscore=None,
            all_jobs_zscore_cat=None,
            living_wage_zscore=None,
            living_wage_zscore_cat=None,
            not_living_wage_zscore=None,
            not_living_wage_zscore_cat=None
        )

        feature = GeoJSONFeature(geometry=geometry, properties=properties)
        json_data = feature.model_dump()

        assert json_data["type"] == "Feature"
        assert json_data["geometry"] == geometry
        assert json_data["properties"]["geoid"] == "12345"

    def test_missing_required_fields(self):
        """Test validation errors for missing required fields."""
        properties = SpatialFeatureProperties(
            geoid="12345",
            all_jobs_zscore=None,
            all_jobs_zscore_cat=None,
            living_wage_zscore=None,
            living_wage_zscore_cat=None,
            not_living_wage_zscore=None,
            not_living_wage_zscore_cat=None
        )

        # Missing geometry
        with pytest.raises(ValueError):
            GeoJSONFeature(properties=properties)

        # Missing properties
        geometry = {"type": "Point", "coordinates": [0, 0]}
        with pytest.raises(ValueError):
            GeoJSONFeature(geometry=geometry)


class TestGeoJSONFeatureCollection:
    """Test cases for GeoJSONFeatureCollection Pydantic model."""

    def test_valid_feature_collection(self):
        """Test creating a valid GeoJSON FeatureCollection."""
        features = []
        for i in range(3):
            geometry = {"type": "Point", "coordinates": [i, i]}
            properties = SpatialFeatureProperties(
                geoid=str(i),
                all_jobs_zscore=None,
                all_jobs_zscore_cat=None,
                living_wage_zscore=None,
                living_wage_zscore_cat=None,
                not_living_wage_zscore=None,
                not_living_wage_zscore_cat=None
            )
            feature = GeoJSONFeature(geometry=geometry, properties=properties)
            features.append(feature)

        collection = GeoJSONFeatureCollection(features=features)

        assert collection.type == "FeatureCollection"
        assert len(collection.features) == 3
        assert collection.features[0].properties.geoid == "0"
        assert collection.features[2].properties.geoid == "2"

    def test_empty_feature_collection(self):
        """Test creating empty FeatureCollection."""
        collection = GeoJSONFeatureCollection(features=[])

        assert collection.type == "FeatureCollection"
        assert collection.features == []
        assert len(collection.features) == 0

    def test_type_default_value(self):
        """Test that type field has correct default value."""
        collection = GeoJSONFeatureCollection(features=[])
        assert collection.type == "FeatureCollection"

    def test_large_feature_collection(self):
        """Test with a large number of features."""
        features = []
        for i in range(100):
            geometry = {
                "type": "Polygon",
                "coordinates": [[[i, i], [i+1, i], [i+1, i+1], [i, i+1], [i, i]]]
            }
            properties = SpatialFeatureProperties(
                geoid=str(i),
                all_jobs_zscore=i * 0.1,
                all_jobs_zscore_cat="High" if i > 50 else "Low",
                living_wage_zscore=None,
                living_wage_zscore_cat=None,
                not_living_wage_zscore=None,
                not_living_wage_zscore_cat=None
            )
            feature = GeoJSONFeature(geometry=geometry, properties=properties)
            features.append(feature)

        collection = GeoJSONFeatureCollection(features=features)
        assert len(collection.features) == 100
        assert collection.features[50].properties.all_jobs_zscore == 5.0

    def test_feature_collection_serialization(self):
        """Test serialization of FeatureCollection."""
        geometry = {"type": "Point", "coordinates": [0, 0]}
        properties = SpatialFeatureProperties(
            geoid="12345",
            all_jobs_zscore=None,
            all_jobs_zscore_cat=None,
            living_wage_zscore=None,
            living_wage_zscore_cat=None,
            not_living_wage_zscore=None,
            not_living_wage_zscore_cat=None
        )
        feature = GeoJSONFeature(geometry=geometry, properties=properties)

        collection = GeoJSONFeatureCollection(features=[feature])
        json_data = collection.model_dump()

        assert json_data["type"] == "FeatureCollection"
        assert len(json_data["features"]) == 1
        assert json_data["features"][0]["type"] == "Feature"
        assert json_data["features"][0]["properties"]["geoid"] == "12345"

    def test_features_validation_error(self):
        """Test validation error for invalid features."""
        # features must be a list
        with pytest.raises(ValueError):
            GeoJSONFeatureCollection(features="not a list")

        # features must contain GeoJSONFeature objects
        with pytest.raises(ValueError):
            GeoJSONFeatureCollection(features=[{"invalid": "object"}])

    def test_nested_serialization(self):
        """Test full nested serialization with exclude_none."""
        features = []
        for i in range(2):
            geometry = {"type": "Point", "coordinates": [i, i]}
            properties = SpatialFeatureProperties(
                geoid=str(i),
                all_jobs_zscore=i * 1.0 if i > 0 else None,
                all_jobs_zscore_cat=None,
                living_wage_zscore=None,
                living_wage_zscore_cat=None,
                not_living_wage_zscore=None,
                not_living_wage_zscore_cat=None
            )
            feature = GeoJSONFeature(geometry=geometry, properties=properties)
            features.append(feature)

        collection = GeoJSONFeatureCollection(features=features)

        # Full serialization
        full_data = collection.model_dump()
        assert full_data["features"][0]["properties"]["all_jobs_zscore"] is None
        assert full_data["features"][1]["properties"]["all_jobs_zscore"] == 1.0

        # Serialization with exclude_none
        compact_data = collection.model_dump(exclude_none=True)
        assert "all_jobs_zscore" not in compact_data["features"][0]["properties"]
        assert compact_data["features"][1]["properties"]["all_jobs_zscore"] == 1.0


class TestModelIntegration:
    """Integration tests for model interactions."""

    def test_orm_to_pydantic_conversion(self):
        """Test converting ORM models to Pydantic response models."""
        # Create mock TTIClone instance
        mock_tti = MagicMock(spec=TTIClone)
        mock_tti.geoid = "12345"
        mock_tti.all_jobs_zscore = 1.5
        mock_tti.all_jobs_zscore_cat = "High"
        mock_tti.living_wage_zscore = None
        mock_tti.living_wage_zscore_cat = None
        mock_tti.not_living_wage_zscore = -0.5
        mock_tti.not_living_wage_zscore_cat = "Low"

        # Convert to Pydantic model
        properties = SpatialFeatureProperties(
            geoid=mock_tti.geoid,
            all_jobs_zscore=mock_tti.all_jobs_zscore,
            all_jobs_zscore_cat=mock_tti.all_jobs_zscore_cat,
            living_wage_zscore=mock_tti.living_wage_zscore,
            living_wage_zscore_cat=mock_tti.living_wage_zscore_cat,
            not_living_wage_zscore=mock_tti.not_living_wage_zscore,
            not_living_wage_zscore_cat=mock_tti.not_living_wage_zscore_cat
        )

        assert properties.geoid == "12345"
        assert properties.all_jobs_zscore == 1.5
        assert properties.living_wage_zscore is None

    def test_geojson_compliance(self):
        """Test that generated GeoJSON follows the specification."""
        # Create a complete GeoJSON structure
        geometry = {
            "type": "Polygon",
            "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]
        }
        properties = SpatialFeatureProperties(
            geoid="12345",
            all_jobs_zscore=1.0,
            all_jobs_zscore_cat="Medium",
            living_wage_zscore=None,
            living_wage_zscore_cat=None,
            not_living_wage_zscore=None,
            not_living_wage_zscore_cat=None
        )
        feature = GeoJSONFeature(geometry=geometry, properties=properties)
        collection = GeoJSONFeatureCollection(features=[feature])

        # Verify structure
        json_data = collection.model_dump()

        # Top level must have type and features
        assert "type" in json_data
        assert "features" in json_data
        assert json_data["type"] == "FeatureCollection"
        assert isinstance(json_data["features"], list)

        # Each feature must have type, geometry, and properties
        feature_data = json_data["features"][0]
        assert "type" in feature_data
        assert "geometry" in feature_data
        assert "properties" in feature_data
        assert feature_data["type"] == "Feature"

        # Geometry must have type and coordinates
        assert "type" in feature_data["geometry"]
        assert "coordinates" in feature_data["geometry"]
