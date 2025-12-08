"""
Import drugs from free public databases:
- PubChem (NIH) - Free for commercial use
- ChEMBL (EBI) - Open license
- RxNorm/DailyMed (FDA) - Public domain
"""

import sqlite3
import requests
import json
import time
from pathlib import Path

DB_PATH = "C:/Users/HUAWEI/Downloads/Project_O3/database/oncopurpose.db"


def create_drugs_table(conn):
    """Create drugs table or add missing columns"""
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='drugs'")
    table_exists = cursor.fetchone() is not None
    
    if not table_exists:
        # Create new table
        cursor.execute("""
            CREATE TABLE drugs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                drugbank_id TEXT,
                pubchem_cid TEXT,
                chembl_id TEXT,
                name TEXT NOT NULL,
                description TEXT,
                indication TEXT,
                mechanism TEXT,
                pharmacodynamics TEXT,
                drug_class TEXT,
                cas_number TEXT,
                fda_approved BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(name)
            )
        """)
        print("✅ Created new drugs table")
    else:
        # Add missing columns if needed
        cursor.execute("PRAGMA table_info(drugs)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'pubchem_cid' not in columns:
            cursor.execute("ALTER TABLE drugs ADD COLUMN pubchem_cid TEXT")
            print("✅ Added pubchem_cid column")
        
        if 'chembl_id' not in columns:
            cursor.execute("ALTER TABLE drugs ADD COLUMN chembl_id TEXT")
            print("✅ Added chembl_id column")
        
        print("✅ Drugs table updated")
    
    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_drug_name ON drugs(name)")
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pubchem_cid ON drugs(pubchem_cid)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chembl_id ON drugs(chembl_id)")
    except:
        pass
    
    conn.commit()


def fetch_chembl_drugs(limit=500):
    """Fetch FDA-approved drugs from ChEMBL"""
    print(f"📥 Fetching up to {limit} drugs from ChEMBL...")
    
    drugs = []
    url = "https://www.ebi.ac.uk/chembl/api/data/molecule.json"
    
    params = {
        'max_phase': 4,  # FDA approved
        'limit': 100,
        'offset': 0
    }
    
    try:
        while len(drugs) < limit:
            print(f"   Fetching batch {params['offset']//100 + 1}...")
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            molecules = data.get('molecules', [])
            
            if not molecules:
                break
            
            for mol in molecules:
                try:
                    drug = {
                        'chembl_id': mol.get('molecule_chembl_id'),
                        'name': mol.get('pref_name', ''),
                        'description': mol.get('molecule_properties', {}).get('full_mwt'),
                        'indication': None,  # Will get from other sources
                        'mechanism': mol.get('mechanism_of_action'),
                        'drug_class': mol.get('molecule_type'),
                        'fda_approved': 1 if mol.get('max_phase') == 4 else 0
                    }
                    
                    if drug['name']:
                        drugs.append(drug)
                        
                except Exception as e:
                    continue
            
            params['offset'] += 100
            
            if len(drugs) >= limit:
                drugs = drugs[:limit]
                break
            
            time.sleep(0.5)  # Rate limiting
        
        print(f"✅ Fetched {len(drugs)} drugs from ChEMBL")
        return drugs
        
    except Exception as e:
        print(f"⚠️  Error fetching from ChEMBL: {e}")
        return []


def fetch_pubchem_info(drug_name):
    """Fetch additional info from PubChem"""
    try:
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{drug_name}/cids/JSON"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            cid = data.get('IdentifierList', {}).get('CID', [None])[0]
            return str(cid) if cid else None
            
    except:
        pass
    
    return None


def get_fda_approved_drugs():
    """Get comprehensive list of common FDA-approved drugs"""
    return [
        # Cancer drugs
        {'name': 'Imatinib', 'indication': 'CML, GIST', 'mechanism': 'BCR-ABL tyrosine kinase inhibitor', 'drug_class': 'Tyrosine Kinase Inhibitor', 'fda_approved': 1},
        {'name': 'Erlotinib', 'indication': 'NSCLC, pancreatic cancer', 'mechanism': 'EGFR tyrosine kinase inhibitor', 'drug_class': 'Tyrosine Kinase Inhibitor', 'fda_approved': 1},
        {'name': 'Gefitinib', 'indication': 'NSCLC', 'mechanism': 'EGFR tyrosine kinase inhibitor', 'drug_class': 'Tyrosine Kinase Inhibitor', 'fda_approved': 1},
        {'name': 'Sunitinib', 'indication': 'RCC, GIST', 'mechanism': 'Multi-kinase inhibitor', 'drug_class': 'Tyrosine Kinase Inhibitor', 'fda_approved': 1},
        {'name': 'Sorafenib', 'indication': 'RCC, HCC', 'mechanism': 'Multi-kinase inhibitor', 'drug_class': 'Tyrosine Kinase Inhibitor', 'fda_approved': 1},
        {'name': 'Bevacizumab', 'indication': 'Colorectal, lung, kidney cancer', 'mechanism': 'VEGF inhibitor', 'drug_class': 'Monoclonal Antibody', 'fda_approved': 1},
        {'name': 'Trastuzumab', 'indication': 'HER2+ breast cancer', 'mechanism': 'HER2 inhibitor', 'drug_class': 'Monoclonal Antibody', 'fda_approved': 1},
        {'name': 'Rituximab', 'indication': 'NHL, CLL', 'mechanism': 'CD20 inhibitor', 'drug_class': 'Monoclonal Antibody', 'fda_approved': 1},
        {'name': 'Pembrolizumab', 'indication': 'Various cancers', 'mechanism': 'PD-1 inhibitor', 'drug_class': 'Checkpoint Inhibitor', 'fda_approved': 1},
        {'name': 'Nivolumab', 'indication': 'Melanoma, NSCLC', 'mechanism': 'PD-1 inhibitor', 'drug_class': 'Checkpoint Inhibitor', 'fda_approved': 1},
        {'name': 'Tamoxifen', 'indication': 'Breast cancer', 'mechanism': 'Estrogen receptor modulator', 'drug_class': 'SERM', 'fda_approved': 1},
        {'name': 'Letrozole', 'indication': 'Breast cancer', 'mechanism': 'Aromatase inhibitor', 'drug_class': 'Aromatase Inhibitor', 'fda_approved': 1},
        {'name': 'Paclitaxel', 'indication': 'Breast, ovarian, lung cancer', 'mechanism': 'Microtubule stabilization', 'drug_class': 'Taxane', 'fda_approved': 1},
        {'name': 'Doxorubicin', 'indication': 'Various cancers', 'mechanism': 'DNA intercalation', 'drug_class': 'Anthracycline', 'fda_approved': 1},
        {'name': 'Cisplatin', 'indication': 'Various cancers', 'mechanism': 'DNA crosslinking', 'drug_class': 'Platinum Agent', 'fda_approved': 1},
        {'name': 'Carboplatin', 'indication': 'Ovarian, lung cancer', 'mechanism': 'DNA crosslinking', 'drug_class': 'Platinum Agent', 'fda_approved': 1},
        {'name': '5-Fluorouracil', 'indication': 'Colorectal, breast cancer', 'mechanism': 'Thymidylate synthase inhibitor', 'drug_class': 'Antimetabolite', 'fda_approved': 1},
        {'name': 'Capecitabine', 'indication': 'Colorectal, breast cancer', 'mechanism': 'Prodrug of 5-FU', 'drug_class': 'Antimetabolite', 'fda_approved': 1},
        {'name': 'Gemcitabine', 'indication': 'Pancreatic, lung cancer', 'mechanism': 'Nucleoside analog', 'drug_class': 'Antimetabolite', 'fda_approved': 1},
        {'name': 'Methotrexate', 'indication': 'Leukemia, lymphoma', 'mechanism': 'DHFR inhibitor', 'drug_class': 'Antimetabolite', 'fda_approved': 1},
        
        # Cardiovascular drugs
        {'name': 'Aspirin', 'indication': 'Pain relief, anti-inflammatory, antiplatelet', 'mechanism': 'COX inhibitor', 'drug_class': 'NSAID', 'fda_approved': 1},
        {'name': 'Lisinopril', 'indication': 'Hypertension, heart failure', 'mechanism': 'ACE inhibitor', 'drug_class': 'ACE Inhibitor', 'fda_approved': 1},
        {'name': 'Enalapril', 'indication': 'Hypertension, heart failure', 'mechanism': 'ACE inhibitor', 'drug_class': 'ACE Inhibitor', 'fda_approved': 1},
        {'name': 'Atorvastatin', 'indication': 'High cholesterol', 'mechanism': 'HMG-CoA reductase inhibitor', 'drug_class': 'Statin', 'fda_approved': 1},
        {'name': 'Simvastatin', 'indication': 'High cholesterol', 'mechanism': 'HMG-CoA reductase inhibitor', 'drug_class': 'Statin', 'fda_approved': 1},
        {'name': 'Rosuvastatin', 'indication': 'High cholesterol', 'mechanism': 'HMG-CoA reductase inhibitor', 'drug_class': 'Statin', 'fda_approved': 1},
        {'name': 'Amlodipine', 'indication': 'Hypertension, angina', 'mechanism': 'Calcium channel blocker', 'drug_class': 'Calcium Channel Blocker', 'fda_approved': 1},
        {'name': 'Metoprolol', 'indication': 'Hypertension, angina', 'mechanism': 'Beta-1 selective blocker', 'drug_class': 'Beta Blocker', 'fda_approved': 1},
        {'name': 'Carvedilol', 'indication': 'Heart failure, hypertension', 'mechanism': 'Non-selective beta blocker', 'drug_class': 'Beta Blocker', 'fda_approved': 1},
        {'name': 'Losartan', 'indication': 'Hypertension', 'mechanism': 'Angiotensin II receptor blocker', 'drug_class': 'ARB', 'fda_approved': 1},
        {'name': 'Valsartan', 'indication': 'Hypertension, heart failure', 'mechanism': 'Angiotensin II receptor blocker', 'drug_class': 'ARB', 'fda_approved': 1},
        {'name': 'Warfarin', 'indication': 'Anticoagulation', 'mechanism': 'Vitamin K antagonist', 'drug_class': 'Anticoagulant', 'fda_approved': 1},
        {'name': 'Clopidogrel', 'indication': 'Antiplatelet', 'mechanism': 'P2Y12 inhibitor', 'drug_class': 'Antiplatelet', 'fda_approved': 1},
        {'name': 'Hydrochlorothiazide', 'indication': 'Hypertension, edema', 'mechanism': 'Thiazide diuretic', 'drug_class': 'Diuretic', 'fda_approved': 1},
        {'name': 'Furosemide', 'indication': 'Edema, heart failure', 'mechanism': 'Loop diuretic', 'drug_class': 'Diuretic', 'fda_approved': 1},
        
        # Diabetes drugs
        {'name': 'Metformin', 'indication': 'Type 2 diabetes', 'mechanism': 'Reduces hepatic glucose production', 'drug_class': 'Biguanide', 'fda_approved': 1},
        {'name': 'Insulin Glargine', 'indication': 'Type 1 & 2 diabetes', 'mechanism': 'Long-acting insulin analog', 'drug_class': 'Insulin', 'fda_approved': 1},
        {'name': 'Sitagliptin', 'indication': 'Type 2 diabetes', 'mechanism': 'DPP-4 inhibitor', 'drug_class': 'DPP-4 Inhibitor', 'fda_approved': 1},
        {'name': 'Empagliflozin', 'indication': 'Type 2 diabetes', 'mechanism': 'SGLT2 inhibitor', 'drug_class': 'SGLT2 Inhibitor', 'fda_approved': 1},
        
        # Pain & Inflammation
        {'name': 'Ibuprofen', 'indication': 'Pain, fever, inflammation', 'mechanism': 'COX-1/COX-2 inhibitor', 'drug_class': 'NSAID', 'fda_approved': 1},
        {'name': 'Naproxen', 'indication': 'Pain, inflammation', 'mechanism': 'COX inhibitor', 'drug_class': 'NSAID', 'fda_approved': 1},
        {'name': 'Acetaminophen', 'indication': 'Pain, fever', 'mechanism': 'COX inhibitor (CNS)', 'drug_class': 'Analgesic', 'fda_approved': 1},
        {'name': 'Celecoxib', 'indication': 'Arthritis pain', 'mechanism': 'COX-2 selective inhibitor', 'drug_class': 'NSAID', 'fda_approved': 1},
        {'name': 'Morphine', 'indication': 'Severe pain', 'mechanism': 'Mu-opioid receptor agonist', 'drug_class': 'Opioid', 'fda_approved': 1},
        {'name': 'Tramadol', 'indication': 'Moderate pain', 'mechanism': 'Opioid receptor agonist, SNRI', 'drug_class': 'Opioid', 'fda_approved': 1},
        
        # Neurological drugs
        {'name': 'Gabapentin', 'indication': 'Neuropathic pain, seizures', 'mechanism': 'GABA analog', 'drug_class': 'Anticonvulsant', 'fda_approved': 1},
        {'name': 'Pregabalin', 'indication': 'Neuropathic pain, fibromyalgia', 'mechanism': 'GABA analog', 'drug_class': 'Anticonvulsant', 'fda_approved': 1},
        {'name': 'Levetiracetam', 'indication': 'Epilepsy', 'mechanism': 'SV2A modulator', 'drug_class': 'Anticonvulsant', 'fda_approved': 1},
        {'name': 'Phenytoin', 'indication': 'Epilepsy', 'mechanism': 'Sodium channel blocker', 'drug_class': 'Anticonvulsant', 'fda_approved': 1},
        {'name': 'Valproic Acid', 'indication': 'Epilepsy, bipolar', 'mechanism': 'Multiple mechanisms', 'drug_class': 'Anticonvulsant', 'fda_approved': 1},
        
        # Psychiatry
        {'name': 'Sertraline', 'indication': 'Depression, anxiety', 'mechanism': 'SSRI', 'drug_class': 'Antidepressant', 'fda_approved': 1},
        {'name': 'Fluoxetine', 'indication': 'Depression, OCD', 'mechanism': 'SSRI', 'drug_class': 'Antidepressant', 'fda_approved': 1},
        {'name': 'Escitalopram', 'indication': 'Depression, anxiety', 'mechanism': 'SSRI', 'drug_class': 'Antidepressant', 'fda_approved': 1},
        {'name': 'Venlafaxine', 'indication': 'Depression, anxiety', 'mechanism': 'SNRI', 'drug_class': 'Antidepressant', 'fda_approved': 1},
        {'name': 'Bupropion', 'indication': 'Depression, smoking cessation', 'mechanism': 'NDRI', 'drug_class': 'Antidepressant', 'fda_approved': 1},
        {'name': 'Aripiprazole', 'indication': 'Schizophrenia, bipolar', 'mechanism': 'Dopamine partial agonist', 'drug_class': 'Antipsychotic', 'fda_approved': 1},
        {'name': 'Quetiapine', 'indication': 'Schizophrenia, bipolar', 'mechanism': 'Multiple receptor antagonist', 'drug_class': 'Antipsychotic', 'fda_approved': 1},
        {'name': 'Alprazolam', 'indication': 'Anxiety, panic', 'mechanism': 'GABA-A agonist', 'drug_class': 'Benzodiazepine', 'fda_approved': 1},
        {'name': 'Lorazepam', 'indication': 'Anxiety', 'mechanism': 'GABA-A agonist', 'drug_class': 'Benzodiazepine', 'fda_approved': 1},
        
        # Respiratory
        {'name': 'Albuterol', 'indication': 'Asthma, COPD', 'mechanism': 'Beta-2 agonist', 'drug_class': 'Bronchodilator', 'fda_approved': 1},
        {'name': 'Montelukast', 'indication': 'Asthma, allergies', 'mechanism': 'Leukotriene receptor antagonist', 'drug_class': 'Leukotriene Inhibitor', 'fda_approved': 1},
        {'name': 'Fluticasone', 'indication': 'Asthma, allergic rhinitis', 'mechanism': 'Corticosteroid', 'drug_class': 'Corticosteroid', 'fda_approved': 1},
        
        # GI drugs
        {'name': 'Omeprazole', 'indication': 'GERD, ulcers', 'mechanism': 'Proton pump inhibitor', 'drug_class': 'PPI', 'fda_approved': 1},
        {'name': 'Lansoprazole', 'indication': 'GERD, ulcers', 'mechanism': 'Proton pump inhibitor', 'drug_class': 'PPI', 'fda_approved': 1},
        {'name': 'Pantoprazole', 'indication': 'GERD, ulcers', 'mechanism': 'Proton pump inhibitor', 'drug_class': 'PPI', 'fda_approved': 1},
        {'name': 'Ranitidine', 'indication': 'GERD, ulcers', 'mechanism': 'H2 receptor antagonist', 'drug_class': 'H2 Blocker', 'fda_approved': 1},
        
        # Endocrine
        {'name': 'Levothyroxine', 'indication': 'Hypothyroidism', 'mechanism': 'Thyroid hormone replacement', 'drug_class': 'Thyroid Hormone', 'fda_approved': 1},
        {'name': 'Prednisone', 'indication': 'Inflammation, autoimmune', 'mechanism': 'Glucocorticoid', 'drug_class': 'Corticosteroid', 'fda_approved': 1},
        
        # Antibiotics
        {'name': 'Amoxicillin', 'indication': 'Bacterial infections', 'mechanism': 'Cell wall synthesis inhibitor', 'drug_class': 'Penicillin', 'fda_approved': 1},
        {'name': 'Azithromycin', 'indication': 'Bacterial infections', 'mechanism': 'Protein synthesis inhibitor', 'drug_class': 'Macrolide', 'fda_approved': 1},
        {'name': 'Ciprofloxacin', 'indication': 'Bacterial infections', 'mechanism': 'DNA gyrase inhibitor', 'drug_class': 'Fluoroquinolone', 'fda_approved': 1},
        {'name': 'Doxycycline', 'indication': 'Bacterial infections', 'mechanism': 'Protein synthesis inhibitor', 'drug_class': 'Tetracycline', 'fda_approved': 1},
        
        # Antivirals
        {'name': 'Acyclovir', 'indication': 'Herpes infections', 'mechanism': 'DNA polymerase inhibitor', 'drug_class': 'Antiviral', 'fda_approved': 1},
        {'name': 'Oseltamivir', 'indication': 'Influenza', 'mechanism': 'Neuraminidase inhibitor', 'drug_class': 'Antiviral', 'fda_approved': 1},
    ]


def insert_drugs(conn, drugs):
    """Insert drugs into database"""
    cursor = conn.cursor()
    
    inserted = 0
    skipped = 0
    
    for drug in drugs:
        if not drug.get('name'):
            skipped += 1
            continue
            
        try:
            cursor.execute("""
                INSERT INTO drugs 
                (chembl_id, pubchem_cid, name, description, indication, mechanism, 
                 pharmacodynamics, drug_class, cas_number, fda_approved)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                drug.get('chembl_id'),
                drug.get('pubchem_cid'),
                drug['name'],
                drug.get('description'),
                drug.get('indication'),
                drug.get('mechanism'),
                drug.get('pharmacodynamics'),
                drug.get('drug_class'),
                drug.get('cas_number'),
                drug.get('fda_approved', 0)
            ))
            
            inserted += 1
                
        except sqlite3.IntegrityError:
            # Duplicate name
            skipped += 1
        except Exception as e:
            print(f"⚠️  Error inserting {drug.get('name')}: {e}")
            skipped += 1
    
    conn.commit()
    print(f"✅ Inserted {inserted} drugs, skipped {skipped} duplicates")


def main():
    """Main import function"""
    print("🚀 Free Public Database Import")
    print("=" * 50)
    print("Sources: ChEMBL, PubChem, FDA")
    print("")
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    print(f"📂 Database: {DB_PATH}")
    
    # Create table
    create_drugs_table(conn)
    
    # Use curated FDA drug list (ChEMBL API often returns incomplete data)
    print("")
    print("📋 Loading curated FDA-approved drugs...")
    drugs = get_fda_approved_drugs()
    print(f"✅ Loaded {len(drugs)} drugs from curated list")
    
    # Insert drugs
    if drugs:
        print("")
        print(f"💾 Importing {len(drugs)} drugs...")
        insert_drugs(conn, drugs)
    
    # Show stats
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM drugs")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM drugs WHERE fda_approved = 1")
    approved = cursor.fetchone()[0]
    
    print("")
    print("📊 Database Statistics:")
    print(f"   Total drugs: {total}")
    print(f"   FDA approved: {approved}")
    
    conn.close()
    print("")
    print("✨ Import complete!")
    print("")
    print("💡 To expand database:")
    print("   - ChEMBL: https://www.ebi.ac.uk/chembl")
    print("   - PubChem: https://pubchem.ncbi.nlm.nih.gov")
    print("   - DailyMed: https://dailymed.nlm.nih.gov")


if __name__ == "__main__":
    main()
