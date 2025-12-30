"""
Data Loader - Load all downloaded datasets into memory for API use

Loads:
1. Broad Institute Hub - 6,798 drugs with mechanisms/targets
2. Hero Cases - 15 high-confidence repurposing examples
3. Oncology subset - 242 cancer-relevant compounds

This module provides fast in-memory access to all data for the demo API.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class DataLoader:
    """Load and manage all repurposing datasets"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        
        # Loaded datasets
        self.broad_drugs: List[Dict] = []
        self.broad_samples: List[Dict] = []
        self.oncology_compounds: List[Dict] = []
        self.hero_cases: List[Dict] = []
        
        # Indexes for fast lookup
        self.drugs_by_name: Dict[str, Dict] = {}
        self.drugs_by_target: Dict[str, List[Dict]] = {}
        self.drugs_by_moa: Dict[str, List[Dict]] = {}
        
        self._load_all_data()
    
    def _load_all_data(self):
        """Load all datasets and build indexes"""
        
        # Load Broad Institute complete dataset
        broad_file = self.data_dir / "broad" / "broad_complete.json"
        if broad_file.exists():
            with open(broad_file, 'r', encoding='utf-8') as f:
                broad_data = json.load(f)
                self.broad_drugs = broad_data.get('all_drugs', [])
                self.broad_samples = broad_data.get('all_samples', [])
            logger.info(f"✅ Loaded {len(self.broad_drugs)} drugs from Broad Hub")
        else:
            logger.warning(f"⚠️ Broad data not found at {broad_file}")
        
        # Load oncology subset
        oncology_file = self.data_dir / "broad" / "broad_oncology_compounds.json"
        if oncology_file.exists():
            with open(oncology_file, 'r', encoding='utf-8') as f:
                oncology_data = json.load(f)
                self.oncology_compounds = oncology_data.get('oncology_drugs', [])
            logger.info(f"✅ Loaded {len(self.oncology_compounds)} oncology compounds")
        
        # Load hero cases
        hero_file = self.data_dir / "hero_cases" / "hero_repurposing_cases.json"
        if hero_file.exists():
            with open(hero_file, 'r', encoding='utf-8') as f:
                self.hero_cases = json.load(f)
            logger.info(f"✅ Loaded {len(self.hero_cases)} hero cases")
        else:
            logger.warning(f"⚠️ Hero cases not found at {hero_file}")
        
        # Build indexes
        self._build_indexes()
        
        logger.info(f"📊 Data loaded: {len(self.broad_drugs)} total drugs, {len(self.oncology_compounds)} oncology")
    
    def _build_indexes(self):
        """Build lookup indexes for fast search"""
        
        # Index by drug name
        for drug in self.broad_drugs:
            name = drug.get('pert_iname', '').lower()
            if name:
                self.drugs_by_name[name] = drug
        
        # Index by mechanism of action
        for drug in self.broad_drugs:
            moa = drug.get('moa', '')
            if moa:
                if moa not in self.drugs_by_moa:
                    self.drugs_by_moa[moa] = []
                self.drugs_by_moa[moa].append(drug)
        
        # Index by target
        for drug in self.broad_drugs:
            targets = drug.get('target', '')
            if targets:
                # Targets are pipe-separated
                for target in targets.split('|'):
                    target = target.strip()
                    if target:
                        if target not in self.drugs_by_target:
                            self.drugs_by_target[target] = []
                        self.drugs_by_target[target].append(drug)
        
        logger.info(f"📑 Indexes built: {len(self.drugs_by_name)} drugs, {len(self.drugs_by_moa)} MOAs, {len(self.drugs_by_target)} targets")
    
    def search_drugs(self, query: str, limit: int = 50) -> List[Dict]:
        """Search drugs by name, mechanism, or target"""
        
        query_lower = query.lower()
        results = []
        
        # Exact name match
        if query_lower in self.drugs_by_name:
            results.append(self.drugs_by_name[query_lower])
        
        # Partial name match
        for name, drug in self.drugs_by_name.items():
            if query_lower in name and drug not in results:
                results.append(drug)
        
        # Search in mechanisms
        for moa, drugs in self.drugs_by_moa.items():
            if query_lower in moa.lower():
                for drug in drugs:
                    if drug not in results:
                        results.append(drug)
        
        # Search in targets
        for target, drugs in self.drugs_by_target.items():
            if query_lower in target.lower():
                for drug in drugs:
                    if drug not in results:
                        results.append(drug)
        
        # Search in disease areas and indications
        for drug in self.broad_drugs:
            if drug in results:
                continue
            
            disease_area = drug.get('disease_area', '').lower()
            indication = drug.get('indication', '').lower()
            
            if query_lower in disease_area or query_lower in indication:
                results.append(drug)
        
        return results[:limit]
    
    def get_drug_by_name(self, name: str) -> Optional[Dict]:
        """Get drug by exact name (case-insensitive)"""
        return self.drugs_by_name.get(name.lower())
    
    def get_oncology_drugs(self, limit: int = 100) -> List[Dict]:
        """Get oncology-related drugs"""
        return self.oncology_compounds[:limit]
    
    def get_hero_cases(self) -> List[Dict]:
        """Get all hero repurposing cases"""
        return self.hero_cases
    
    def get_hero_case(self, drug_name: str) -> Optional[Dict]:
        """Get specific hero case by drug name"""
        for case in self.hero_cases:
            if case['drug_name'].lower() == drug_name.lower():
                return case
        return None
    
    def get_stats(self) -> Dict:
        """Get dataset statistics"""
        return {
            'total_drugs': len(self.broad_drugs),
            'total_samples': len(self.broad_samples),
            'oncology_compounds': len(self.oncology_compounds),
            'hero_cases': len(self.hero_cases),
            'mechanisms': len(self.drugs_by_moa),
            'targets': len(self.drugs_by_target)
        }
    
    def get_drugs_by_phase(self, phase: str) -> List[Dict]:
        """Get all drugs in a specific clinical phase"""
        return [d for d in self.broad_drugs if d.get('clinical_phase', '').lower() == phase.lower()]
    
    def get_drugs_by_mechanism(self, moa: str) -> List[Dict]:
        """Get all drugs with a specific mechanism of action"""
        return self.drugs_by_moa.get(moa, [])
    
    def get_drugs_by_target(self, target: str) -> List[Dict]:
        """Get all drugs targeting a specific gene/protein"""
        return self.drugs_by_target.get(target, [])


# Global data loader instance (singleton)
_data_loader: Optional[DataLoader] = None


def get_data_loader() -> DataLoader:
    """Get global data loader instance (lazy loading)"""
    global _data_loader
    if _data_loader is None:
        _data_loader = DataLoader()
    return _data_loader


if __name__ == "__main__":
    # Test data loader
    logging.basicConfig(level=logging.INFO)
    
    loader = DataLoader()
    
    print("\n" + "=" * 60)
    print("Data Loader Test")
    print("=" * 60)
    
    stats = loader.get_stats()
    print(f"\n📊 Statistics:")
    for key, value in stats.items():
        print(f"   {key}: {value:,}")
    
    print(f"\n🔍 Search Test: 'metformin'")
    results = loader.search_drugs('metformin')
    print(f"   Found {len(results)} results")
    if results:
        drug = results[0]
        print(f"   - {drug.get('pert_iname')}: {drug.get('clinical_phase')} - {drug.get('moa')}")
    
    print(f"\n🌟 Hero Cases:")
    for case in loader.get_hero_cases()[:5]:
        print(f"   - {case['drug_name']}: {case['confidence_score']}")
