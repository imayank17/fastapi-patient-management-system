"""
Database configuration module.

Sets up SQLAlchemy with SQLite for the Patient Management System.
Provides engine, session factory, Base class, and a dependency
function for injecting DB sessions into route handlers.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite database file will be created in the project root
DATABASE_URL = "sqlite:///./patients.db"

# Create the SQLAlchemy engine
# check_same_thread=False is needed for SQLite with FastAPI (multi-threaded)
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create a session factory - each call to SessionLocal() gives a new session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all SQLAlchemy models
Base = declarative_base()


def get_db():
    """
    Dependency function that provides a database session.
    
    Usage in routes:
        def my_route(db: Session = Depends(get_db)):
    
    The session is automatically closed after the request is done.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
