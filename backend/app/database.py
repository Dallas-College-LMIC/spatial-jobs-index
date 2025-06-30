from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session, sessionmaker as SessionMaker
from pydantic import BaseModel
import os
from typing import Generator, Optional


class DatabaseConfig(BaseModel):
    username: str
    password: str
    url: str
    database: str

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """Create database config from environment variables"""
        required_vars = ["USERNAME", "PASS", "URL", "DB"]
        missing_vars = []

        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            raise RuntimeError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )

        return cls(
            username=os.getenv("USERNAME", ""),  # MyPy: provide default to ensure str
            password=os.getenv("PASS", ""),  # MyPy: provide default to ensure str
            url=os.getenv("URL", ""),  # MyPy: provide default to ensure str
            database=os.getenv("DB", ""),  # MyPy: provide default to ensure str
        )

    @property
    def database_url(self) -> str:
        """Get the database URL for psycopg2"""
        return (
            f"postgresql://{self.username}:{self.password}@{self.url}/{self.database}"
        )


# Global variables for database
engine: Optional[Engine] = None
session_maker: Optional[SessionMaker[Session]] = None


def init_database(config: DatabaseConfig):
    """Initialize the database engine and session maker"""
    global engine, session_maker

    engine = create_engine(
        config.database_url,
        echo=False,  # Set to True for SQL debugging
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
    )

    session_maker = sessionmaker(bind=engine, expire_on_commit=False)


def get_db_session() -> Generator[Session, None, None]:
    """Dependency to get database session"""
    if session_maker is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    session = session_maker()
    try:
        yield session
    finally:
        session.close()


def close_database():
    """Close database connections"""
    if engine:
        engine.dispose()
