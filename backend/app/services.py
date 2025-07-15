from sqlalchemy.orm import Session
from typing import List, Dict
import os
import logging

from .models import (
    SpatialFeatureProperties,
    GeoJSONFeature,
    OccupationSpatialProperties,
    OccupationGeoJSONFeature,
    SchoolOfStudySpatialProperties,
    SchoolOfStudyGeoJSONFeature,
    IsochroneProperties,
    IsochroneFeature,
)
from .repositories import (
    OccupationRepository,
    SchoolOfStudyRepository,
    TravelTimeRepository,
)

logger = logging.getLogger(__name__)


class OccupationService:
    """Service for occupation-related operations"""

    def __init__(self, session: Session):
        self.repository = OccupationRepository(session)
        self.session = session

    def get_occupation_ids(self) -> List[str]:
        """Get all distinct occupation categories"""
        categories = self.repository.get_occupation_categories()
        return [cat["code"] for cat in categories]

    def get_occupations_with_names(self) -> List[Dict[str, str]]:
        """
        Get all occupation codes with their names from the occupation_codes table.
        """
        from app.occupation_cache import _cache

        # Check if we're in testing mode
        is_testing = os.getenv("TESTING") == "1"

        # Generate cache key
        cache_key = "get_occupations_with_names"

        # Try to get from cache if not testing
        if not is_testing:
            cached_value = _cache.get(cache_key)
            if cached_value is not None:
                return cached_value

        # Get occupation categories from repository
        occupations = self.repository.get_occupation_categories()

        # Cache the result if not testing
        if not is_testing:
            _cache.set(cache_key, occupations, 86400)  # Cache for 24 hours

        return occupations

    def get_occupation_spatial_data(
        self, category: str
    ) -> List[OccupationGeoJSONFeature]:
        """Get spatial data for a specific occupation category as GeoJSON features"""
        # Get features from repository
        features_data = self.repository.get_spatial_data_by_category(category)

        # Convert to Pydantic models
        features = []
        for feature_dict in features_data:
            properties = OccupationSpatialProperties(**feature_dict["properties"])
            feature = OccupationGeoJSONFeature(
                geometry=feature_dict["geometry"], properties=properties
            )
            features.append(feature)

        return features


class SpatialService:
    """Service for spatial data operations"""

    def __init__(self, session: Session):
        self.repository = TravelTimeRepository(session)
        self.session = session

    def get_geojson_features(self) -> List[GeoJSONFeature]:
        """Get all spatial data as GeoJSON features"""
        # Get all wage data from repository
        features_data = self.repository.get_all_wage_data()

        # Convert to Pydantic models
        features = []
        for feature_dict in features_data:
            properties = SpatialFeatureProperties(**feature_dict["properties"])
            feature = GeoJSONFeature(
                geometry=feature_dict["geometry"], properties=properties
            )
            features.append(feature)

        return features


class SchoolOfStudyService:
    """Service for school of study data operations"""

    # School category to full name mappings
    SCHOOL_NAME_MAPPINGS = {
        "BHGT": "Business, Hospitality, Governance & Tourism",
        "CAED": "Creative Arts, Entertainment & Design",
        "CE": "Construction & Engineering",
        "EDU": "Education",
        "ETMS": "Energy, Technology, Manufacturing & Science",
        "HS": "Health Services",
        "LPS": "Legal & Public Services",
        "MIT": "Management & Information Technology",
    }

    def __init__(self, session: Session):
        self.repository = SchoolOfStudyRepository(session)
        self.session = session

    def get_school_ids(self) -> List[str]:
        """Get all distinct school categories"""
        categories = self.repository.get_school_of_study_categories()
        return [cat["code"] for cat in categories]

    @classmethod
    def get_school_name_mappings(cls) -> Dict[str, str]:
        """Get the mapping of school category codes to full names"""
        return cls.SCHOOL_NAME_MAPPINGS.copy()

    def get_school_spatial_data(
        self, category: str
    ) -> List[SchoolOfStudyGeoJSONFeature]:
        """Get spatial data for a specific school category as GeoJSON features"""
        # Get features from repository
        features_data = self.repository.get_spatial_data_by_category(category)

        # Convert to Pydantic models
        features = []
        for feature_dict in features_data:
            properties = SchoolOfStudySpatialProperties(**feature_dict["properties"])
            feature = SchoolOfStudyGeoJSONFeature(
                geometry=feature_dict["geometry"], properties=properties
            )
            features.append(feature)

        return features


class IsochroneService:
    """Service for isochrone travel time operations"""

    # Color mapping for travel time categories
    TIME_CATEGORY_COLORS = {
        "< 5": "#1a9850",
        "5~10": "#66bd63",
        "10~15": "#a6d96a",
        "15~20": "#fdae61",
        "20~25": "#fee08b",
        "25~30": "#f46d43",
        "30~45": "#d73027",
        "> 45": "#a50026",
    }

    def __init__(self, session: Session):
        self.repository = TravelTimeRepository(session)
        self.session = session

    @classmethod
    def get_time_category_colors(cls) -> Dict[str, str]:
        """Get the mapping of time categories to colors"""
        return cls.TIME_CATEGORY_COLORS.copy()

    def get_isochrones_by_geoid(self, geoid: str) -> List[IsochroneFeature]:
        """Get all isochrone bands for a specific census tract"""
        # Get isochrone data from repository
        features_data = self.repository.get_isochrones_by_geoid(geoid)

        # Convert to Pydantic models
        features = []
        for feature_dict in features_data:
            properties = IsochroneProperties(**feature_dict["properties"])
            feature = IsochroneFeature(
                geometry=feature_dict["geometry"], properties=properties
            )
            features.append(feature)

        return features
