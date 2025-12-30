"""
Database Setup for Production Deployment
Creates SQLite database for multi-user webapp deployment
"""

import sqlite3
import json
import os
from pathlib import Path

# Database file location
DB_FILE = Path(__file__).parent.parent / 'data' / 'oncopurpose.db'
DATA_DIR = Path(__file__).parent.parent / 'data'

def create_database():
    """Create SQLite database with all necessary tables"""
    
    # Ensure data directory exists
    DATA_DIR.mkdir(exist_ok=True)
    
    # Connect to database (creates if doesn't exist)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    print(f"📊 Creating database at: {DB_FILE}")
    
    # Drop existing tables (for clean setup)
    cursor.execute("DROP TABLE IF EXISTS drugs")
    cursor.execute("DROP TABLE IF EXISTS research_papers")
    cursor.execute("DROP TABLE IF EXISTS clinical_trials")
    cursor.execute("DROP TABLE IF EXISTS discovery_results")
    cursor.execute("DROP TABLE IF EXISTS user_searches")
    
    # 1. Drugs table
    cursor.execute("""
        CREATE TABLE drugs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            clinical_phase TEXT,
            target_name TEXT,
            disease_area TEXT,
            moa TEXT,
            indication TEXT,
            source TEXT,
            smiles TEXT,
            is_oncology BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_json TEXT
        )
    """)
    print("✅ Created drugs table")
    
    # 2. Research Papers table
    cursor.execute("""
        CREATE TABLE research_papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pmid TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            authors TEXT,
            author_string TEXT,
            abstract TEXT,
            journal TEXT,
            publication_date TEXT,
            year INTEGER,
            keywords TEXT,
            cancer_types TEXT,
            study_type TEXT,
            url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✅ Created research_papers table")
    
    # 3. Clinical Trials table
    cursor.execute("""
        CREATE TABLE clinical_trials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nct_id TEXT UNIQUE NOT NULL,
            title TEXT,
            phase TEXT,
            status TEXT,
            enrollment INTEGER,
            sponsor TEXT,
            start_date TEXT,
            completion_date TEXT,
            primary_outcome TEXT,
            drug_name TEXT,
            disease TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✅ Created clinical_trials table")
    
    # 4. Discovery Results (cached analysis results)
    cursor.execute("""
        CREATE TABLE discovery_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            drug_name TEXT NOT NULL,
            cancer_type TEXT NOT NULL,
            confidence_score REAL,
            clinical_phase TEXT,
            evidence_level TEXT,
            market_potential TEXT,
            analysis_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(drug_name, cancer_type)
        )
    """)
    print("✅ Created discovery_results table")
    
    # 5. User Searches (analytics)
    cursor.execute("""
        CREATE TABLE user_searches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            search_type TEXT,
            search_query TEXT,
            results_count INTEGER,
            user_ip TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✅ Created user_searches table")
    
    # Create indexes for better query performance
    cursor.execute("CREATE INDEX idx_drugs_name ON drugs(name)")
    cursor.execute("CREATE INDEX idx_drugs_oncology ON drugs(is_oncology)")
    cursor.execute("CREATE INDEX idx_papers_pmid ON research_papers(pmid)")
    cursor.execute("CREATE INDEX idx_papers_year ON research_papers(year)")
    cursor.execute("CREATE INDEX idx_trials_nct ON clinical_trials(nct_id)")
    cursor.execute("CREATE INDEX idx_discovery_drug ON discovery_results(drug_name)")
    print("✅ Created indexes")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Database created successfully!")
    print(f"📍 Location: {DB_FILE.absolute()}")
    print(f"💾 Size: {DB_FILE.stat().st_size if DB_FILE.exists() else 0} bytes")
    
    return DB_FILE


def load_drugs_from_json():
    """Load drugs from JSON files into database"""
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Load Broad Institute data
    broad_file = DATA_DIR / 'broad_repurposing_drugs_20200324.txt'
    if broad_file.exists():
        print(f"\n📥 Loading drugs from {broad_file.name}...")
        
        import csv
        with open(broad_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            drugs_loaded = 0
            
            for row in reader:
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO drugs 
                        (name, clinical_phase, target_name, disease_area, moa, indication, source, smiles, data_json)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        row.get('pert_iname', ''),
                        row.get('clinical_phase', ''),
                        row.get('target', ''),
                        row.get('disease_area', ''),
                        row.get('moa', ''),
                        row.get('indication', ''),
                        'Broad Institute',
                        row.get('InChIKey', ''),
                        json.dumps(row)
                    ))
                    drugs_loaded += 1
                except Exception as e:
                    continue
        
        conn.commit()
        print(f"✅ Loaded {drugs_loaded} drugs from Broad Institute")
    
    # Load oncology compounds
    oncology_file = DATA_DIR / 'oncology_compounds.json'
    if oncology_file.exists():
        print(f"\n📥 Loading oncology compounds from {oncology_file.name}...")
        
        with open(oncology_file, 'r', encoding='utf-8') as f:
            oncology_data = json.load(f)
            oncology_loaded = 0
            
            for compound in oncology_data.get('compounds', []):
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO drugs 
                        (name, clinical_phase, target_name, moa, indication, source, is_oncology, data_json)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        compound.get('name', ''),
                        compound.get('phase', ''),
                        compound.get('target', ''),
                        compound.get('mechanism', ''),
                        compound.get('indication', ''),
                        'Oncology Database',
                        1,
                        json.dumps(compound)
                    ))
                    oncology_loaded += 1
                except Exception as e:
                    continue
        
        conn.commit()
        print(f"✅ Loaded {oncology_loaded} oncology compounds")
    
    conn.close()


def load_research_papers():
    """Load research papers from JSON into database"""
    
    papers_file = DATA_DIR / 'research_papers' / 'pubmed_papers.json'
    if not papers_file.exists():
        print(f"⚠️  Research papers file not found: {papers_file}")
        return
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    print(f"\n📥 Loading research papers from {papers_file.name}...")
    
    with open(papers_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        papers = data.get('papers', [])
        papers_loaded = 0
        
        for paper in papers:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO research_papers 
                    (pmid, title, authors, author_string, abstract, journal, 
                     publication_date, year, keywords, cancer_types, study_type, url)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    paper.get('pmid', ''),
                    paper.get('title', ''),
                    json.dumps(paper.get('authors', [])),
                    paper.get('author_string', ''),
                    paper.get('abstract', ''),
                    paper.get('journal', ''),
                    paper.get('publication_date', ''),
                    paper.get('year', 0),
                    json.dumps(paper.get('keywords', [])),
                    json.dumps(paper.get('cancer_types', [])),
                    paper.get('study_type', ''),
                    paper.get('url', '')
                ))
                papers_loaded += 1
            except Exception as e:
                continue
    
    conn.commit()
    conn.close()
    
    print(f"✅ Loaded {papers_loaded} research papers")


def verify_database():
    """Verify database contents"""
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    print("\n" + "="*70)
    print("📊 DATABASE VERIFICATION")
    print("="*70)
    
    # Count drugs
    cursor.execute("SELECT COUNT(*) FROM drugs")
    drug_count = cursor.fetchone()[0]
    print(f"✅ Drugs: {drug_count:,}")
    
    # Count oncology drugs
    cursor.execute("SELECT COUNT(*) FROM drugs WHERE is_oncology = 1")
    oncology_count = cursor.fetchone()[0]
    print(f"✅ Oncology compounds: {oncology_count:,}")
    
    # Count research papers
    cursor.execute("SELECT COUNT(*) FROM research_papers")
    papers_count = cursor.fetchone()[0]
    print(f"✅ Research papers: {papers_count:,}")
    
    # Database size
    db_size = DB_FILE.stat().st_size / (1024 * 1024)  # MB
    print(f"💾 Database size: {db_size:.2f} MB")
    
    print("="*70)
    
    conn.close()
    
    return drug_count > 0 or papers_count > 0


if __name__ == "__main__":
    print("🚀 OncoPurpose Database Setup")
    print("="*70)
    
    # Create database structure
    create_database()
    
    # Load data
    load_drugs_from_json()
    load_research_papers()
    
    # Verify
    if verify_database():
        print("\n✅ Database setup complete and verified!")
        print(f"\n📍 Database location: {DB_FILE.absolute()}")
        print("\n🔧 Update your .env file with:")
        print(f'DATABASE_URL=sqlite:///{DB_FILE.absolute()}')
    else:
        print("\n⚠️  Database created but no data loaded")
        print("   Check that data files exist in the data/ directory")
