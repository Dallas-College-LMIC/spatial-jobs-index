"""Unit tests for SchoolOfStudyService in app/services.py."""

from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from app.services import SchoolOfStudyService
from app.models import SchoolOfStudyGeoJSONFeature


class TestSchoolOfStudyService:
    """Test cases for SchoolOfStudyService."""

    def test_get_school_ids(self):
        """Test getting all distinct school categories."""
        # Mock session
        mock_session = MagicMock(spec=Session)

        # Create service instance
        service = SchoolOfStudyService(mock_session)

        # Mock repository method
        mock_categories = [
            {"code": "ETMS", "name": "Energy, Technology, Manufacturing & Science"},
            {"code": "BHGT", "name": "Business, Hospitality, Governance & Tourism"},
            {"code": "CE", "name": "Construction & Engineering"},
            {"code": "EDU", "name": "Education"},
            {"code": "CAED", "name": "Creative Arts, Entertainment & Design"},
            {"code": "HS", "name": "Health Services"},
            {"code": "LPS", "name": "Legal & Public Services"},
            {"code": "MIT", "name": "Management & Information Technology"},
        ]
        service.repository.get_school_of_study_categories = MagicMock(
            return_value=mock_categories
        )

        # Call the service method
        result = service.get_school_ids()

        # Verify results
        assert result == ["ETMS", "BHGT", "CE", "EDU", "CAED", "HS", "LPS", "MIT"]
        assert len(result) == 8

        # Verify repository method was called
        service.repository.get_school_of_study_categories.assert_called_once()

    def test_get_school_name_mappings(self):
        """Test that school name mappings are correctly defined."""
        mappings = SchoolOfStudyService.get_school_name_mappings()

        # Verify all 8 categories are mapped
        assert len(mappings) == 8

        # Verify specific mappings
        assert mappings["BHGT"] == "Business, Hospitality, Governance & Tourism"
        assert mappings["CAED"] == "Creative Arts, Entertainment & Design"
        assert mappings["CE"] == "Construction & Engineering"
        assert mappings["EDU"] == "Education"
        assert mappings["ETMS"] == "Energy, Technology, Manufacturing & Science"
        assert mappings["HS"] == "Health Services"
        assert mappings["LPS"] == "Legal & Public Services"
        assert mappings["MIT"] == "Management & Information Technology"

        # Verify all values are strings
        for key, value in mappings.items():
            assert isinstance(key, str)
            assert isinstance(value, str)
            assert len(value) > 0

    def test_get_school_spatial_data(self):
        """Test getting spatial data for a specific school category."""
        # Mock session
        mock_session = MagicMock(spec=Session)

        # Create service instance
        service = SchoolOfStudyService(mock_session)

        # Mock repository method response
        mock_features_data = [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-96.7969, 32.7763]},
                "properties": {
                    "geoid": "48113020100",
                    "category": "ETMS",
                    "openings_2024_zscore": 1.5,
                    "jobs_2024_zscore": -0.3,
                    "openings_2024_zscore_color": "#FF0000",
                },
            }
        ]
        service.repository.get_spatial_data_by_category = MagicMock(
            return_value=mock_features_data
        )

        # Call the service method
        result = service.get_school_spatial_data("ETMS")

        # Verify results
        assert len(result) == 1
        assert isinstance(result[0], SchoolOfStudyGeoJSONFeature)

        # Verify feature properties
        feature = result[0]
        assert feature.type == "Feature"
        assert feature.properties.geoid == "48113020100"
        assert feature.properties.category == "ETMS"
        assert feature.properties.openings_2024_zscore == 1.5
        assert feature.properties.jobs_2024_zscore == -0.3
        assert feature.properties.openings_2024_zscore_color == "#FF0000"

        # Verify geometry
        assert feature.geometry == {"type": "Point", "coordinates": [-96.7969, 32.7763]}

        # Verify repository method was called with correct parameters
        service.repository.get_spatial_data_by_category.assert_called_once_with("ETMS")

    def test_get_school_spatial_data_empty_result(self):
        """Test getting spatial data when no data exists for category."""
        # Mock session
        mock_session = MagicMock(spec=Session)

        # Create service instance
        service = SchoolOfStudyService(mock_session)

        # Mock empty repository response
        service.repository.get_spatial_data_by_category = MagicMock(return_value=[])

        # Call the service method
        result = service.get_school_spatial_data("NONEXISTENT")

        # Verify empty results
        assert result == []
        assert len(result) == 0

        # Verify repository method was called
        service.repository.get_spatial_data_by_category.assert_called_once_with(
            "NONEXISTENT"
        )

    def test_get_school_spatial_data_multiple_features(self):
        """Test getting spatial data with multiple features for a category."""
        # Mock session
        mock_session = MagicMock(spec=Session)

        # Create service instance
        service = SchoolOfStudyService(mock_session)

        # Mock repository method response with multiple features
        mock_features_data = [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-96.7969, 32.7763]},
                "properties": {
                    "geoid": "48113020100",
                    "category": "ETMS",
                    "openings_2024_zscore": 1.5,
                    "jobs_2024_zscore": -0.3,
                    "openings_2024_zscore_color": "#FF0000",
                },
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-96.8000, 32.8000]},
                "properties": {
                    "geoid": "48113020200",
                    "category": "ETMS",
                    "openings_2024_zscore": 0.8,
                    "jobs_2024_zscore": 1.2,
                    "openings_2024_zscore_color": "#00FF00",
                },
            },
        ]
        service.repository.get_spatial_data_by_category = MagicMock(
            return_value=mock_features_data
        )

        # Call the service method
        result = service.get_school_spatial_data("ETMS")

        # Verify results
        assert len(result) == 2

        # Verify first feature
        feature1 = result[0]
        assert feature1.properties.geoid == "48113020100"
        assert feature1.properties.openings_2024_zscore == 1.5

        # Verify second feature
        feature2 = result[1]
        assert feature2.properties.geoid == "48113020200"
        assert feature2.properties.openings_2024_zscore == 0.8

    def test_get_school_spatial_data_with_none_values(self):
        """Test getting spatial data with None values in optional fields."""
        # Mock session
        mock_session = MagicMock(spec=Session)

        # Create service instance
        service = SchoolOfStudyService(mock_session)

        # Mock repository method response with None values
        mock_features_data = [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-96.7969, 32.7763]},
                "properties": {
                    "geoid": "48113020100",
                    "category": "ETMS",
                    "openings_2024_zscore": None,
                    "jobs_2024_zscore": None,
                    "openings_2024_zscore_color": None,
                },
            }
        ]
        service.repository.get_spatial_data_by_category = MagicMock(
            return_value=mock_features_data
        )

        # Call the service method
        result = service.get_school_spatial_data("ETMS")

        # Verify results
        assert len(result) == 1
        feature = result[0]
        assert feature.properties.geoid == "48113020100"
        assert feature.properties.category == "ETMS"
        assert feature.properties.openings_2024_zscore is None
        assert feature.properties.jobs_2024_zscore is None
        assert feature.properties.openings_2024_zscore_color is None
