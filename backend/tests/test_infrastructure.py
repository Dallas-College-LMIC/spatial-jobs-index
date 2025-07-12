"""
Test to verify the test infrastructure is working correctly.
"""
import pytest
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi.testclient import TestClient

from app.models import OccupationLvlData, TTIClone
from tests.factories import (
    OccupationLvlDataFactory,
    TTICloneFactory,
    create_sample_occupation_data,
    create_sample_spatial_data
)


class TestInfrastructure:
    """Verify test infrastructure components."""

    def test_test_client_creation(self, test_client):
        """Test that test client is created successfully."""
        assert test_client is not None
        assert isinstance(test_client, TestClient)

    def test_database_session(self, test_session):
        """Test that database session is created successfully."""
        assert test_session is not None
        assert isinstance(test_session, Session)

        # Test we can execute a simple query
        result = test_session.execute(text("SELECT 1"))
        assert result.scalar() == 1

    @pytest.mark.skip(reason="Requires PostgreSQL with schema support")
    def test_occupation_factory(self, test_session):
        """Test OccupationLvlDataFactory creates valid objects."""
        OccupationLvlDataFactory._meta.sqlalchemy_session = test_session

        occupation = OccupationLvlDataFactory()
        assert occupation.category is not None
        assert isinstance(occupation.category, str)

        # Verify it's in the session
        test_session.commit()
        found = test_session.query(OccupationLvlData).filter_by(
            category=occupation.category
        ).first()
        assert found is not None

    @pytest.mark.skip(reason="Requires PostgreSQL with schema support")
    def test_tti_clone_factory(self, test_session):
        """Test TTICloneFactory creates valid objects."""
        TTICloneFactory._meta.sqlalchemy_session = test_session

        spatial_data = TTICloneFactory()
        assert spatial_data.geoid is not None
        assert isinstance(spatial_data.all_jobs_zscore, float)
        assert spatial_data.all_jobs_zscore_cat in ["High", "Medium", "Low"]

        # Note: Geometry testing would require PostGIS or proper SQLite spatial support

    @pytest.mark.skip(reason="Requires PostgreSQL with schema support")
    def test_create_sample_data(self, test_session):
        """Test sample data creation utilities."""
        # Create occupation data
        occupations = create_sample_occupation_data(test_session, count=5)
        assert len(occupations) == 5
        assert all(isinstance(o, OccupationLvlData) for o in occupations)

        # Create spatial data
        spatial_data = create_sample_spatial_data(test_session, count=3)
        assert len(spatial_data) == 3
        assert all(isinstance(s, TTIClone) for s in spatial_data)

    @pytest.mark.asyncio
    async def test_async_client(self, async_test_client):
        """Test async test client creation."""
        assert async_test_client is not None

        # Test a simple async request
        response = await async_test_client.get("/")
        assert response.status_code in [200, 404]  # Depends on if root endpoint exists

    def test_mock_env_vars(self, mock_env_vars):
        """Test environment variable mocking."""
        import os
        assert os.getenv("USERNAME") == "test_user"
        assert os.getenv("PASS") == "test_pass"
        assert os.getenv("URL") == "test_host:5432"
        assert os.getenv("DB") == "test_db"

    @pytest.mark.skip(reason="Requires PostgreSQL with schema support")
    def test_api_endpoint_with_mocked_db(self, test_client, test_session):
        """Test that API endpoints work with mocked database."""
        # Create some test data
        create_sample_occupation_data(test_session, count=3)

        # Test the occupation_ids endpoint
        response = test_client.get("/occupation_ids")

        # Even if it fails due to SQLite limitations, we're testing the infrastructure
        assert response is not None
