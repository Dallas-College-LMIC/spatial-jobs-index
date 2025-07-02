"""Test helper utilities for handling database schema differences."""
from sqlalchemy import MetaData, Table, Column, String, Float
from sqlalchemy.orm import Session


def create_test_tables(engine):
    """
    Create test tables that mimic the production schema.
    
    This handles the difference between PostgreSQL schemas and SQLite.
    """
    metadata = MetaData()
    
    # Create occupation_lvl_data table without schema for SQLite
    Table(  # noqa: F841
        'occupation_lvl_data',
        metadata,
        Column('geoid', String, primary_key=True),
        Column('category', String, primary_key=True),
        Column('openings_2024_zscore', Float),
        Column('jobs_2024_zscore', Float),
        Column('openings_2024_zscore_color', String),
        Column('geom', String),  # Store as text in SQLite
    )
    
    # Create tti_clone table without schema for SQLite
    Table(  # noqa: F841
        'tti_clone',
        metadata,
        Column('geoid', String, primary_key=True),
        Column('all_jobs_zscore', Float),
        Column('all_jobs_zscore_cat', String),
        Column('living_wage_zscore', Float),
        Column('living_wage_zscore_cat', String),
        Column('not_living_wage_zscore', Float),
        Column('not_living_wage_zscore_cat', String),
        Column('geom', String),  # Store as text in SQLite
    )
    
    # Create all tables
    metadata.create_all(engine)
    
    return metadata


def insert_test_occupation_data(session: Session, data: list):
    """
    Insert test occupation data into the database.
    
    Args:
        session: SQLAlchemy session
        data: List of dicts with occupation data
    """
    for item in data:
        session.execute(
            "INSERT INTO occupation_lvl_data "
            "(geoid, category, openings_2024_zscore, jobs_2024_zscore, openings_2024_zscore_color, geom) "
            "VALUES (:geoid, :category, :openings_2024_zscore, :jobs_2024_zscore, :openings_2024_zscore_color, :geom)",
            {
                'geoid': item.get('geoid'),
                'category': item.get('category'),
                'openings_2024_zscore': item.get('openings_2024_zscore'),
                'jobs_2024_zscore': item.get('jobs_2024_zscore'),
                'openings_2024_zscore_color': item.get('openings_2024_zscore_color', ''),
                'geom': item.get('geom', '{}')
            }
        )
    session.commit()