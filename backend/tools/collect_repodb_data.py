"""
Collect data from repoDB - Gold Standard for Drug Repurposing Validation
Source: https://unmtid-shinyapps.net/shiny/repodb/

This script downloads the full repoDB dataset containing:
- Approved drug-indication pairs
- Failed drug-indication pairs
- Perfect for retrospective validation
"""

import csv
import json
import logging
from pathlib import Path
from typing import Dict, List

import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RepoDBCollector:
    """Collects and processes repoDB data"""
    
    # Official repoDB dataset from Zenodo (published with the paper)
    # Source: https://doi.org/10.1038/sdata.2017.29
    # Direct CSV download from the official repoDB app backend
    REPODB_FULL_URL = "http://unmtid-shinyapps.net/download/repoDB/full.csv"
    REPODB_APPROVED_URL = "http://unmtid-shinyapps.net/download/repoDB/approved.csv"  
    REPODB_FAILED_URL = "http://unmtid-shinyapps.net/download/repoDB/failed.csv"
    
    def __init__(self, data_dir: str = "../data/repodb"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def download_dataset(self, url: str, filename: str) -> Path:
        """Download a dataset from URL"""
        filepath = self.data_dir / filename
        
        if filepath.exists():
            logger.info(f"File {filename} already exists, skipping download")
            return filepath
            
        logger.info(f"Downloading {filename} from {url}")
        
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
                
            logger.info(f"Successfully downloaded {filename}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to download {filename}: {e}")
            raise
    
    def parse_repodb_csv(self, filepath: Path) -> List[Dict]:
        """Parse repoDB CSV file"""
        data = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        
        logger.info(f"Parsed {len(data)} records from {filepath.name}")
        return data
    
    def extract_oncology_data(self, data: List[Dict]) -> List[Dict]:
        """Extract only oncology-related repurposing examples"""
        oncology_keywords = [
            'cancer', 'carcinoma', 'tumor', 'tumour', 'leukemia', 'lymphoma',
            'melanoma', 'sarcoma', 'glioma', 'myeloma', 'blastoma',
            'neoplasm', 'oncology', 'malignant', 'metastatic'
        ]
        
        oncology_data = []
        
        for record in data:
            indication = record.get('ind_name', '').lower()
            if any(keyword in indication for keyword in oncology_keywords):
                oncology_data.append(record)
        
        logger.info(f"Found {len(oncology_data)} oncology-related records")
        return oncology_data
    
    def collect_all(self) -> Dict[str, List[Dict]]:
        """Collect all repoDB datasets"""
        
        # Download datasets
        full_path = self.download_dataset(self.REPODB_FULL_URL, "full_database.csv")
        approved_path = self.download_dataset(self.REPODB_APPROVED_URL, "approved_database.csv")
        failed_path = self.download_dataset(self.REPODB_FAILED_URL, "failed_database.csv")
        
        # Parse datasets - KEEP ALL DATA
        full_data = self.parse_repodb_csv(full_path)
        approved_data = self.parse_repodb_csv(approved_path)
        failed_data = self.parse_repodb_csv(failed_path)
        
        # Also extract oncology-specific subset for quick reference
        oncology_full = self.extract_oncology_data(full_data)
        oncology_approved = self.extract_oncology_data(approved_data)
        oncology_failed = self.extract_oncology_data(failed_data)
        
        # Save COMPLETE datasets
        complete_output = {
            'full': full_data,
            'approved': approved_data,
            'failed': failed_data,
            'metadata': {
                'total_records': len(full_data),
                'approved_records': len(approved_data),
                'failed_records': len(failed_data),
                'oncology_full': len(oncology_full),
                'oncology_approved': len(oncology_approved),
                'oncology_failed': len(oncology_failed)
            }
        }
        
        # Save complete dataset
        complete_path = self.data_dir / "repodb_complete.json"
        with open(complete_path, 'w', encoding='utf-8') as f:
            json.dump(complete_output, f, indent=2)
        
        # Save oncology subset separately
        oncology_output = {
            'full': oncology_full,
            'approved': oncology_approved,
            'failed': oncology_failed
        }
        
        oncology_path = self.data_dir / "oncology_repurposing.json"
        with open(oncology_path, 'w', encoding='utf-8') as f:
            json.dump(oncology_output, f, indent=2)
        
        logger.info(f"Saved complete dataset to {complete_path}")
        logger.info(f"Saved oncology subset to {oncology_path}")
        
        return complete_output


if __name__ == "__main__":
    collector = RepoDBCollector()
    data = collector.collect_all()
    
    meta = data['metadata']
    print(f"\n✅ Collection Summary:")
    print(f"   - TOTAL records: {meta['total_records']}")
    print(f"   - Approved pairs: {meta['approved_records']}")
    print(f"   - Failed pairs: {meta['failed_records']}")
    print(f"   - Oncology subset: {meta['oncology_approved']} approved, {meta['oncology_failed']} failed")
    print(f"\n💾 Saved to: data/repodb/repodb_complete.json")
    print(f"💡 Use approved cases for demo and validation benchmark!")
