"""Configuration settings for the application."""

import os
from typing import Literal

DatabaseDialect = Literal["postgresql", "sqlite"]


class DatabaseConfig:
    """Database configuration settings."""

    @staticmethod
    def get_dialect() -> DatabaseDialect:
        """Get the database dialect based on environment."""
        if os.getenv("TESTING") == "1":
            return "sqlite"
        return "postgresql"

    @staticmethod
    def is_testing() -> bool:
        """Check if running in testing mode."""
        return os.getenv("TESTING") == "1"

    @staticmethod
    def supports_postgis() -> bool:
        """Check if the current database supports PostGIS functions."""
        return DatabaseConfig.get_dialect() == "postgresql"


class AppConfig:
    """Application configuration settings."""

    @staticmethod
    def get_log_level() -> str:
        """Get the logging level."""
        return os.getenv("LOG_LEVEL", "INFO")
