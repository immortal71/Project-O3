"""
Collect data from Broad Institute Drug Repurposing Hub
Source: https://repo-hub.broadinstitute.org/repurposing

Free dataset with thousands of compounds, mechanisms, and clinical phases
"""

import csv
import json
import logging
from pathlib import Path
from typing import Dict, List

import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BroadRepurposingCollector:
    """Collects Broad Institute Drug Repurposing Hub data"""
    
    # Public download URLs
    BROAD_DRUGS_URL = "https://s3.amazonaws.com/data.clue.io/repurposing/downloads/repurposing_drugs_20200324.txt"
    BROAD_SAMPLES_URL = "https://s3.amazonaws.com/data.clue.io/repurposing/downloads/repurposing_samples_20200324.txt"
    
    def __init__(self, data_dir: str = "../data/broad"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def download_dataset(self, url: str, filename: str) -> Path:
        """Download dataset from URL"""
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
    
    def parse_tsv(self, filepath: Path) -> List[Dict]:
        """Parse tab-separated file (skip comment lines starting with !)"""
        data = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            # Skip comment lines starting with !
            lines = [line for line in f if not line.startswith('!')]
        
        # Parse the remaining lines
        import io
        text_io = io.StringIO(''.join(lines))
        reader = csv.DictReader(text_io, delimiter='\t')
        
        for row in reader:
            data.append(row)
        
        logger.info(f"Parsed {len(data)} records from {filepath.name}")
        return data
    
    def extract_oncology_compounds(self, drugs_data: List[Dict]) -> List[Dict]:
        """Extract compounds with oncology potential"""
        oncology_compounds = []
        
        oncology_keywords = [
            'cancer', 'tumor', 'oncology', 'carcinoma', 'leukemia',
            'lymphoma', 'melanoma', 'chemotherapy', 'antineoplastic'
        ]
        
        for drug in drugs_data:
            # Check indication, clinical phase, or target
            indication = drug.get('indication', '').lower()
            disease_area = drug.get('disease_area', '').lower()
            target = drug.get('target', '').lower()
            moa = drug.get('moa', '').lower()
            
            search_text = f"{indication} {disease_area} {target} {moa}"
            
            if any(keyword in search_text for keyword in oncology_keywords):
                oncology_compounds.append(drug)
        
        logger.info(f"Found {len(oncology_compounds)} oncology-related compounds")
        return oncology_compounds
    
    def collect_all(self) -> Dict[str, List[Dict]]:
        """Collect all Broad datasets"""
        
        # Download datasets
        drugs_path = self.download_dataset(self.BROAD_DRUGS_URL, "repurposing_drugs.txt")
        samples_path = self.download_dataset(self.BROAD_SAMPLES_URL, "repurposing_samples.txt")
        
        # Parse datasets - KEEP ALL DATA
        drugs_data = self.parse_tsv(drugs_path)
        samples_data = self.parse_tsv(samples_path)
        
        # Extract oncology compounds subset
        oncology_drugs = self.extract_oncology_compounds(drugs_data)
        
        # Save COMPLETE dataset
        complete_output = {
            'all_drugs': drugs_data,  # ALL drugs
            'all_samples': samples_data,  # ALL samples
            'metadata': {
                'total_drugs': len(drugs_data),
                'total_samples': len(samples_data),
                'oncology_drugs': len(oncology_drugs)
            }
        }
        
        complete_path = self.data_dir / "broad_complete.json"
        with open(complete_path, 'w', encoding='utf-8') as f:
            json.dump(complete_output, f, indent=2)
        
        # Save oncology subset separately
        oncology_output = {
            'oncology_drugs': oncology_drugs
        }
        
        oncology_path = self.data_dir / "broad_oncology_compounds.json"
        with open(oncology_path, 'w', encoding='utf-8') as f:
            json.dump(oncology_output, f, indent=2)
        
        logger.info(f"Saved complete dataset to {complete_path}")
        logger.info(f"Saved oncology subset to {oncology_path}")
        
        return complete_output


if __name__ == "__main__":
    collector = BroadRepurposingCollector()
    data = collector.collect_all()
    
    meta = data['metadata']
    print(f"\n✅ Collection Summary:")
    print(f"   - TOTAL drugs: {meta['total_drugs']}")
    print(f"   - TOTAL samples: {meta['total_samples']}")
    print(f"   - Oncology subset: {meta['oncology_drugs']} compounds")
    print(f"\n💾 Saved to: data/broad/broad_complete.json")
    print(f"💡 Use these for mechanism/pathway data in demo!")
