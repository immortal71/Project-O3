"""
Collect data from ClinicalTrials.gov API v2
For known repurposed drugs in oncology

Free API - no authentication needed
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, List

import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClinicalTrialsCollector:
    """Collects ClinicalTrials.gov data for repurposed drugs"""
    
    API_BASE = "https://clinicaltrials.gov/api/v2/studies"
    
    # Known repurposed drugs to search for
    REPURPOSED_DRUGS = [
        "metformin",
        "aspirin",
        "statins",
        "atorvastatin",
        "simvastatin",
        "ibuprofen",
        "celecoxib",
        "thalidomide",
        "sildenafil",
        "valproic acid",
        "doxycycline",
        "chloroquine",
        "mebendazole",
        "propranolol",
        "digoxin"
    ]
    
    def __init__(self, data_dir: str = "../data/clinicaltrials"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def search_drug_cancer_trials(self, drug_name: str, max_results: int = 20) -> List[Dict]:
        """Search for trials involving a drug and cancer"""
        
        params = {
            'query.cond': 'cancer',
            'query.intr': drug_name,
            'pageSize': max_results,
            'format': 'json'
        }
        
        try:
            logger.info(f"Searching trials for {drug_name} in cancer...")
            response = requests.get(self.API_BASE, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            studies = data.get('studies', [])
            
            logger.info(f"Found {len(studies)} trials for {drug_name}")
            return studies
            
        except Exception as e:
            logger.error(f"Failed to fetch trials for {drug_name}: {e}")
            return []
    
    def extract_trial_info(self, study: Dict) -> Dict:
        """Extract relevant trial information"""
        protocol = study.get('protocolSection', {})
        identification = protocol.get('identificationModule', {})
        status = protocol.get('statusModule', {})
        description = protocol.get('descriptionModule', {})
        conditions = protocol.get('conditionsModule', {})
        interventions = protocol.get('armsInterventionsModule', {})
        
        return {
            'nct_id': identification.get('nctId'),
            'title': identification.get('briefTitle'),
            'status': status.get('overallStatus'),
            'phase': status.get('phase', []),
            'conditions': conditions.get('conditions', []),
            'interventions': [
                i.get('name') for i in interventions.get('interventions', [])
            ],
            'summary': description.get('briefSummary'),
            'start_date': status.get('startDateStruct', {}).get('date'),
        }
    
    def collect_for_drug(self, drug_name: str) -> Dict:
        """Collect trial data for a specific drug"""
        
        trials = self.search_drug_cancer_trials(drug_name)
        
        processed_trials = []
        for trial in trials:
            info = self.extract_trial_info(trial)
            processed_trials.append(info)
        
        return {
            'drug': drug_name,
            'trial_count': len(processed_trials),
            'trials': processed_trials
        }
    
    def collect_all(self) -> Dict[str, Dict]:
        """Collect trial data for all known repurposed drugs"""
        
        all_data = {}
        
        for drug in self.REPURPOSED_DRUGS:
            logger.info(f"\n📊 Collecting data for {drug}...")
            
            drug_data = self.collect_for_drug(drug)
            all_data[drug] = drug_data
            
            # Save individual drug data
            drug_file = self.data_dir / f"{drug.replace(' ', '_')}_trials.json"
            with open(drug_file, 'w', encoding='utf-8') as f:
                json.dump(drug_data, f, indent=2)
            
            # Rate limiting - be nice to the API
            time.sleep(1)
        
        # Save combined data
        output_path = self.data_dir / "all_repurposed_drug_trials.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2)
        
        logger.info(f"\n✅ Saved all data to {output_path}")
        
        return all_data


if __name__ == "__main__":
    collector = ClinicalTrialsCollector()
    data = collector.collect_all()
    
    print(f"\n✅ Collection Summary:")
    for drug, info in data.items():
        print(f"   - {drug}: {info['trial_count']} trials")
    
    print(f"\n💡 Use trial counts for confidence scoring in demo!")
