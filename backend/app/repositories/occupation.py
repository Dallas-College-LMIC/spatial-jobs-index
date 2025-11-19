from typing import List, Dict
from sqlalchemy import func, case, or_, Float as SQLFloat
from sqlalchemy.orm import Session
import json

from .base import BaseRepository
from ..models import OccupationLvlData, OccupationCode, OccupationRawCounts


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
        """Get spatial data for a specific occupation category with raw counts"""
        results = (
            self.session.query(
                OccupationLvlData.geoid,
                OccupationLvlData.openings_2024_zscore,
                OccupationLvlData.jobs_2024_zscore,
                OccupationLvlData.openings_2024_zscore_color,
                func.ST_AsGeoJSON(OccupationLvlData.geom).label("geometry"),
                # Raw count fields from occupation_raw_counts
                OccupationRawCounts.jobs_2014_rawcount,
                OccupationRawCounts.jobs_2019_rawcount,
                OccupationRawCounts.jobs_2024_rawcount,
                OccupationRawCounts.jobs_2029_rawcount,
                OccupationRawCounts.percentile_50th_earnings_2023_rawcount,
                OccupationRawCounts.openings_2014_rawcount,
                OccupationRawCounts.openings_2019_rawcount,
                OccupationRawCounts.openings_2024_rawcount,
                OccupationRawCounts.openings_2029_rawcount,
                OccupationRawCounts.distance_minutes,
            )
            .outerjoin(
                OccupationRawCounts,
                (
                    func.cast(OccupationLvlData.geoid, SQLFloat)
                    == OccupationRawCounts.geoid
                )
                & (OccupationLvlData.category == OccupationRawCounts.category),
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
                        "geoid": str(row.geoid) if row.geoid is not None else None,
                        "category": category,
                        "openings_2024_zscore": row.openings_2024_zscore,
                        "jobs_2024_zscore": row.jobs_2024_zscore,
                        "openings_2024_zscore_color": row.openings_2024_zscore_color,
                        # Raw count fields
                        "jobs_2014_rawcount": row.jobs_2014_rawcount,
                        "jobs_2019_rawcount": row.jobs_2019_rawcount,
                        "jobs_2024_rawcount": row.jobs_2024_rawcount,
                        "jobs_2029_rawcount": row.jobs_2029_rawcount,
                        "percentile_50th_earnings_2023_rawcount": row.percentile_50th_earnings_2023_rawcount,
                        "openings_2014_rawcount": row.openings_2014_rawcount,
                        "openings_2019_rawcount": row.openings_2019_rawcount,
                        "openings_2024_rawcount": row.openings_2024_rawcount,
                        "openings_2029_rawcount": row.openings_2029_rawcount,
                        "distance_minutes": row.distance_minutes,
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
