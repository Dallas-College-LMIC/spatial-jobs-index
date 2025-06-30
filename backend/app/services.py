from sqlalchemy.orm import Session
from sqlalchemy import select
from geoalchemy2.functions import ST_AsGeoJSON
from typing import List
import json

from .models import OccupationLvlData, TTIClone, SpatialFeatureProperties, GeoJSONFeature, OccupationSpatialProperties, OccupationGeoJSONFeature

class OccupationService:
    """Service for occupation-related operations"""
    
    @staticmethod
    def get_occupation_ids(session: Session) -> List[str]:
        """Get all distinct occupation categories"""
        result = session.execute(
            select(OccupationLvlData.category).distinct()
        )
        return [row[0] for row in result.fetchall()]
    
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