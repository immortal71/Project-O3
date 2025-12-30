"""
SQLite Database Connection for Production
Use this for deployment when MySQL is not available
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
import logging
from pathlib import Path
import os

logger = logging.getLogger(__name__)

# Database configuration
DB_FILE = Path(__file__).parent.parent / 'data' / 'oncopurpose.db'
DATABASE_URL = f'sqlite:///{DB_FILE}'

# Create engine with SQLite-specific settings
engine = None
SessionLocal = None
Base = declarative_base()

def init_sqlite_connection():
    """Initialize SQLite database connection"""
    global engine, SessionLocal
    
    try:
        # Ensure data directory exists
        DB_FILE.parent.mkdir(exist_ok=True)
        
        # Create engine with connection pooling
        engine = create_engine(
            DATABASE_URL,
            connect_args={
                "check_same_thread": False,  # Allow multi-threading
                "timeout": 30  # Timeout for locks
            },
            poolclass=StaticPool,  # Use static pool for SQLite
            echo=False
        )
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        logger.info(f"✅ SQLite database connected: {DB_FILE}")
        return True
        
    except Exception as e:
        logger.error(f"❌ SQLite connection failed: {str(e)}")
        return False


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection():
    """Test database connection and return status"""
    try:
        if not DB_FILE.exists():
            return {
                "connected": False,
                "error": "Database file not found. Run setup_sqlite_db.py first.",
                "type": "sqlite",
                "file": str(DB_FILE)
            }
        
        with engine.connect() as conn:
            # Test query
            result = conn.execute(text("SELECT COUNT(*) as count FROM drugs"))
            drug_count = result.fetchone()[0]
            
            result = conn.execute(text("SELECT COUNT(*) as count FROM research_papers"))
            paper_count = result.fetchone()[0]
            
            return {
                "connected": True,
                "type": "sqlite",
                "file": str(DB_FILE),
                "drugs": drug_count,
                "papers": paper_count,
                "size_mb": round(DB_FILE.stat().st_size / (1024 * 1024), 2)
            }
    except Exception as e:
        return {
            "connected": False,
            "error": str(e),
            "type": "sqlite",
            "file": str(DB_FILE)
        }


def get_drug_count():
    """Get total drug count from database"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM drugs"))
            return result.fetchone()[0]
    except:
        return 0


def get_paper_count():
    """Get total research paper count"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM research_papers"))
            return result.fetchone()[0]
    except:
        return 0


def search_drugs(query: str, limit: int = 20):
    """Search drugs in database"""
    try:
        with engine.connect() as conn:
            sql = text("""
                SELECT name, clinical_phase, target_name, disease_area, moa, indication
                FROM drugs
                WHERE name LIKE :query 
                   OR moa LIKE :query 
                   OR indication LIKE :query
                LIMIT :limit
            """)
            result = conn.execute(sql, {"query": f"%{query}%", "limit": limit})
            
            drugs = []
            for row in result:
                drugs.append({
                    "name": row[0],
                    "clinical_phase": row[1],
                    "target": row[2],
                    "disease_area": row[3],
                    "moa": row[4],
                    "indication": row[5]
                })
            
            return drugs
    except Exception as e:
        logger.error(f"Drug search failed: {str(e)}")
        return []


def search_papers(query: str = None, cancer_type: str = None, limit: int = 50):
    """Search research papers in database"""
    try:
        with engine.connect() as conn:
            where_clauses = []
            params = {"limit": limit}
            
            if query:
                where_clauses.append("(title LIKE :query OR abstract LIKE :query)")
                params["query"] = f"%{query}%"
            
            if cancer_type:
                where_clauses.append("cancer_types LIKE :cancer_type")
                params["cancer_type"] = f"%{cancer_type}%"
            
            where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
            
            sql = text(f"""
                SELECT pmid, title, author_string, journal, year, 
                       abstract, keywords, cancer_types, study_type, url
                FROM research_papers
                WHERE {where_sql}
                ORDER BY year DESC
                LIMIT :limit
            """)
            
            result = conn.execute(sql, params)
            
            papers = []
            for row in result:
                import json
                papers.append({
                    "pmid": row[0],
                    "title": row[1],
                    "author_string": row[2],
                    "journal": row[3],
                    "year": row[4],
                    "abstract": row[5],
                    "keywords": json.loads(row[6]) if row[6] else [],
                    "cancer_types": json.loads(row[7]) if row[7] else [],
                    "study_type": row[8],
                    "url": row[9]
                })
            
            return papers
    except Exception as e:
        logger.error(f"Paper search failed: {str(e)}")
        return []


# Initialize connection on import
init_sqlite_connection()
