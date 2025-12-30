"""
ReDO_Trials_DB Data Collector
Downloads oncology-specific repurposing trials from Anti-Cancer Fund's ReDO project.
Source: https://www.anticancerfund.org/en/redo-trials-db

This is a gold-standard dataset of non-cancer drugs being tested in cancer trials.
Perfect for validating repurposing predictions.
"""

import requests
import json
import csv
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReDOCollector:
    """Download and process ReDO_Trials_DB (oncology repurposing trials)"""
    
    def __init__(self, output_dir: str = "../data/redo"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # ReDO_Trials_DB URLs (try multiple sources)
        self.urls = [
            "http://www.anticancerfund.org/sites/default/files/ReDO_Trials_DB.txt",
            "https://www.anticancerfund.org/sites/default/files/ReDO_Trials_DB.txt",
        ]
    
    def download_redo_trials(self) -> Path:
        """Download ReDO_Trials_DB.txt (tab-delimited file)"""
        
        for url in self.urls:
            try:
                logger.info(f"Attempting download from: {url}")
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                # Check if we got actual data (not HTML error page)
                content = response.text
                if content.startswith("<!DOCTYPE") or content.startswith("<html"):
                    logger.warning(f"Got HTML instead of data from {url}")
                    continue
                
                output_file = self.output_dir / "ReDO_Trials_DB.txt"
                output_file.write_text(content, encoding='utf-8')
                
                logger.info(f"✅ Downloaded ReDO_Trials_DB.txt ({len(content)} bytes)")
                logger.info(f"   Saved to: {output_file}")
                return output_file
                
            except Exception as e:
                logger.warning(f"Failed to download from {url}: {e}")
                continue
        
        raise Exception("Could not download ReDO_Trials_DB from any source")
    
    def parse_redo_trials(self, filepath: Path) -> list[dict]:
        """Parse ReDO_Trials_DB.txt (tab-delimited format)"""
        
        trials = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            # Tab-delimited file
            reader = csv.DictReader(f, delimiter='\t')
            
            for row in reader:
                trials.append(dict(row))
        
        logger.info(f"📊 Parsed {len(trials)} trials from ReDO_Trials_DB")
        return trials
    
    def process_all(self) -> dict:
        """Download and process all ReDO trial data"""
        
        logger.info("=" * 60)
        logger.info("ReDO_Trials_DB Collector - Oncology Repurposing Trials")
        logger.info("=" * 60)
        
        # Download
        filepath = self.download_redo_trials()
        
        # Parse all trials
        trials = self.parse_redo_trials(filepath)
        
        # Save as JSON for easy access
        json_output = self.output_dir / "redo_trials.json"
        with open(json_output, 'w', encoding='utf-8') as f:
            json.dump(trials, f, indent=2)
        
        logger.info(f"💾 Saved {len(trials)} trials to: {json_output}")
        
        # Extract unique drugs
        drugs = set()
        cancers = set()
        for trial in trials:
            # Fields vary, but typically include Drug, Cancer Type, etc.
            for key, value in trial.items():
                if 'drug' in key.lower() and value:
                    drugs.add(value.strip())
                if any(term in key.lower() for term in ['cancer', 'tumor', 'indication']) and value:
                    cancers.add(value.strip())
        
        logger.info(f"\n📈 Dataset Summary:")
        logger.info(f"   Total trials: {len(trials)}")
        logger.info(f"   Unique drugs: {len(drugs)}")
        logger.info(f"   Cancer types: {len(cancers)}")
        
        return {
            'trials': trials,
            'unique_drugs': sorted(drugs),
            'cancer_types': sorted(cancers),
            'total_trials': len(trials)
        }


if __name__ == "__main__":
    collector = ReDOCollector()
    results = collector.process_all()
    
    print("\n✅ ReDO_Trials_DB collection complete!")
    print(f"   {results['total_trials']} trials downloaded")
    print(f"   {len(results['unique_drugs'])} unique repurposed drugs")
    print(f"   {len(results['cancer_types'])} cancer types covered")
