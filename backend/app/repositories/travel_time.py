from typing import List, Dict
from sqlalchemy import func, text
import json

from .base import BaseRepository
from ..models import TTIClone
from ..constants import TIME_CATEGORY_COLORS, DEFAULT_COLOR


class TravelTimeRepository(BaseRepository[TTIClone]):
    """Repository for travel time and isochrone data access"""

    @property
    def model(self) -> type[TTIClone]:
        return TTIClone

    def get_wage_level_data(self, wage_type: str = "all_jobs") -> List[Dict]:
        """
        Get wage level data for all census tracts.

        Args:
            wage_type: Type of wage data - "all_jobs", "living_wage", or "not_living_wage"

        Returns:
            List of dictionaries with geoid, zscore, zscore_cat, and geometry
        """
        # Map wage type to column names
        column_mapping = {
            "all_jobs": (TTIClone.all_jobs_zscore, TTIClone.all_jobs_zscore_cat),
            "living_wage": (
                TTIClone.living_wage_zscore,
                TTIClone.living_wage_zscore_cat,
            ),
            "not_living_wage": (
                TTIClone.not_living_wage_zscore,
                TTIClone.not_living_wage_zscore_cat,
            ),
        }

        if wage_type not in column_mapping:
            raise ValueError(
                f"Invalid wage_type: {wage_type}. Must be one of: {list(column_mapping.keys())}"
            )

        zscore_col, zscore_cat_col = column_mapping[wage_type]

        results = self.session.query(
            TTIClone.geoid,
            zscore_col.label("zscore"),
            zscore_cat_col.label("zscore_cat"),
            func.ST_AsGeoJSON(TTIClone.geom).label("geometry"),
        ).all()

        features = []
        for row in results:
            features.append(
                {
                    "type": "Feature",
                    "geometry": json.loads(row.geometry) if row.geometry else None,
                    "properties": {
                        "geoid": str(int(float(row.geoid)))
                        if row.geoid is not None
                        else None,
                        f"{wage_type}_zscore": row.zscore,
                        f"{wage_type}_zscore_cat": row.zscore_cat,
                    },
                }
            )

        return features

    def get_all_wage_data(self) -> List[Dict]:
        """
        Get all wage level data (all_jobs, living_wage, not_living_wage) for all census tracts.

        Returns:
            List of GeoJSON features with all wage data
        """
        results = self.session.query(
            TTIClone.geoid,
            TTIClone.all_jobs_zscore,
            TTIClone.all_jobs_zscore_cat,
            TTIClone.living_wage_zscore,
            TTIClone.living_wage_zscore_cat,
            TTIClone.not_living_wage_zscore,
            TTIClone.not_living_wage_zscore_cat,
            func.ST_AsGeoJSON(TTIClone.geom).label("geometry"),
        ).all()

        features = []
        for row in results:
            features.append(
                {
                    "type": "Feature",
                    "geometry": json.loads(row.geometry) if row.geometry else None,
                    "properties": {
                        "geoid": str(int(float(row.geoid)))
                        if row.geoid is not None
                        else None,
                        "all_jobs_zscore": row.all_jobs_zscore,
                        "all_jobs_zscore_cat": row.all_jobs_zscore_cat,
                        "living_wage_zscore": row.living_wage_zscore,
                        "living_wage_zscore_cat": row.living_wage_zscore_cat,
                        "not_living_wage_zscore": row.not_living_wage_zscore,
                        "not_living_wage_zscore_cat": row.not_living_wage_zscore_cat,
                    },
                }
            )

        return features

    def get_isochrones_by_geoid(self, geoid: str) -> List[Dict]:
        """
        Get all isochrone bands for a specific census tract.

        Args:
            geoid: Census tract GEOID

        Returns:
            List of isochrone features with travel time categories and colors
        """

        # Query the isochrone table
        query = text("""
            SELECT
                geoid,
                traveltime_category,
                ST_AsGeoJSON(geom) as geometry
            FROM jsi_data.isochrone_table
            WHERE geoid = :geoid
            ORDER BY
                CASE traveltime_category
                    WHEN '< 5' THEN 1
                    WHEN '5~10' THEN 2
                    WHEN '10~15' THEN 3
                    WHEN '15~20' THEN 4
                    WHEN '20~25' THEN 5
                    WHEN '25~30' THEN 6
                    WHEN '30~45' THEN 7
                    WHEN '> 45' THEN 8
                END
        """)

        result = self.session.execute(query, {"geoid": geoid})
        features = []

        for row in result.fetchall():
            time_category = row.traveltime_category
            color = TIME_CATEGORY_COLORS.get(time_category, DEFAULT_COLOR)

            features.append(
                {
                    "type": "Feature",
                    "geometry": json.loads(row.geometry),
                    "properties": {
                        "geoid": str(row.geoid),
                        "time_category": time_category,
                        "color": color,
                    },
                }
            )

        return features

    def geoid_exists(self, geoid: str) -> bool:
        """Check if a GEOID exists in the TTIClone table"""
        return (
            self.session.query(TTIClone).filter(TTIClone.geoid == geoid).first()
        ) is not None

    def isochrone_exists(self, geoid: str) -> bool:
        """Check if isochrone data exists for a specific GEOID"""
        query = text("""
            SELECT 1
            FROM jsi_data.isochrone_table
            WHERE geoid = :geoid
            LIMIT 1
        """)

        result = self.session.execute(query, {"geoid": geoid}).first()
        return result is not None
