"""
Lightcast API client implementation.
This module provides a simple HTTP client for the Lightcast API
without relying on the problematic pyghtcast library.
"""

import json
import logging
import requests
from typing import List, Dict, Optional
from functools import lru_cache

from app.config import LightcastConfig

logger = logging.getLogger(__name__)


class LightcastAPIClient:
    """Direct HTTP client for Lightcast API."""
    
    BASE_URL = "https://auth.emsicloud.com"
    API_URL = "https://emsiservices.com"
    
    def __init__(self):
        """Initialize the Lightcast API client."""
        self.config = LightcastConfig.from_env()
        self.token = None
        self.token_expires = 0
        
    def _authenticate(self) -> str:
        """Authenticate with Lightcast API and get access token."""
        auth_url = f"{self.BASE_URL}/connect/token"
        
        data = {
            "client_id": self.config.username,
            "client_secret": self.config.password,
            "grant_type": "client_credentials",
            "scope": "emsi_open"
        }
        
        try:
            response = requests.post(auth_url, data=data)
            response.raise_for_status()
            
            auth_data = response.json()
            self.token = auth_data.get("access_token")
            self.token_expires = auth_data.get("expires_in", 3600)
            
            logger.info("Successfully authenticated with Lightcast API")
            return self.token
            
        except requests.RequestException as e:
            logger.error(f"Failed to authenticate with Lightcast API: {str(e)}")
            raise
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication token."""
        if not self.token:
            self._authenticate()
            
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    @lru_cache(maxsize=1)
    def get_occupations(self) -> List[Dict[str, str]]:
        """
        Fetch occupation codes and names from Lightcast API.
        
        Returns:
            List of dictionaries with 'code' and 'name' keys
        """
        try:
            # For now, return an extended static mapping
            # This will be replaced with actual API calls once we resolve the dependency issues
            return self._get_extended_occupation_mapping()
            
        except Exception as e:
            logger.error(f"Failed to fetch occupations: {str(e)}")
            return []
    
    def _get_extended_occupation_mapping(self) -> List[Dict[str, str]]:
        """
        Get extended occupation mapping.
        This combines our static mapping with additional common occupations.
        """
        # Import the static mapping
        from app.occupation_cache import OCCUPATION_NAMES
        
        # Convert to list format
        occupations = []
        for code, name in OCCUPATION_NAMES.items():
            occupations.append({
                'code': code,
                'name': name
            })
        
        # Add additional common occupations not in the static list
        additional_occupations = {
            "11-1011": "Chief Executives",
            "11-2011": "Advertising and Promotions Managers",
            "11-2021": "Marketing Managers",
            "11-3061": "Purchasing Managers",
            "11-3131": "Training and Development Managers",
            "11-9013": "Farmers, Ranchers, and Other Agricultural Managers",
            "11-9032": "Education Administrators, Elementary and Secondary School",
            "11-9033": "Education Administrators, Postsecondary",
            "11-9039": "Education Administrators, All Other",
            "11-9051": "Food Service Managers",
            "11-9061": "Funeral Service Managers",
            "11-9081": "Lodging Managers",
            "11-9111": "Medical and Health Services Managers",
            "11-9121": "Natural Sciences Managers",
            "11-9141": "Property, Real Estate, and Community Association Managers",
            "11-9151": "Social and Community Service Managers",
            "11-9199": "Managers, All Other",
            "13-1011": "Agents and Business Managers of Artists, Performers, and Athletes",
            "13-1021": "Buyers and Purchasing Agents, Farm Products",
            "13-1022": "Wholesale and Retail Buyers, Except Farm Products",
            "13-1023": "Purchasing Agents, Except Wholesale, Retail, and Farm Products",
            "13-1031": "Claims Adjusters, Examiners, and Investigators",
            "13-1051": "Cost Estimators",
            "13-1071": "Human Resources Specialists",
            "13-1081": "Logisticians",
            "13-1121": "Meeting, Convention, and Event Planners",
            "13-1131": "Fundraisers",
            "13-1141": "Compensation, Benefits, and Job Analysis Specialists",
            "13-1151": "Training and Development Specialists",
            "13-1199": "Business Operations Specialists, All Other",
            "13-2021": "Appraisers and Assessors of Real Estate",
            "13-2031": "Budget Analysts",
            "13-2041": "Credit Analysts",
            "13-2052": "Personal Financial Advisors",
            "13-2053": "Insurance Underwriters",
            "13-2061": "Financial Examiners",
            "13-2071": "Credit Counselors",
            "13-2072": "Loan Officers",
            "13-2081": "Tax Examiners and Collectors, and Revenue Agents",
            "13-2082": "Tax Preparers",
            "13-2099": "Financial Specialists, All Other",
            "15-1211": "Computer Systems Analysts",
            "15-1212": "Information Security Analysts",
            "15-1221": "Computer and Information Research Scientists",
            "15-1231": "Computer Network Support Specialists",
            "15-1232": "Computer User Support Specialists",
            "15-1242": "Database Administrators",
            "15-1243": "Database Architects",
            "15-1244": "Network and Computer Systems Administrators",
            "15-1253": "Software Quality Assurance Analysts and Testers",
            "15-1254": "Web Developers",
            "15-1255": "Web and Digital Interface Designers",
            "15-2011": "Actuaries",
            "15-2021": "Mathematicians",
            "15-2041": "Statisticians",
            "15-2099": "Mathematical Science Occupations, All Other",
            "17-1011": "Architects, Except Landscape and Naval",
            "17-1012": "Landscape Architects",
            "17-1021": "Cartographers and Photogrammetrists",
            "17-1022": "Surveyors",
            "17-2011": "Aerospace Engineers",
            "17-2021": "Agricultural Engineers",
            "17-2031": "Bioengineers and Biomedical Engineers",
            "17-2041": "Chemical Engineers",
            "17-2061": "Computer Hardware Engineers",
            "17-2081": "Environmental Engineers",
            "17-2111": "Health and Safety Engineers, Except Mining Safety Engineers and Inspectors",
            "17-2121": "Marine Engineers and Naval Architects",
            "17-2131": "Materials Engineers",
            "17-2151": "Mining and Geological Engineers, Including Mining Safety Engineers",
            "17-2161": "Nuclear Engineers",
            "17-2171": "Petroleum Engineers",
            "17-2199": "Engineers, All Other",
            "17-3011": "Architectural and Civil Drafters",
            "17-3012": "Electrical and Electronics Drafters",
            "17-3013": "Mechanical Drafters",
            "17-3019": "Drafters, All Other",
            "17-3021": "Aerospace Engineering and Operations Technologists and Technicians",
            "17-3022": "Civil Engineering Technologists and Technicians",
            "17-3023": "Electrical and Electronic Engineering Technologists and Technicians",
            "17-3024": "Electro-Mechanical and Mechatronics Technologists and Technicians",
            "17-3025": "Environmental Engineering Technologists and Technicians",
            "17-3026": "Industrial Engineering Technologists and Technicians",
            "17-3027": "Mechanical Engineering Technologists and Technicians",
            "17-3028": "Calibration Technologists and Technicians",
            "17-3029": "Engineering Technologists and Technicians, Except Drafters, All Other",
            "17-3031": "Surveying and Mapping Technicians",
            "19-1011": "Animal Scientists",
            "19-1012": "Food Scientists and Technologists",
            "19-1013": "Soil and Plant Scientists",
            "19-1021": "Biochemists and Biophysicists",
            "19-1022": "Microbiologists",
            "19-1023": "Zoologists and Wildlife Biologists",
            "19-1029": "Biological Scientists, All Other",
            "19-1031": "Conservation Scientists",
            "19-1032": "Foresters",
            "19-1041": "Epidemiologists",
            "19-1042": "Medical Scientists, Except Epidemiologists",
            "19-1099": "Life Scientists, All Other",
            "19-2011": "Astronomers",
            "19-2012": "Physicists",
            "19-2021": "Atmospheric and Space Scientists",
            "19-2031": "Chemists",
            "19-2032": "Materials Scientists",
            "19-2042": "Geoscientists, Except Hydrologists and Geographers",
            "19-2043": "Hydrologists",
            "19-2099": "Physical Scientists, All Other",
            "19-3011": "Economists",
            "19-3021": "Market Research Analysts and Marketing Specialists",
            "19-3022": "Survey Researchers",
            "19-3031": "Clinical, Counseling, and School Psychologists",
            "19-3032": "Industrial-Organizational Psychologists",
            "19-3039": "Psychologists, All Other",
            "19-3041": "Sociologists",
            "19-3051": "Urban and Regional Planners",
            "19-3091": "Anthropologists and Archeologists",
            "19-3092": "Geographers",
            "19-3093": "Historians",
            "19-3099": "Social Scientists and Related Workers, All Other",
            "19-4011": "Agricultural and Food Science Technicians",
            "19-4012": "Agricultural Technicians",
            "19-4013": "Food Science Technicians",
            "19-4021": "Biological Technicians",
            "19-4031": "Chemical Technicians",
            "19-4041": "Geological and Hydrologic Technicians",
            "19-4042": "Environmental Science and Protection Technicians, Including Health",
            "19-4043": "Geological Technicians, Except Hydrologic Technicians",
            "19-4044": "Hydrologic Technicians",
            "19-4051": "Nuclear Technicians",
            "19-4052": "Nuclear Monitoring Technicians",
            "19-4053": "Nuclear Technicians",
            "19-4061": "Social Science Research Assistants",
            "19-4062": "Statistical Assistants",
            "19-4071": "Forest and Conservation Technicians",
            "19-4072": "Forest and Conservation Technicians",
            "19-4091": "Environmental Science and Protection Technicians, Including Health",
            "19-4092": "Forensic Science Technicians",
            "19-4093": "Forest and Conservation Technicians",
            "19-4099": "Life, Physical, and Social Science Technicians, All Other"
        }
        
        # Add additional occupations if not already present
        existing_codes = {occ['code'] for occ in occupations}
        for code, name in additional_occupations.items():
            if code not in existing_codes:
                occupations.append({
                    'code': code,
                    'name': name
                })
        
        # Sort by code
        occupations.sort(key=lambda x: x['code'])
        
        return occupations


# Singleton instance
_client: Optional[LightcastAPIClient] = None


def get_lightcast_client() -> LightcastAPIClient:
    """Get or create the singleton Lightcast API client."""
    global _client
    if _client is None:
        _client = LightcastAPIClient()
    return _client