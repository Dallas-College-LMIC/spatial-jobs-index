"""Simple in-memory cache for occupation data with TTL support."""
import time
from typing import Dict, Optional, Any
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class SimpleCache:
    """Simple in-memory cache with TTL support."""
    
    def __init__(self):
        self._cache: Dict[str, tuple[Any, float]] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        if key in self._cache:
            value, expiry = self._cache[key]
            if time.time() < expiry:
                return value
            else:
                # Remove expired entry
                del self._cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl_seconds: int):
        """Set value in cache with TTL."""
        expiry = time.time() + ttl_seconds
        self._cache[key] = (value, expiry)
    
    def clear(self):
        """Clear all cache entries."""
        self._cache.clear()


# Global cache instance
_cache = SimpleCache()


def cache_with_ttl(ttl_seconds: int = 86400):  # Default 24 hours
    """Decorator to cache function results with TTL."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Check cache first
            cached_value = _cache.get(cache_key)
            if cached_value is not None:
                logger.info(f"Cache hit for {func.__name__}")
                return cached_value
            
            # Call function and cache result
            logger.info(f"Cache miss for {func.__name__}, calling function")
            result = func(*args, **kwargs)
            _cache.set(cache_key, result, ttl_seconds)
            
            return result
        return wrapper
    return decorator


# Static occupation names mapping as fallback
# This is a subset of common SOC codes with their names
# In production, this would be populated from Lightcast API
OCCUPATION_NAMES = {
    "11-1021": "General and Operations Managers",
    "11-2022": "Sales Managers",
    "11-3021": "Computer and Information Systems Managers",
    "11-3031": "Financial Managers",
    "11-3071": "Transportation, Storage, and Distribution Managers",
    "11-3121": "Human Resources Managers",
    "11-9021": "Construction Managers",
    "11-9041": "Architectural and Engineering Managers",
    "13-1041": "Compliance Officers",
    "13-1111": "Management Analysts",
    "13-1161": "Market Research Analysts and Marketing Specialists",
    "13-2011": "Accountants and Auditors",
    "13-2051": "Financial Analysts",
    "15-1241": "Computer Network Architects",
    "15-1251": "Computer Programmers",
    "15-1252": "Software Developers",
    "15-1299": "Computer Occupations, All Other",
    "15-2031": "Operations Research Analysts",
    "15-2051": "Data Scientists",
    "17-2051": "Civil Engineers",
    "17-2071": "Electrical Engineers",
    "17-2072": "Electronics Engineers, Except Computer",
    "17-2112": "Industrial Engineers",
    "17-2141": "Mechanical Engineers",
    "19-1021": "Biochemists and Biophysicists",
    "19-2041": "Environmental Scientists and Specialists",
    "19-3094": "Political Scientists",
    "19-4061": "Social Science Research Assistants",
    "21-1015": "Rehabilitation Counselors",
    "21-1022": "Healthcare Social Workers",
    "23-1011": "Lawyers",
    "25-2021": "Elementary School Teachers",
    "25-2031": "Secondary School Teachers",
    "25-2051": "Special Education Teachers",
    "25-3099": "Teachers and Instructors, All Other",
    "25-9021": "Farm and Home Management Educators",
    "27-1019": "Artists and Related Workers, All Other",
    "27-3031": "Public Relations Specialists",
    "29-1011": "Chiropractors",
    "29-1021": "Dentists, General",
    "29-1141": "Registered Nurses",
    "29-1171": "Nurse Practitioners",
    "29-2021": "Dental Hygienists",
    "29-2061": "Licensed Practical and Licensed Vocational Nurses",
    "31-9091": "Dental Assistants",
    "31-9092": "Medical Assistants",
    "33-3012": "Correctional Officers and Jailers",
    "33-3021": "Detectives and Criminal Investigators",
    "33-3051": "Police and Sheriff's Patrol Officers",
    "33-9032": "Security Guards",
    "35-1011": "Chefs and Head Cooks",
    "35-2011": "Cooks, Fast Food",
    "35-2014": "Cooks, Restaurant",
    "35-3011": "Bartenders",
    "35-3023": "Fast Food and Counter Workers",
    "37-2011": "Janitors and Cleaners",
    "39-3031": "Ushers, Lobby Attendants, and Ticket Takers",
    "39-5012": "Hairdressers, Hairstylists, and Cosmetologists",
    "39-9031": "Fitness Trainers and Aerobics Instructors",
    "41-1011": "First-Line Supervisors of Retail Sales Workers",
    "41-2011": "Cashiers",
    "41-2031": "Retail Salespersons",
    "41-3091": "Sales Representatives of Services",
    "41-4012": "Sales Representatives, Wholesale and Manufacturing",
    "43-3021": "Billing and Posting Clerks",
    "43-3031": "Bookkeeping, Accounting, and Auditing Clerks",
    "43-4051": "Customer Service Representatives",
    "43-4171": "Receptionists and Information Clerks",
    "43-5061": "Production, Planning, and Expediting Clerks",
    "43-6011": "Executive Secretaries and Executive Administrative Assistants",
    "43-6014": "Secretaries and Administrative Assistants",
    "43-9061": "Office Clerks, General",
    "45-2041": "Graders and Sorters, Agricultural Products",
    "47-1011": "First-Line Supervisors of Construction Trades",
    "47-2031": "Carpenters",
    "47-2061": "Construction Laborers",
    "47-2073": "Operating Engineers and Other Construction Equipment Operators",
    "47-2111": "Electricians",
    "47-2152": "Plumbers, Pipefitters, and Steamfitters",
    "49-1011": "First-Line Supervisors of Mechanics",
    "49-3023": "Automotive Service Technicians and Mechanics",
    "49-3031": "Bus and Truck Mechanics and Diesel Engine Specialists",
    "49-9021": "Heating, Air Conditioning, and Refrigeration Mechanics",
    "49-9071": "Maintenance and Repair Workers, General",
    "51-1011": "First-Line Supervisors of Production Workers",
    "51-2092": "Team Assemblers",
    "51-3011": "Bakers",
    "51-4041": "Machinists",
    "51-4121": "Welders, Cutters, Solderers, and Brazers",
    "51-8031": "Water and Wastewater Treatment Plant Operators",
    "51-9061": "Inspectors, Testers, Sorters, Samplers, and Weighers",
    "51-9161": "Computer Numerically Controlled Tool Operators",
    "51-9198": "Helpers--Production Workers",
    "53-3032": "Heavy and Tractor-Trailer Truck Drivers",
    "53-3033": "Light Truck Drivers",
    "53-3052": "Bus Drivers, Transit and Intercity",
    "53-3053": "Shuttle Drivers and Chauffeurs",
    "53-7051": "Industrial Truck and Tractor Operators",
    "53-7061": "Cleaners of Vehicles and Equipment",
    "53-7062": "Laborers and Freight, Stock, and Material Movers",
    "53-7065": "Stockers and Order Fillers",
    "99-9999": "All Other Occupations"
}