from typing import List, Dict
from sqlalchemy import func, distinct, cast, String
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import json
import logging

from .base import BaseRepository
from ..models import SchoolOfLvlData
from ..config import DatabaseConfig


class SchoolOfStudyRepository(BaseRepository[SchoolOfLvlData]):
    """Repository for school of study-related data access"""

    @property
    def model(self) -> type[SchoolOfLvlData]:
        return SchoolOfLvlData

    def __init__(self, session: Session):
        super().__init__(session)

    def get_school_of_study_categories(self) -> List[Dict[str, str]]:
        """Get all unique school of study categories with their codes"""
        try:
            results = (
                self.session.query(distinct(SchoolOfLvlData.category))
                .order_by(SchoolOfLvlData.category)
                .all()
            )

            return [{"code": r[0]} for r in results]
        except SQLAlchemyError as e:
            logging.error(f"Database error in get_school_of_study_categories: {e}")
            raise

    def get_spatial_data_by_category(self, category: str) -> List[Dict]:
        """Get spatial data for a specific school of study category"""
        try:
            # Use configuration to determine database capabilities
            supports_postgis = DatabaseConfig.supports_postgis()

            if supports_postgis:
                # For PostgreSQL production, use PostGIS functions
                results = (
                    self.session.query(
                        cast(SchoolOfLvlData.geoid, String).label("geoid"),
                        SchoolOfLvlData.openings_2024_zscore,
                        SchoolOfLvlData.jobs_2024_zscore,
                        SchoolOfLvlData.openings_2024_zscore_color,
                        func.ST_AsGeoJSON(SchoolOfLvlData.geom).label("geometry"),
                    )
                    .filter(SchoolOfLvlData.category == category)
                    .all()
                )
            else:
                # For SQLite testing, geometry is stored as text
                results = (
                    self.session.query(
                        cast(SchoolOfLvlData.geoid, String).label("geoid"),
                        SchoolOfLvlData.openings_2024_zscore,
                        SchoolOfLvlData.jobs_2024_zscore,
                        SchoolOfLvlData.openings_2024_zscore_color,
                        SchoolOfLvlData.geom.label("geometry"),
                    )
                    .filter(SchoolOfLvlData.category == category)
                    .all()
                )

            features = []
            for row in results:
                # Handle geometry parsing - both environments return JSON strings
                try:
                    geometry = json.loads(row.geometry) if row.geometry else None
                except (json.JSONDecodeError, TypeError) as e:
                    logging.warning(
                        f"Failed to parse geometry for geoid {row.geoid}: {e}"
                    )
                    geometry = None

                features.append(
                    {
                        "type": "Feature",
                        "geometry": geometry,
                        "properties": {
                            "geoid": row.geoid,
                            "category": category,
                            "openings_2024_zscore": row.openings_2024_zscore,
                            "jobs_2024_zscore": row.jobs_2024_zscore,
                            "openings_2024_zscore_color": row.openings_2024_zscore_color,
                        },
                    }
                )

            return features
        except SQLAlchemyError as e:
            logging.error(f"Database error in get_spatial_data_by_category: {e}")
            raise

    def category_exists(self, category: str) -> bool:
        """Check if a school of study category exists"""
        try:
            return (
                self.session.query(SchoolOfLvlData)
                .filter(SchoolOfLvlData.category == category)
                .first()
            ) is not None
        except SQLAlchemyError as e:
            logging.error(f"Database error in category_exists: {e}")
            raise
