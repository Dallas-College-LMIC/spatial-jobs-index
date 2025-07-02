import logging
from typing import List, Dict, Optional
from functools import lru_cache
import os

from pyghtcast import lightcast
from app.config import LightcastConfig

logger = logging.getLogger(__name__)


class LightcastService:
    """Service for interacting with Lightcast API to fetch occupation data."""
    
    def __init__(self):
        """Initialize the Lightcast API connection."""
        config = LightcastConfig.from_env()
        self.client = lightcast.Lightcast(
            username=config.username,
            password=config.password
        )
        logger.info("Lightcast API client initialized")
    
    @lru_cache(maxsize=1, typed=False)
    def get_occupations_with_names(self) -> List[Dict[str, str]]:
        """
        Fetch occupation codes and names from Lightcast API.
        Results are cached in memory for the lifetime of the application.
        
        Returns:
            List of dictionaries with 'code' and 'name' keys
        """
        try:
            # Build query to get occupation codes and names
            query = self.client.build_query_corelmi(
                cols=['soc', 'title'],
                constraints=[]
            )
            
            # Query the occupation taxonomy dataset
            # Note: The exact dataset name may need adjustment based on API response
            results = self.client.query_corelmi('us.occupations', query)
            
            # Transform results to our expected format
            occupations = []
            for row in results.get('data', []):
                if 'soc' in row and 'title' in row:
                    occupations.append({
                        'code': row['soc'],
                        'name': row['title']
                    })
            
            logger.info(f"Successfully fetched {len(occupations)} occupations from Lightcast")
            return occupations
            
        except Exception as e:
            logger.error(f"Failed to fetch occupations from Lightcast: {str(e)}")
            # Return empty list to allow graceful degradation
            return []
    
    def get_occupation_by_code(self, soc_code: str) -> Optional[Dict[str, str]]:
        """Get a specific occupation by its SOC code."""
        occupations = self.get_occupations_with_names()
        for occ in occupations:
            if occ['code'] == soc_code:
                return occ
        return None


# Singleton instance
_lightcast_service: Optional[LightcastService] = None


def get_lightcast_service() -> LightcastService:
    """Get or create the singleton Lightcast service instance."""
    global _lightcast_service
    if _lightcast_service is None:
        _lightcast_service = LightcastService()
    return _lightcast_service