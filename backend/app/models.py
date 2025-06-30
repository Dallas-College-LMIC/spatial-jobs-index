from sqlalchemy import Column, String, Float
from sqlalchemy.orm import DeclarativeBase
from geoalchemy2 import Geometry
from pydantic import BaseModel
from typing import List, Optional

class Base(DeclarativeBase):
    pass

class OccupationLvlData(Base):
    __tablename__ = 'occupation_lvl_data'
    __table_args__ = {'schema': 'jsi_data'}
    
    geoid = Column(String, primary_key=True)
    category = Column(String, primary_key=True)
    openings_2024_zscore = Column(Float)
    jobs_2024_zscore = Column(Float)
    openings_2024_zscore_color = Column(String)
    geom = Column(Geometry('GEOMETRY'))

class TTIClone(Base):
    __tablename__ = 'tti_clone'
    __table_args__ = {'schema': 'jsi_data'}
    
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