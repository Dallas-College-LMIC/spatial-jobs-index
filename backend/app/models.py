from sqlalchemy import Column, String, Float
from sqlalchemy.orm import DeclarativeBase
from geoalchemy2 import Geometry
from pydantic import BaseModel
from typing import List, Optional
import os

class Base(DeclarativeBase):
    pass

# Determine if we're in testing mode
TESTING = os.getenv('TESTING') == '1'

class OccupationLvlData(Base):
    __tablename__ = 'occupation_lvl_data'
    __table_args__ = {} if TESTING else {'schema': 'jsi_data'}
    
    geoid = Column(String, primary_key=True)
    category = Column(String, primary_key=True)
    openings_2024_zscore = Column(Float)
    jobs_2024_zscore = Column(Float)
    openings_2024_zscore_color = Column(String)
    geom = Column(Geometry('GEOMETRY'))

class TTIClone(Base):
    __tablename__ = 'tti_clone'
    __table_args__ = {} if TESTING else {'schema': 'jsi_data'}
    
    geoid = Column(String, primary_key=True)
    all_jobs_zscore = Column(Float)
    all_jobs_zscore_cat = Column(String)
    living_wage_zscore = Column(Float)
    living_wage_zscore_cat = Column(String)
    not_living_wage_zscore = Column(Float)
    not_living_wage_zscore_cat = Column(String)
    geom = Column(Geometry('GEOMETRY'))

# Pydantic response models
class OccupationIdsResponse(BaseModel):
    occupation_ids: List[str]

class OccupationItem(BaseModel):
    code: str
    name: str

class OccupationsResponse(BaseModel):
    occupations: List[OccupationItem]

class SpatialFeatureProperties(BaseModel):
    geoid: str
    all_jobs_zscore: Optional[float]
    all_jobs_zscore_cat: Optional[str]
    living_wage_zscore: Optional[float]
    living_wage_zscore_cat: Optional[str]
    not_living_wage_zscore: Optional[float]
    not_living_wage_zscore_cat: Optional[str]

class GeoJSONFeature(BaseModel):
    type: str = "Feature"
    geometry: dict
    properties: SpatialFeatureProperties

class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[GeoJSONFeature]

# Occupation-specific response models
class OccupationSpatialProperties(BaseModel):
    geoid: str
    category: str
    openings_2024_zscore: Optional[float]
    jobs_2024_zscore: Optional[float]
    openings_2024_zscore_color: Optional[str]

class OccupationGeoJSONFeature(BaseModel):
    type: str = "Feature"
    geometry: dict
    properties: OccupationSpatialProperties

class OccupationGeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[OccupationGeoJSONFeature]

# Isochrone Models
class IsochroneProperties(BaseModel):
    """Properties for isochrone features"""
    geoid: str
    time_category: str
    color: str

class IsochroneFeature(BaseModel):
    """GeoJSON feature for isochrone"""
    type: str = "Feature"
    geometry: dict
    properties: IsochroneProperties

class IsochroneFeatureCollection(BaseModel):
    """GeoJSON FeatureCollection for isochrones"""
    type: str = "FeatureCollection"
    features: List[IsochroneFeature]
