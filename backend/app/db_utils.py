"""Database utilities to handle differences between production and test environments."""
import os
from sqlalchemy import Table
from sqlalchemy.orm import class_mapper


def get_table_for_model(model_class):
    """
    Get the appropriate table reference for a model class.
    
    In testing with SQLite, we need to handle tables without schemas.
    In production with PostgreSQL, we use the full schema.table notation.
    """
    if os.environ.get('TESTING') == '1':
        # In test mode, return table without schema
        mapper = class_mapper(model_class)
        # Create a new table reference without schema
        return Table(
            mapper.mapped_table.name,
            mapper.mapped_table.metadata,
            *mapper.mapped_table.columns,
            extend_existing=True
        )
    else:
        # In production, use the model's table as-is
        return model_class.__table__