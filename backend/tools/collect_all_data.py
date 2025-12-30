"""
Master data collection orchestrator
Runs all data collection scripts and consolidates data for demo backend
"""

import json
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def main():
    """Run all data collection scripts"""
    
    logger.info("="*60)
    logger.info("🚀 ONCOPURPOSE DATA COLLECTION - DEMO BACKEND")
    logger.info("="*60)
    
    print("\n📦 This script will collect data from:")
    print("   1. repoDB - Gold standard drug repurposing validation dataset")
    print("   2. Broad Institute Drug Repurposing Hub - 6000+ compounds")
    print("   3. ClinicalTrials.gov - Trial data for known repurposed drugs")
    
    print("\n⏱️  Estimated time: 5-10 minutes")
    print("\n⚠️  NOTE: Requires internet connection")
    
    response = input("\nProceed with data collection? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        return
    
    # Create data directories
    data_dir = Path("../data")
    data_dir.mkdir(exist_ok=True)
    
    success_count = 0
    
    # 1. Collect repoDB data
    print("\n" + "="*60)
    print("STEP 1: Collecting repoDB data...")
    print("="*60)
    try:
        from collect_repodb_data import RepoDBCollector
        collector = RepoDBCollector()
        repodb_data = collector.collect_all()
        logger.info(f"✅ repoDB: {len(repodb_data['approved'])} approved oncology repurposing cases")
        success_count += 1
    except Exception as e:
        logger.error(f"❌ Failed to collect repoDB data: {e}")
    
    # 2. Collect Broad Institute data
    print("\n" + "="*60)
    print("STEP 2: Collecting Broad Institute Drug Repurposing Hub data...")
    print("="*60)
    try:
        from collect_broad_data import BroadRepurposingCollector
        collector = BroadRepurposingCollector()
        broad_data = collector.collect_all()
        logger.info(f"✅ Broad Hub: {len(broad_data['oncology_drugs'])} oncology compounds")
        success_count += 1
    except Exception as e:
        logger.error(f"❌ Failed to collect Broad data: {e}")
    
    # 3. Collect ClinicalTrials.gov data
    print("\n" + "="*60)
    print("STEP 3: Collecting ClinicalTrials.gov data...")
    print("="*60)
    try:
        from collect_clinicaltrials_data import ClinicalTrialsCollector
        collector = ClinicalTrialsCollector()
        trials_data = collector.collect_all()
        total_trials = sum(d['trial_count'] for d in trials_data.values())
        logger.info(f"✅ ClinicalTrials.gov: {total_trials} trials collected")
        success_count += 1
    except Exception as e:
        logger.error(f"❌ Failed to collect ClinicalTrials data: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("📊 COLLECTION SUMMARY")
    print("="*60)
    print(f"✅ Successfully collected: {success_count}/3 data sources")
    
    if success_count == 3:
        print("\n🎉 All data collected successfully!")
        print("\n📍 Next steps:")
        print("   1. Run: python build_demo_dataset.py")
        print("   2. Run: python validate_with_repodb.py")
        print("   3. Start backend: cd .. && python main.py")
    else:
        print("\n⚠️  Some data sources failed. Check errors above.")
        print("   You can still proceed with available data.")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Collection cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Collection failed: {e}")
        sys.exit(1)
