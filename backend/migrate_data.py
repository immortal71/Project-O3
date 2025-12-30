"""
Data migration script - Load JSON data into MySQL database
Migrates data from JSON files to database
"""

import json
import sys
import os
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import func
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import Drug, HeroCase, Mechanism, Target, DrugMechanism, DrugTarget
from db_connection import SessionLocal, init_database, test_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_json_file(filepath):
    """Load JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading {filepath}: {e}")
        return None


def migrate_drugs(db: Session):
    """Migrate drugs from JSON to database"""
    logger.info("📥 Migrating drugs...")
    
    # Load Broad Hub data
    broad_file = Path(__file__).parent.parent / 'data' / 'broad' / 'broad_complete.json'
    data = load_json_file(broad_file)
    
    if not data:
        logger.error("No drug data found")
        return 0
    
    drugs = data.get('drugs', [])
    count = 0
    
    # Get or create mechanisms and targets dictionaries
    mechanism_map = {}
    target_map = {}
    
    for drug_data in drugs:
        try:
            # Create drug
            drug = Drug(
                drug_name=drug_data.get('name', ''),
                clinical_phase=drug_data.get('clinical_phase', ''),
                mechanism_of_action=drug_data.get('moa', ''),
                target=drug_data.get('target', ''),
                disease_area=drug_data.get('disease_area', ''),
                indication=drug_data.get('indication', ''),
                source='broad_hub'
            )
            db.add(drug)
            db.flush()  # Get drug.id
            
            # Handle mechanisms
            moa = drug_data.get('moa', '')
            if moa and moa != 'Unknown':
                if moa not in mechanism_map:
                    mechanism = db.query(Mechanism).filter_by(mechanism_name=moa).first()
                    if not mechanism:
                        mechanism = Mechanism(mechanism_name=moa, drug_count=0)
                        db.add(mechanism)
                        db.flush()
                    mechanism_map[moa] = mechanism
                
                # Link drug to mechanism
                drug_mech = DrugMechanism(drug_id=drug.id, mechanism_id=mechanism_map[moa].id)
                db.add(drug_mech)
            
            # Handle targets
            target_val = drug_data.get('target', '')
            if target_val and target_val != 'Unknown':
                # Split multiple targets
                targets = [t.strip() for t in target_val.split(',')]
                for target_name in targets[:3]:  # Limit to first 3 targets
                    if target_name not in target_map:
                        target = db.query(Target).filter_by(target_name=target_name).first()
                        if not target:
                            target = Target(target_name=target_name, drug_count=0)
                            db.add(target)
                            db.flush()
                        target_map[target_name] = target
                    
                    # Link drug to target
                    drug_tgt = DrugTarget(drug_id=drug.id, target_id=target_map[target_name].id)
                    db.add(drug_tgt)
            
            count += 1
            
            if count % 500 == 0:
                db.commit()
                logger.info(f"  Migrated {count} drugs...")
                
        except Exception as e:
            logger.error(f"Error migrating drug {drug_data.get('name')}: {e}")
            continue
    
    db.commit()
    
    # Update mechanism and target counts
    logger.info("📊 Updating counts...")
    for mech in db.query(Mechanism).all():
        mech.drug_count = db.query(DrugMechanism).filter_by(mechanism_id=mech.id).count()
    
    for tgt in db.query(Target).all():
        tgt.drug_count = db.query(DrugTarget).filter_by(target_id=tgt.id).count()
    
    db.commit()
    
    logger.info(f"✅ Migrated {count} drugs")
    return count


def migrate_hero_cases(db: Session):
    """Migrate hero cases from JSON to database"""
    logger.info("📥 Migrating hero cases...")
    
    hero_file = Path(__file__).parent.parent / 'data' / 'hero_cases' / 'hero_repurposing_cases.json'
    data = load_json_file(hero_file)
    
    if not data:
        logger.error("No hero case data found")
        return 0
    
    cases = data.get('hero_cases', [])
    count = 0
    
    for case_data in cases:
        try:
            hero_case = HeroCase(
                drug_name=case_data.get('drug_name', ''),
                original_indication=case_data.get('original_indication', ''),
                repurposed_cancer=case_data.get('repurposed_cancer', ''),
                confidence_score=case_data.get('confidence_score', 0),
                trial_count=case_data.get('trial_count', 0),
                citations=case_data.get('citations', 0),
                mechanism=case_data.get('mechanism', ''),
                pathways=', '.join(case_data.get('pathways', [])),
                evidence_level=case_data.get('evidence_level', 'high')
            )
            db.add(hero_case)
            count += 1
        except Exception as e:
            logger.error(f"Error migrating hero case {case_data.get('drug_name')}: {e}")
            continue
    
    db.commit()
    logger.info(f"✅ Migrated {count} hero cases")
    return count


def main():
    """Main migration function"""
    logger.info("🚀 Starting database migration...")
    
    # Test connection
    if not test_connection():
        logger.error("❌ Database connection failed. Check your .env file and MySQL server.")
        return
    
    # Initialize database (create tables)
    if not init_database():
        logger.error("❌ Database initialization failed")
        return
    
    # Create session
    db = SessionLocal()
    
    try:
        # Check if data already exists
        drug_count = db.query(Drug).count()
        hero_count = db.query(HeroCase).count()
        
        if drug_count > 0 or hero_count > 0:
            logger.warning(f"⚠️  Database already contains data: {drug_count} drugs, {hero_count} hero cases")
            response = input("Clear existing data and re-migrate? (yes/no): ")
            if response.lower() != 'yes':
                logger.info("Migration cancelled")
                return
            
            # Clear existing data
            logger.info("🗑️  Clearing existing data...")
            db.query(DrugMechanism).delete()
            db.query(DrugTarget).delete()
            db.query(Drug).delete()
            db.query(HeroCase).delete()
            db.query(Mechanism).delete()
            db.query(Target).delete()
            db.commit()
        
        # Migrate data
        drug_count = migrate_drugs(db)
        hero_count = migrate_hero_cases(db)
        
        # Show summary
        mechanism_count = db.query(Mechanism).count()
        target_count = db.query(Target).count()
        
        logger.info("\n" + "="*60)
        logger.info("✅ MIGRATION COMPLETE")
        logger.info("="*60)
        logger.info(f"📊 Drugs: {drug_count}")
        logger.info(f"🌟 Hero Cases: {hero_count}")
        logger.info(f"🔬 Mechanisms: {mechanism_count}")
        logger.info(f"🎯 Targets: {target_count}")
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == '__main__':
    main()
