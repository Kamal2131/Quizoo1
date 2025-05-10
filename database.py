from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite database URL — change this to PostgreSQL or MySQL URL in production
DATABASE_URL = "sqlite:///./users.db"

# Create SQLAlchemy engine with SQLite-specific setting
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}  # Required for SQLite with multiple threads (like in FastAPI)
)

# Configure session class bound to the engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models to inherit
Base = declarative_base()

# Dependency to get DB session (used with Depends in FastAPI)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
