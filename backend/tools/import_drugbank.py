"""
Import DrugBank Open Data into local database
Download from: https://go.drugbank.com/releases/latest
Free "Open Data" version (~500 FDA-approved drugs)
"""

import sqlite3
import xml.etree.ElementTree as ET
import os
from datetime import datetime
from pathlib import Path

# Database path
DB_PATH = "C:/Users/HUAWEI/Downloads/Project_O3/database/oncopurpose.db"


def create_drugs_table(conn):
    """Create drugs table"""
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS drugs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            drugbank_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            indication TEXT,
            mechanism TEXT,
            pharmacodynamics TEXT,
            drug_class TEXT,
            cas_number TEXT,
            fda_approved BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create index for faster searches
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_drug_name ON drugs(name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_drugbank_id ON drugs(drugbank_id)")
    
    conn.commit()
    print("✅ Drugs table created")


def parse_drugbank_xml(xml_file):
    """Parse DrugBank XML file and extract drug data"""
    print(f"📖 Parsing {xml_file}...")
    
    # Define namespace
    ns = {'db': 'http://www.drugbank.ca'}
    
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        drugs = []
        
        for drug in root.findall('db:drug', ns):
            try:
                # Extract basic info
                drugbank_id = drug.find('db:drugbank-id[@primary="true"]', ns)
                name = drug.find('db:name', ns)
                description = drug.find('db:description', ns)
                indication = drug.find('db:indication', ns)
                pharmacodynamics = drug.find('db:pharmacodynamics', ns)
                mechanism = drug.find('db:mechanism-of-action', ns)
                
                # Extract groups (to check if FDA approved)
                groups = drug.findall('.//db:group', ns)
                fda_approved = any(g.text == 'approved' for g in groups)
                
                # Extract classification
                classification = drug.find('.//db:classification', ns)
                drug_class = None
                if classification is not None:
                    class_elem = classification.find('db:class', ns)
                    if class_elem is not None:
                        drug_class = class_elem.text
                
                # Extract CAS number
                cas = drug.find('.//db:cas-number', ns)
                
                drug_data = {
                    'drugbank_id': drugbank_id.text if drugbank_id is not None else None,
                    'name': name.text if name is not None else None,
                    'description': description.text if description is not None else None,
                    'indication': indication.text if indication is not None else None,
                    'mechanism': mechanism.text if mechanism is not None else None,
                    'pharmacodynamics': pharmacodynamics.text if pharmacodynamics is not None else None,
                    'drug_class': drug_class,
                    'cas_number': cas.text if cas is not None else None,
                    'fda_approved': 1 if fda_approved else 0
                }
                
                if drug_data['drugbank_id'] and drug_data['name']:
                    drugs.append(drug_data)
                    
            except Exception as e:
                print(f"⚠️  Error parsing drug: {e}")
                continue
        
        print(f"✅ Parsed {len(drugs)} drugs")
        return drugs
        
    except Exception as e:
        print(f"❌ Error parsing XML: {e}")
        return []


def insert_drugs(conn, drugs):
    """Insert drugs into database"""
    cursor = conn.cursor()
    
    inserted = 0
    updated = 0
    
    for drug in drugs:
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO drugs 
                (drugbank_id, name, description, indication, mechanism, 
                 pharmacodynamics, drug_class, cas_number, fda_approved, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                drug['drugbank_id'],
                drug['name'],
                drug['description'],
                drug['indication'],
                drug['mechanism'],
                drug['pharmacodynamics'],
                drug['drug_class'],
                drug['cas_number'],
                drug['fda_approved'],
                datetime.utcnow()
            ))
            
            if cursor.rowcount > 0:
                inserted += 1
            else:
                updated += 1
                
        except Exception as e:
            print(f"⚠️  Error inserting {drug.get('name')}: {e}")
    
    conn.commit()
    print(f"✅ Inserted {inserted} drugs, updated {updated} drugs")


def import_sample_drugs(conn):
    """Import sample drugs manually (if no XML file available)"""
    print("📝 Importing sample drugs...")
    
    sample_drugs = [
        {
            'drugbank_id': 'DB00945',
            'name': 'Aspirin',
            'description': 'Aspirin is a salicylate drug used to treat pain, fever, inflammation, and reduce the risk of heart attack and stroke.',
            'indication': 'For use in the temporary relief of various forms of pain, inflammation, and fever. Used to reduce the risk of death and/or non-fatal myocardial infarction in patients with cardiovascular disease.',
            'mechanism': 'Aspirin irreversibly inhibits cyclooxygenase-1 (COX-1) and cyclooxygenase-2 (COX-2) enzymes, preventing the formation of prostaglandins and thromboxanes.',
            'pharmacodynamics': 'Aspirin has anti-inflammatory, analgesic, and antipyretic properties. It also inhibits platelet aggregation.',
            'drug_class': 'Salicylates',
            'cas_number': '50-78-2',
            'fda_approved': 1
        },
        {
            'drugbank_id': 'DB00331',
            'name': 'Metformin',
            'description': 'Metformin is a biguanide antihyperglycemic agent used for treating type 2 diabetes mellitus.',
            'indication': 'For the treatment of type 2 diabetes mellitus, particularly in overweight and obese patients.',
            'mechanism': 'Metformin decreases hepatic glucose production, decreases intestinal absorption of glucose, and improves insulin sensitivity by increasing peripheral glucose uptake and utilization.',
            'pharmacodynamics': 'Metformin is an antihyperglycemic agent which improves glucose tolerance in patients with type 2 diabetes.',
            'drug_class': 'Biguanides',
            'cas_number': '657-24-9',
            'fda_approved': 1
        },
        {
            'drugbank_id': 'DB00316',
            'name': 'Acetaminophen',
            'description': 'Acetaminophen is an analgesic and antipyretic agent used to temporarily relieve mild to moderate pain and fever.',
            'indication': 'For the treatment of mild to moderate pain and fever.',
            'mechanism': 'Acetaminophen inhibits prostaglandin synthesis primarily in the central nervous system.',
            'pharmacodynamics': 'Acetaminophen has analgesic and antipyretic properties but lacks significant anti-inflammatory activity.',
            'drug_class': 'Analgesics',
            'cas_number': '103-90-2',
            'fda_approved': 1
        },
        {
            'drugbank_id': 'DB01174',
            'name': 'Phenobarbital',
            'description': 'A barbiturate that is used as a sedative, hypnotic and anticonvulsant.',
            'indication': 'For the treatment of epilepsy and as a sedative.',
            'mechanism': 'Phenobarbital enhances the activity of GABA, the major inhibitory neurotransmitter in the brain.',
            'pharmacodynamics': 'Phenobarbital is a barbiturate with sedative, hypnotic, and anticonvulsant properties.',
            'drug_class': 'Barbiturates',
            'cas_number': '50-06-6',
            'fda_approved': 1
        },
        {
            'drugbank_id': 'DB00563',
            'name': 'Imatinib',
            'description': 'A tyrosine kinase inhibitor used to treat chronic myelogenous leukemia and gastrointestinal stromal tumors.',
            'indication': 'For treatment of chronic myeloid leukemia (CML) and gastrointestinal stromal tumors (GISTs).',
            'mechanism': 'Imatinib inhibits the BCR-ABL tyrosine kinase, blocking downstream signal transduction pathways.',
            'pharmacodynamics': 'Imatinib is a small molecule kinase inhibitor with activity against multiple tyrosine kinases.',
            'drug_class': 'Tyrosine Kinase Inhibitors',
            'cas_number': '152459-95-5',
            'fda_approved': 1
        }
    ]
    
    insert_drugs(conn, sample_drugs)


def main():
    """Main import function"""
    print("🚀 DrugBank Import Tool")
    print("=" * 50)
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    print(f"📂 Database: {DB_PATH}")
    
    # Create table
    create_drugs_table(conn)
    
    # Check for XML file
    xml_file = Path(__file__).parent / "drugbank_all_full_database.xml"
    
    if xml_file.exists():
        print(f"📄 Found DrugBank XML: {xml_file}")
        drugs = parse_drugbank_xml(xml_file)
        if drugs:
            insert_drugs(conn, drugs)
    else:
        print(f"⚠️  DrugBank XML not found at: {xml_file}")
        print("📥 Download from: https://go.drugbank.com/releases/latest")
        print("    (Use 'Open Data' version - free, no license needed)")
        print("")
        print("💡 Importing sample drugs for now...")
        import_sample_drugs(conn)
    
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


if __name__ == "__main__":
    main()
