from typing import List, Dict
from sqlalchemy import func, distinct
from sqlalchemy.orm import Session
import json

from .base import BaseRepository
from ..models import SchoolOfLvlData, SchoolOfStudyCodes


class SchoolOfStudyRepository(BaseRepository[SchoolOfLvlData]):
    """Repository for school of study-related data access"""

    @property
    def model(self) -> type[SchoolOfLvlData]:
        return SchoolOfLvlData

    def __init__(self, session: Session):
        super().__init__(session)
        self._code_model = SchoolOfStudyCodes

    def get_school_of_study_categories(self) -> List[Dict[str, str]]:
        """Get all unique school of study categories with their codes and names"""
        results = (
            self.session.query(
                distinct(SchoolOfLvlData.category).label("code"),
                SchoolOfStudyCodes.school_name.label("name"),
            )
            .join(
                SchoolOfStudyCodes,
                SchoolOfLvlData.category == SchoolOfStudyCodes.school_code,
            )
            .order_by("name")
            .all()
        )

        return [{"code": r.code, "name": r.name} for r in results]

    def get_spatial_data_by_category(self, category: str) -> List[Dict]:
        """Get spatial data for a specific school of study category"""
        results = (
            self.session.query(
                SchoolOfLvlData.geoid,
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
            features.append(
                {
                    "type": "Feature",
                    "geometry": json.loads(row.geometry) if row.geometry else None,
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
