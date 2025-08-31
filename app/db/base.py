"""
Database base configuration.

This module sets up SQLAlchemy's declarative base and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create the database engine
# echo=True in development shows SQL queries in console (great for learning!)
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG  # Shows SQL queries when DEBUG=True
)

# Create a session factory
# Sessions handle database transactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the declarative base
# All our models will inherit from this
Base = declarative_base()
