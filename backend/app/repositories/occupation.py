from typing import List, Dict
from sqlalchemy import func, case, or_
from sqlalchemy.orm import Session
import json

from .base import BaseRepository
from ..models import OccupationLvlData, OccupationCode


class OccupationRepository(BaseRepository[OccupationLvlData]):
    """Repository for occupation-related data access"""

    @property
    def model(self) -> type[OccupationLvlData]:
        return OccupationLvlData

    def __init__(self, session: Session):
        super().__init__(session)
        self._code_model = OccupationCode

    def get_occupation_categories(self) -> List[Dict[str, str]]:
        """Get all unique occupation categories with their codes and names"""
        results = (
            self.session.query(
                OccupationCode.occupation_code.label("code"),
                case(
                    (
                        or_(
                            OccupationCode.occupation_name.is_(None),
                            OccupationCode.occupation_name == "",
                            func.trim(OccupationCode.occupation_name) == "",
                        ),
                        OccupationCode.occupation_code,
                    ),
                    else_=OccupationCode.occupation_name,
                ).label("name"),
            )
            .order_by(OccupationCode.occupation_code)
            .all()
        )

        return [{"code": r.code, "name": r.name} for r in results]

    def get_spatial_data_by_category(self, category: str) -> List[Dict]:
        """Get spatial data for a specific occupation category"""
        results = (
            self.session.query(
                OccupationLvlData.geoid,
                OccupationLvlData.openings_2024_zscore,
                OccupationLvlData.jobs_2024_zscore,
                OccupationLvlData.openings_2024_zscore_color,
                func.ST_AsGeoJSON(OccupationLvlData.geom).label("geometry"),
            )
            .filter(OccupationLvlData.category == category)
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
        """Check if an occupation category exists"""
        return (
            self.session.query(OccupationLvlData)
            .filter(OccupationLvlData.category == category)
            .first()
        ) is not None
