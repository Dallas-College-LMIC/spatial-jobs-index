from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
import json
from ..logging_config import StructuredLogger

T = TypeVar("T")

logger = StructuredLogger(__name__)


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
        """
        Get a single record by primary key.

        Note: This method assumes the model has a single 'id' primary key.
        Models with composite primary keys should override this method.
        """
        try:
            # Check if the model has an 'id' attribute
            if not hasattr(self.model, "id"):
                raise NotImplementedError(
                    f"Model {self.model.__name__} does not have an 'id' attribute. "
                    "Override get_by_id() method in the repository subclass."
                )
            return self.session.query(self.model).filter(self.model.id == id).first()  # type: ignore
        except SQLAlchemyError:
            logger.error(
                "Database error in get_by_id",
                exc_info=True,
                extra={"operation": "get_by_id", "id": str(id)},
            )
            raise

    def get_all(self) -> List[T]:
        """Get all records"""
        try:
            return self.session.query(self.model).all()
        except SQLAlchemyError:
            logger.error(
                "Database error in get_all",
                exc_info=True,
                extra={"operation": "get_all"},
            )
            raise

    def create(self, **kwargs: Any) -> T:
        """
        Create a new record.

        Note: This method does not automatically commit. Call session.commit()
        explicitly to persist changes or use the session's transaction management.
        """
        try:
            instance = self.model(**kwargs)
            self.session.add(instance)
            return instance
        except SQLAlchemyError:
            logger.error(
                "Database error in create",
                exc_info=True,
                extra={"operation": "create", "kwargs": str(kwargs)},
            )
            self.session.rollback()
            raise

    def update(self, instance: T, **kwargs: Any) -> T:
        """
        Update an existing record.

        Note: This method does not automatically commit. Call session.commit()
        explicitly to persist changes or use the session's transaction management.
        """
        try:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            return instance
        except SQLAlchemyError:
            logger.error(
                "Database error in update",
                exc_info=True,
                extra={"operation": "update", "kwargs": str(kwargs)},
            )
            self.session.rollback()
            raise

    def delete(self, instance: T) -> None:
        """
        Delete a record.

        Note: This method does not automatically commit. Call session.commit()
        explicitly to persist changes or use the session's transaction management.
        """
        try:
            self.session.delete(instance)
        except SQLAlchemyError:
            logger.error(
                "Database error in delete", exc_info=True, extra={"operation": "delete"}
            )
            self.session.rollback()
            raise

    def get_geojson_geometry(self, geom_column: Any) -> Optional[dict]:
        """Convert PostGIS geometry to GeoJSON format"""
        try:
            geojson_str = self.session.scalar(func.ST_AsGeoJSON(geom_column))
            return json.loads(geojson_str) if geojson_str else None
        except (SQLAlchemyError, json.JSONDecodeError):
            logger.error(
                "Error converting geometry to GeoJSON",
                exc_info=True,
                extra={"operation": "get_geojson_geometry"},
            )
            return None
