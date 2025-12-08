"""
Simple database setup for OpenAI analysis results
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()


class DrugAnalysis(Base):
    """Store drug repurposing analysis results"""
    __tablename__ = "drug_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    drug_name = Column(String(255), index=True, nullable=False)
    cancer_type = Column(String(255), index=True, nullable=False)
    molecular_target = Column(String(255), nullable=True)
    current_indication = Column(String(500), nullable=True)
    
    # Analysis settings
    analysis_mode = Column(String(50), nullable=False)  # fast or deep
    confidence_threshold = Column(Float, nullable=False)
    
    # Results
    confidence_score = Column(Float, nullable=True)
    mechanism_of_action = Column(Text, nullable=True)
    evidence_summary = Column(Text, nullable=True)
    safety_profile = Column(Text, nullable=True)
    market_opportunity = Column(Text, nullable=True)
    recommendation = Column(Text, nullable=True)
    
    # Full result as JSON
    full_result = Column(JSON, nullable=True)
    
    # Metadata
    model_used = Column(String(100), nullable=True)
    tokens_used = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<DrugAnalysis {self.drug_name} for {self.cancer_type}>"


def init_database():
    """Initialize SQLite database"""
    # Load environment variables
    from dotenv import load_dotenv
    from pathlib import Path
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)
    
    # Get database path from environment or use default
    db_path = os.getenv("DATABASE_URL", "sqlite:///./oncopurpose.db")
    
    print(f"📍 Database URL from env: {db_path}")
    
    # Create engine
    if db_path.startswith("sqlite"):
        # Extract file path from sqlite URL
        db_file = db_path.replace("sqlite+aiosqlite:///", "").replace("sqlite:///", "")
        
        # Ensure directory exists for relative paths (not for absolute paths like D:/)
        if not (db_file.startswith("D:/") or db_file.startswith("D:\\") or 
                db_file.startswith("C:/") or db_file.startswith("C:\\")):
            db_dir = os.path.dirname(db_file)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
        
        engine = create_engine(f"sqlite:///{db_file}")
        print(f"📂 Database file location: {os.path.abspath(db_file)}")
    else:
        engine = create_engine(db_path)
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    print(f"✅ Database initialized successfully")
    print(f"✅ Table created: drug_analyses")
    
    return engine


if __name__ == "__main__":
    # Initialize database
    engine = init_database()
    
    # Create session factory
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    # Check if table exists
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print(f"\n📊 Database tables: {tables}")
    print(f"\n✨ Database is ready for storing analysis results!")
    
    session.close()
