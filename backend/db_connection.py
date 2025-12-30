"""
Database connection and session management
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
import os
from pathlib import Path
from dotenv import load_dotenv
from models import Base
import logging

# Load environment variables from project root
project_root = Path(__file__).parent.parent
dotenv_path = project_root / '.env'
load_dotenv(dotenv_path=dotenv_path)

logger = logging.getLogger(__name__)

# Database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://oncopurpose_user:oncopurpose_pass@localhost:3306/oncopurpose"
)

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,   # Recycle connections after 1 hour
    echo=False,          # Set to True for SQL logging
    future=True
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """
    Dependency for FastAPI to get database session
    Usage: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database():
    """
    Initialize database - create all tables
    """
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False


def test_connection():
    """
    Test database connection
    """
    try:
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            logger.info("✅ Database connection successful")
            return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


# Event listener for MySQL connection charset
@event.listens_for(engine, "connect")
def set_mysql_charset(dbapi_connection, connection_record):
    """Set charset to utf8mb4 for MySQL connections"""
    try:
        cursor = dbapi_connection.cursor()
        cursor.execute("SET NAMES utf8mb4")
        cursor.close()
    except Exception as e:
        logger.warning(f"Could not set charset: {e}")
