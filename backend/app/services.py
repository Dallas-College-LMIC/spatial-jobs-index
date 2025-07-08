from sqlalchemy.orm import Session
from sqlalchemy import select
from geoalchemy2.functions import ST_AsGeoJSON
from typing import List, Dict
import json

from .models import OccupationLvlData, TTIClone, SpatialFeatureProperties, GeoJSONFeature, OccupationSpatialProperties, OccupationGeoJSONFeature

import logging

logger = logging.getLogger(__name__)

class OccupationService:
    """Service for occupation-related operations"""
    
    @staticmethod
    def get_occupation_ids(session: Session) -> List[str]:
        """Get all distinct occupation categories"""
        # Use table reference that works in both test and production
        if hasattr(OccupationLvlData, '__table__'):
            result = session.execute(
                select(OccupationLvlData.category).distinct()
            )
        else:
            # Fallback for edge cases
            result = session.execute(
                select(OccupationLvlData.category).distinct()
            )
        return [row[0] for row in result.fetchall()]
    
    @staticmethod
    def get_occupations_with_names(session: Session) -> List[Dict[str, str]]:
        """
        Get all distinct occupation categories with their names.
        First tries to get names from Lightcast API, falls back to static mapping if needed.
        """
        import os
        from app.occupation_cache import _cache, OCCUPATION_NAMES
        
        # Check if we're in testing mode
        is_testing = os.getenv('TESTING') == '1'
        
        # Generate cache key
        cache_key = "get_occupations_with_names"
        
        # Try to get from cache if not testing
        if not is_testing:
            cached_value = _cache.get(cache_key)
            if cached_value is not None:
                return cached_value
        
        # Get occupation codes from database
        result = session.execute(
            select(OccupationLvlData.category).distinct()
        )
        occupation_codes = [row[0] for row in result.fetchall()]
        
        # Try to get names from Lightcast API first
        occupations_dict = {}
        try:
            from app.lightcast_api import get_lightcast_client
            client = get_lightcast_client()
            lightcast_occupations = client.get_occupations()
            
            # Create a lookup dict from Lightcast data
            for occ in lightcast_occupations:
                occupations_dict[occ['code']] = occ['name']
                
            logger.info(f"Successfully loaded {len(lightcast_occupations)} occupation names")
        except Exception as e:
            logger.warning(f"Failed to fetch from Lightcast API, using static mapping: {str(e)}")
            # Fall back to static mapping
            occupations_dict = OCCUPATION_NAMES
        
        # Map codes to names
        occupations = []
        for code in occupation_codes:
            # Use Lightcast name if available, otherwise static mapping, otherwise code itself
            name = occupations_dict.get(code, OCCUPATION_NAMES.get(code, code))
            occupations.append({
                'code': code,
                'name': name
            })
        
        # Sort by code for consistent ordering
        occupations.sort(key=lambda x: x['code'])
        
        # Cache the result if not testing
        if not is_testing:
            _cache.set(cache_key, occupations, 86400)  # Cache for 24 hours
        
        return occupations
    
    @staticmethod
    def get_occupation_spatial_data(session: Session, category: str) -> List[OccupationGeoJSONFeature]:
        """Get spatial data for a specific occupation category as GeoJSON features"""
        query = select(
            OccupationLvlData.geoid,
            OccupationLvlData.category,
            OccupationLvlData.openings_2024_zscore,
            OccupationLvlData.jobs_2024_zscore,
            OccupationLvlData.openings_2024_zscore_color,
            ST_AsGeoJSON(OccupationLvlData.geom).label('geometry')
        ).where(OccupationLvlData.category == category)
        
        result = session.execute(query)
        features = []
        
        for row in result.fetchall():
            properties = OccupationSpatialProperties(
                geoid=str(row.geoid),
                category=row.category,
                openings_2024_zscore=row.openings_2024_zscore,
                jobs_2024_zscore=row.jobs_2024_zscore,
                openings_2024_zscore_color=row.openings_2024_zscore_color
            )
            
            feature = OccupationGeoJSONFeature(
                geometry=json.loads(row.geometry),
                properties=properties
            )
            features.append(feature)
        
        return features

class SpatialService:
    """Service for spatial data operations"""
    
    @staticmethod
    def get_geojson_features(session: Session) -> List[GeoJSONFeature]:
        """Get all spatial data as GeoJSON features"""
        query = select(
            TTIClone.geoid,
            TTIClone.all_jobs_zscore,
            TTIClone.all_jobs_zscore_cat,
            TTIClone.living_wage_zscore,
            TTIClone.living_wage_zscore_cat,
            TTIClone.not_living_wage_zscore,
            TTIClone.not_living_wage_zscore_cat,
            ST_AsGeoJSON(TTIClone.geom).label('geometry')
        )
        
        result = session.execute(query)
        features = []
        
        for row in result.fetchall():
            properties = SpatialFeatureProperties(
                geoid=str(row.geoid),
                all_jobs_zscore=row.all_jobs_zscore,
                all_jobs_zscore_cat=row.all_jobs_zscore_cat,
                living_wage_zscore=row.living_wage_zscore,
                living_wage_zscore_cat=row.living_wage_zscore_cat,
                not_living_wage_zscore=row.not_living_wage_zscore,
                not_living_wage_zscore_cat=row.not_living_wage_zscore_cat
            )
            
            feature = GeoJSONFeature(
                geometry=json.loads(row.geometry),
                properties=properties
            )
            features.append(feature)
        
        return features