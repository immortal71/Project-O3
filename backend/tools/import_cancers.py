"""
Import Cancer Types into local database
Source: NCI Cancer Types list
"""

import sqlite3
from datetime import datetime
from pathlib import Path

# Database path
DB_PATH = "C:/Users/HUAWEI/Downloads/Project_O3/database/oncopurpose.db"


def create_cancers_table(conn):
    """Create cancers table"""
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cancers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            icd_code TEXT,
            category TEXT,
            prevalence_estimate TEXT,
            mortality_rate TEXT,
            common_genes TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create index for faster searches
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cancer_name ON cancers(name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cancer_category ON cancers(category)")
    
    conn.commit()
    print("✅ Cancers table created")


def insert_cancers(conn, cancers):
    """Insert cancer types into database"""
    cursor = conn.cursor()
    
    inserted = 0
    
    for cancer in cancers:
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO cancers 
                (name, icd_code, category, prevalence_estimate, mortality_rate, 
                 common_genes, description, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cancer['name'],
                cancer.get('icd_code'),
                cancer.get('category'),
                cancer.get('prevalence_estimate'),
                cancer.get('mortality_rate'),
                cancer.get('common_genes'),
                cancer.get('description'),
                datetime.utcnow()
            ))
            
            inserted += 1
                
        except Exception as e:
            print(f"⚠️  Error inserting {cancer.get('name')}: {e}")
    
    conn.commit()
    print(f"✅ Inserted {inserted} cancer types")


def get_cancer_data():
    """Get comprehensive list of major cancer types"""
    cancers = [
        # Lung Cancers
        {
            'name': 'Non-Small Cell Lung Cancer',
            'icd_code': 'C34',
            'category': 'Lung Cancer',
            'prevalence_estimate': '~2.2 million cases/year globally',
            'mortality_rate': 'High (5-year survival ~25%)',
            'common_genes': 'EGFR, KRAS, ALK, ROS1, BRAF',
            'description': 'The most common type of lung cancer, accounting for about 85% of cases.'
        },
        {
            'name': 'Small Cell Lung Cancer',
            'icd_code': 'C34',
            'category': 'Lung Cancer',
            'prevalence_estimate': '~250,000 cases/year globally',
            'mortality_rate': 'Very High (5-year survival ~7%)',
            'common_genes': 'TP53, RB1, MYC',
            'description': 'Aggressive lung cancer that grows and spreads quickly.'
        },
        
        # Breast Cancers
        {
            'name': 'Breast Cancer',
            'icd_code': 'C50',
            'category': 'Breast Cancer',
            'prevalence_estimate': '~2.3 million cases/year globally',
            'mortality_rate': 'Moderate (5-year survival ~90%)',
            'common_genes': 'BRCA1, BRCA2, HER2, PIK3CA',
            'description': 'The most common cancer in women worldwide.'
        },
        {
            'name': 'Triple-Negative Breast Cancer',
            'icd_code': 'C50',
            'category': 'Breast Cancer',
            'prevalence_estimate': '~300,000 cases/year globally',
            'mortality_rate': 'High (5-year survival ~77%)',
            'common_genes': 'BRCA1, TP53',
            'description': 'Aggressive breast cancer subtype lacking ER, PR, and HER2 receptors.'
        },
        
        # Colorectal Cancers
        {
            'name': 'Colorectal Cancer',
            'icd_code': 'C18-C20',
            'category': 'Gastrointestinal Cancer',
            'prevalence_estimate': '~1.9 million cases/year globally',
            'mortality_rate': 'Moderate (5-year survival ~65%)',
            'common_genes': 'APC, KRAS, TP53, BRAF',
            'description': 'Cancer affecting the colon or rectum.'
        },
        
        # Prostate Cancer
        {
            'name': 'Prostate Cancer',
            'icd_code': 'C61',
            'category': 'Urological Cancer',
            'prevalence_estimate': '~1.4 million cases/year globally',
            'mortality_rate': 'Low to Moderate (5-year survival ~98%)',
            'common_genes': 'BRCA2, AR, PTEN',
            'description': 'The most common cancer in men.'
        },
        
        # Stomach Cancer
        {
            'name': 'Gastric Cancer',
            'icd_code': 'C16',
            'category': 'Gastrointestinal Cancer',
            'prevalence_estimate': '~1.1 million cases/year globally',
            'mortality_rate': 'High (5-year survival ~32%)',
            'common_genes': 'HER2, TP53, CDH1',
            'description': 'Cancer of the stomach lining.'
        },
        
        # Liver Cancer
        {
            'name': 'Hepatocellular Carcinoma',
            'icd_code': 'C22',
            'category': 'Hepatobiliary Cancer',
            'prevalence_estimate': '~900,000 cases/year globally',
            'mortality_rate': 'Very High (5-year survival ~20%)',
            'common_genes': 'TP53, CTNNB1, AXIN1',
            'description': 'Primary liver cancer, often related to cirrhosis.'
        },
        
        # Blood Cancers
        {
            'name': 'Acute Myeloid Leukemia',
            'icd_code': 'C92.0',
            'category': 'Blood Cancer',
            'prevalence_estimate': '~20,000 cases/year in US',
            'mortality_rate': 'High (5-year survival ~29%)',
            'common_genes': 'FLT3, NPM1, IDH1, IDH2',
            'description': 'Aggressive cancer of myeloid blood cells.'
        },
        {
            'name': 'Chronic Myeloid Leukemia',
            'icd_code': 'C92.1',
            'category': 'Blood Cancer',
            'prevalence_estimate': '~9,000 cases/year in US',
            'mortality_rate': 'Low with treatment (5-year survival ~70%)',
            'common_genes': 'BCR-ABL1',
            'description': 'Chronic cancer characterized by BCR-ABL fusion gene.'
        },
        {
            'name': 'Multiple Myeloma',
            'icd_code': 'C90',
            'category': 'Blood Cancer',
            'prevalence_estimate': '~160,000 cases/year globally',
            'mortality_rate': 'Moderate (5-year survival ~55%)',
            'common_genes': 'KRAS, NRAS, TP53',
            'description': 'Cancer of plasma cells in bone marrow.'
        },
        {
            'name': 'Non-Hodgkin Lymphoma',
            'icd_code': 'C82-C85',
            'category': 'Blood Cancer',
            'prevalence_estimate': '~540,000 cases/year globally',
            'mortality_rate': 'Moderate (5-year survival ~73%)',
            'common_genes': 'BCL2, MYC, TP53',
            'description': 'Group of blood cancers affecting lymphatic system.'
        },
        
        # Brain Cancers
        {
            'name': 'Glioblastoma',
            'icd_code': 'C71',
            'category': 'Brain Cancer',
            'prevalence_estimate': '~15,000 cases/year in US',
            'mortality_rate': 'Very High (5-year survival ~7%)',
            'common_genes': 'EGFR, TP53, IDH1',
            'description': 'Aggressive primary brain tumor.'
        },
        
        # Pancreatic Cancer
        {
            'name': 'Pancreatic Adenocarcinoma',
            'icd_code': 'C25',
            'category': 'Gastrointestinal Cancer',
            'prevalence_estimate': '~500,000 cases/year globally',
            'mortality_rate': 'Very High (5-year survival ~11%)',
            'common_genes': 'KRAS, TP53, CDKN2A, SMAD4',
            'description': 'Aggressive cancer of the pancreas.'
        },
        
        # Ovarian Cancer
        {
            'name': 'Ovarian Cancer',
            'icd_code': 'C56',
            'category': 'Gynecological Cancer',
            'prevalence_estimate': '~310,000 cases/year globally',
            'mortality_rate': 'High (5-year survival ~49%)',
            'common_genes': 'BRCA1, BRCA2, TP53',
            'description': 'Cancer affecting the ovaries.'
        },
        
        # Bladder Cancer
        {
            'name': 'Bladder Cancer',
            'icd_code': 'C67',
            'category': 'Urological Cancer',
            'prevalence_estimate': '~570,000 cases/year globally',
            'mortality_rate': 'Moderate (5-year survival ~77%)',
            'common_genes': 'FGFR3, TP53, RB1',
            'description': 'Cancer of the bladder lining.'
        },
        
        # Kidney Cancer
        {
            'name': 'Renal Cell Carcinoma',
            'icd_code': 'C64',
            'category': 'Urological Cancer',
            'prevalence_estimate': '~430,000 cases/year globally',
            'mortality_rate': 'Moderate (5-year survival ~76%)',
            'common_genes': 'VHL, PBRM1, BAP1',
            'description': 'Most common type of kidney cancer.'
        },
        
        # Melanoma
        {
            'name': 'Melanoma',
            'icd_code': 'C43',
            'category': 'Skin Cancer',
            'prevalence_estimate': '~330,000 cases/year globally',
            'mortality_rate': 'Moderate to High (5-year survival ~93% localized)',
            'common_genes': 'BRAF, NRAS, NF1',
            'description': 'Aggressive skin cancer arising from melanocytes.'
        },
        
        # Thyroid Cancer
        {
            'name': 'Thyroid Cancer',
            'icd_code': 'C73',
            'category': 'Endocrine Cancer',
            'prevalence_estimate': '~570,000 cases/year globally',
            'mortality_rate': 'Low (5-year survival ~98%)',
            'common_genes': 'BRAF, RET, NTRK',
            'description': 'Cancer of the thyroid gland.'
        },
        
        # Esophageal Cancer
        {
            'name': 'Esophageal Cancer',
            'icd_code': 'C15',
            'category': 'Gastrointestinal Cancer',
            'prevalence_estimate': '~600,000 cases/year globally',
            'mortality_rate': 'Very High (5-year survival ~20%)',
            'common_genes': 'TP53, CDKN2A, HER2',
            'description': 'Cancer of the esophagus.'
        },
        
        # Cervical Cancer
        {
            'name': 'Cervical Cancer',
            'icd_code': 'C53',
            'category': 'Gynecological Cancer',
            'prevalence_estimate': '~600,000 cases/year globally',
            'mortality_rate': 'Moderate (5-year survival ~66%)',
            'common_genes': 'HPV16, HPV18',
            'description': 'Cancer of the cervix, often HPV-related.'
        },
        
        # Head and Neck Cancers
        {
            'name': 'Head and Neck Squamous Cell Carcinoma',
            'icd_code': 'C00-C14',
            'category': 'Head and Neck Cancer',
            'prevalence_estimate': '~900,000 cases/year globally',
            'mortality_rate': 'Moderate (5-year survival ~67%)',
            'common_genes': 'TP53, CDKN2A, PIK3CA',
            'description': 'Cancer of the mouth, throat, nose, or salivary glands.'
        },
        
        # Sarcomas
        {
            'name': 'Soft Tissue Sarcoma',
            'icd_code': 'C49',
            'category': 'Sarcoma',
            'prevalence_estimate': '~15,000 cases/year in US',
            'mortality_rate': 'Moderate (5-year survival ~65%)',
            'common_genes': 'TP53, RB1, PTEN',
            'description': 'Rare cancer affecting soft tissues.'
        },
        {
            'name': 'Osteosarcoma',
            'icd_code': 'C40-C41',
            'category': 'Sarcoma',
            'prevalence_estimate': '~3,500 cases/year in US',
            'mortality_rate': 'Moderate (5-year survival ~70%)',
            'common_genes': 'TP53, RB1',
            'description': 'Bone cancer, most common in children and young adults.'
        },
    ]
    
    return cancers


def main():
    """Main import function"""
    print("🚀 Cancer Types Import Tool")
    print("=" * 50)
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    print(f"📂 Database: {DB_PATH}")
    
    # Create table
    create_cancers_table(conn)
    
    # Get cancer data
    cancers = get_cancer_data()
    print(f"📝 Importing {len(cancers)} cancer types...")
    
    # Insert cancers
    insert_cancers(conn, cancers)
    
    # Show stats
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM cancers")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT category, COUNT(*) FROM cancers GROUP BY category")
    categories = cursor.fetchall()
    
    print("")
    print("📊 Database Statistics:")
    print(f"   Total cancer types: {total}")
    print("")
    print("   By category:")
    for cat, count in categories:
        print(f"      {cat}: {count}")
    
    conn.close()
    print("")
    print("✨ Import complete!")


if __name__ == "__main__":
    main()
