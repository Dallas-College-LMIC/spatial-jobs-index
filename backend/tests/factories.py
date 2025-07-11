"""
Test data factories using factory-boy.

These factories provide consistent test data generation for models.
"""
import factory
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker
from geoalchemy2.elements import WKTElement
import random

from app.models import OccupationLvlData, TTIClone, OccupationCode


fake = Faker()


class BaseFactory(SQLAlchemyModelFactory):
    """Base factory configuration."""
    
    class Meta:
        abstract = True
        sqlalchemy_session_persistence = "commit"


class OccupationCodeFactory(BaseFactory):
    """Factory for OccupationCode model."""
    
    class Meta:
        model = OccupationCode
    
    occupation_code = factory.Sequence(lambda n: f"{11 + n % 90:02d}-{1000 + n:04d}")
    occupation_name = factory.Faker("job")


class OccupationLvlDataFactory(BaseFactory):
    """Factory for OccupationLvlData model."""
    
    class Meta:
        model = OccupationLvlData
    
    category = factory.Faker(
        "random_element",
        elements=[
            "Healthcare Support",
            "Computer and Mathematical",
            "Education, Training, and Library",
            "Business and Financial Operations",
            "Construction and Extraction",
            "Food Preparation and Serving Related",
            "Office and Administrative Support",
            "Production",
            "Transportation and Material Moving",
            "Sales and Related",
            "Installation, Maintenance, and Repair",
            "Personal Care and Service",
            "Architecture and Engineering",
            "Life, Physical, and Social Science",
            "Arts, Design, Entertainment, Sports, and Media",
            "Management",
            "Healthcare Practitioners and Technical",
            "Protective Service",
            "Building and Grounds Cleaning and Maintenance",
            "Community and Social Service",
            "Legal",
            "Farming, Fishing, and Forestry"
        ]
    )


class TTICloneFactory(BaseFactory):
    """Factory for TTIClone model with spatial data."""
    
    class Meta:
        model = TTIClone
    
    # Generate a unique GEOID (census tract identifier)
    geoid = factory.Sequence(lambda n: f"48{str(n).zfill(9)}")
    
    # Z-scores typically range from -3 to 3
    all_jobs_zscore = factory.Faker(
        "pyfloat",
        left_digits=1,
        right_digits=2,
        positive=False,
        min_value=-3.0,
        max_value=3.0
    )
    
    # Category based on z-score
    all_jobs_zscore_cat = factory.LazyAttribute(
        lambda obj: TTICloneFactory._categorize_zscore(obj.all_jobs_zscore)
    )
    
    living_wage_zscore = factory.Faker(
        "pyfloat",
        left_digits=1,
        right_digits=2,
        positive=False,
        min_value=-3.0,
        max_value=3.0
    )
    
    living_wage_zscore_cat = factory.LazyAttribute(
        lambda obj: TTICloneFactory._categorize_zscore(obj.living_wage_zscore)
    )
    
    not_living_wage_zscore = factory.Faker(
        "pyfloat",
        left_digits=1,
        right_digits=2,
        positive=False,
        min_value=-3.0,
        max_value=3.0
    )
    
    not_living_wage_zscore_cat = factory.LazyAttribute(
        lambda obj: TTICloneFactory._categorize_zscore(obj.not_living_wage_zscore)
    )
    
    # Generate random point geometry (Dallas area coordinates)
    geom = factory.LazyFunction(
        lambda: WKTElement(
            f"POINT({random.uniform(-97.5, -96.5)} {random.uniform(32.5, 33.0)})",
            srid=4326
        )
    )
    
    @staticmethod
    def _categorize_zscore(zscore):
        """Categorize z-score into High/Medium/Low."""
        if zscore is None:
            return None
        if zscore >= 1.0:
            return "High"
        elif zscore >= -1.0:
            return "Medium"
        else:
            return "Low"
    
    @classmethod
    def create_batch_with_geometry(cls, size, session=None, **kwargs):
        """
        Create a batch of TTIClone objects with varied geometry types.
        
        This method creates points distributed across the Dallas-Fort Worth area.
        """
        instances = []
        
        # Define bounding box for Dallas-Fort Worth area
        min_lon, max_lon = -97.5, -96.5
        min_lat, max_lat = 32.5, 33.0
        
        for i in range(size):
            # Generate random coordinates within bounds
            lon = random.uniform(min_lon, max_lon)
            lat = random.uniform(min_lat, max_lat)
            
            # Create WKT geometry
            geom = WKTElement(f"POINT({lon} {lat})", srid=4326)
            
            # Override geometry in kwargs
            kwargs_copy = kwargs.copy()
            kwargs_copy['geom'] = geom
            
            # Create instance
            if session:
                instance = cls._create(model_class=cls._meta.model, session=session, **kwargs_copy)
            else:
                instance = cls.build(**kwargs_copy)
            
            instances.append(instance)
        
        return instances


class GeoJSONFeatureFactory(factory.Factory):
    """Factory for creating GeoJSON feature dictionaries."""
    
    class Meta:
        model = dict
    
    type = "Feature"
    
    geometry = factory.LazyFunction(
        lambda: {
            "type": "Point",
            "coordinates": [
                random.uniform(-97.5, -96.5),  # longitude
                random.uniform(32.5, 33.0)      # latitude
            ]
        }
    )
    
    properties = factory.LazyFunction(
        lambda: {
            "geoid": fake.numerify(text="###########"),
            "all_jobs_zscore": round(random.uniform(-3.0, 3.0), 2),
            "all_jobs_zscore_cat": random.choice(["High", "Medium", "Low"]),
            "living_wage_zscore": round(random.uniform(-3.0, 3.0), 2),
            "living_wage_zscore_cat": random.choice(["High", "Medium", "Low"]),
            "not_living_wage_zscore": round(random.uniform(-3.0, 3.0), 2),
            "not_living_wage_zscore_cat": random.choice(["High", "Medium", "Low"])
        }
    )


class GeoJSONFeatureCollectionFactory(factory.Factory):
    """Factory for creating GeoJSON FeatureCollection dictionaries."""
    
    class Meta:
        model = dict
    
    type = "FeatureCollection"
    
    features = factory.LazyFunction(
        lambda: [GeoJSONFeatureFactory() for _ in range(random.randint(5, 10))]
    )


# Utility functions for test data generation
def create_sample_occupation_data(session, count=10):
    """Create sample occupation data for testing."""
    occupations = [
        "Healthcare Support",
        "Computer and Mathematical",
        "Education, Training, and Library",
        "Business and Financial Operations",
        "Construction and Extraction",
        "Food Preparation and Serving Related",
        "Office and Administrative Support",
        "Production",
        "Transportation and Material Moving",
        "Sales and Related"
    ]
    
    # Configure factory to use the session
    OccupationLvlDataFactory._meta.sqlalchemy_session = session
    
    # Create unique occupations
    created = []
    for i in range(min(count, len(occupations))):
        occupation = OccupationLvlDataFactory(category=occupations[i])
        created.append(occupation)
    
    session.commit()
    return created


def create_sample_spatial_data(session, count=10):
    """Create sample spatial data for testing."""
    # Configure factory to use the session
    TTICloneFactory._meta.sqlalchemy_session = session
    
    # Create spatial data with varied z-scores
    spatial_data = TTICloneFactory.create_batch_with_geometry(count, session=session)
    
    session.commit()
    return spatial_data


def create_test_database_data(session):
    """
    Populate test database with comprehensive sample data.
    
    This function creates a variety of test data for integration testing.
    """
    # Create occupation data
    occupations = create_sample_occupation_data(session, count=15)
    
    # Create spatial data with various z-score combinations
    spatial_data = []
    
    # High performing areas
    for i in range(3):
        spatial_data.append(
            TTICloneFactory(
                all_jobs_zscore=random.uniform(1.5, 3.0),
                living_wage_zscore=random.uniform(1.5, 3.0),
                not_living_wage_zscore=random.uniform(-3.0, -1.5)
            )
        )
    
    # Medium performing areas
    for i in range(4):
        spatial_data.append(
            TTICloneFactory(
                all_jobs_zscore=random.uniform(-0.5, 0.5),
                living_wage_zscore=random.uniform(-0.5, 0.5),
                not_living_wage_zscore=random.uniform(-0.5, 0.5)
            )
        )
    
    # Low performing areas
    for i in range(3):
        spatial_data.append(
            TTICloneFactory(
                all_jobs_zscore=random.uniform(-3.0, -1.5),
                living_wage_zscore=random.uniform(-3.0, -1.5),
                not_living_wage_zscore=random.uniform(1.5, 3.0)
            )
        )
    
    session.commit()
    
    return {
        "occupations": occupations,
        "spatial_data": spatial_data
    }