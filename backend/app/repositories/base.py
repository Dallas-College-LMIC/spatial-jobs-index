from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
import json

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Base repository providing common database operations"""

    def __init__(self, session: Session):
        self.session = session

    @property
    @abstractmethod
    def model(self) -> type[T]:
        """Return the SQLAlchemy model class"""
        pass

    def get_by_id(self, id: Any) -> Optional[T]:
        """Get a single record by primary key"""
        # Note: This assumes the model has an 'id' attribute
        # Subclasses should override if using different primary key
        return self.session.query(self.model).filter(self.model.id == id).first()  # type: ignore

    def get_all(self) -> List[T]:
        """Get all records"""
        return self.session.query(self.model).all()

    def create(self, **kwargs) -> T:
        """Create a new record"""
        instance = self.model(**kwargs)
        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)
        return instance

    def update(self, instance: T, **kwargs) -> T:
        """Update an existing record"""
        for key, value in kwargs.items():
            setattr(instance, key, value)
        self.session.commit()
        self.session.refresh(instance)
        return instance

    def delete(self, instance: T) -> None:
        """Delete a record"""
        self.session.delete(instance)
        self.session.commit()

    def get_geojson_geometry(self, geom_column) -> Optional[dict]:
        """Convert PostGIS geometry to GeoJSON format"""
        geojson_str = self.session.scalar(func.ST_AsGeoJSON(geom_column))
        return json.loads(geojson_str) if geojson_str else None
