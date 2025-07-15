from typing import List, Dict
from sqlalchemy import func, distinct, cast, String
from sqlalchemy.orm import Session
import json

from .base import BaseRepository
from ..models import SchoolOfLvlData


class SchoolOfStudyRepository(BaseRepository[SchoolOfLvlData]):
    """Repository for school of study-related data access"""

    @property
    def model(self) -> type[SchoolOfLvlData]:
        return SchoolOfLvlData

    def __init__(self, session: Session):
        super().__init__(session)

    def get_school_of_study_categories(self) -> List[Dict[str, str]]:
        """Get all unique school of study categories with their codes"""
        results = (
            self.session.query(distinct(SchoolOfLvlData.category))
            .order_by(SchoolOfLvlData.category)
            .all()
        )

        return [{"code": r[0]} for r in results]

    def get_spatial_data_by_category(self, category: str) -> List[Dict]:
        """Get spatial data for a specific school of study category"""
        import os

        # Check if we're in testing mode (SQLite) or production (PostgreSQL)
        is_testing = os.getenv("TESTING") == "1"

        if is_testing:
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
        else:
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

        features = []
        for row in results:
            # Handle geometry parsing for both environments
            if is_testing:
                # In testing, geometry is already a JSON string
                geometry = json.loads(row.geometry) if row.geometry else None
            else:
                # In production, ST_AsGeoJSON returns a JSON string
                geometry = json.loads(row.geometry) if row.geometry else None

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

    def category_exists(self, category: str) -> bool:
        """Check if a school of study category exists"""
        return (
            self.session.query(SchoolOfLvlData)
            .filter(SchoolOfLvlData.category == category)
            .first()
        ) is not None
