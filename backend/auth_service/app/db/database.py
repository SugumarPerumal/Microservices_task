
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config.settings import settings


# Create database engine
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    echo=False
)


# Create database session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass


# Database dependency for FastAPI
def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
