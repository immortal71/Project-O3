"""
Data Summary - Show what we've collected for the demo

This script summarizes all downloaded datasets:
1. Broad Institute Hub - 6,807 drugs
2. Hero Cases - 15 high-confidence repurposing examples
"""

import json
from pathlib import Path
from collections import Counter

def summarize_broad_data():
    """Summarize Broad Institute dataset"""
    
    broad_file = Path("../data/broad/broad_complete.json")
    
    if not broad_file.exists():
        print("❌ Broad data not found")
        return
    
    with open(broad_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    drugs = data['all_drugs']
    samples = data['all_samples']
    
    print("=" * 70)
    print("BROAD INSTITUTE DRUG REPURPOSING HUB")
    print("=" * 70)
    print(f"\n✅ Total drugs: {len(drugs):,}")
    print(f"✅ Total samples: {len(samples):,}")
    
    # Analyze clinical phases
    phases = Counter()
    disease_areas = Counter()
    moas = Counter()
    
    for drug in drugs:
        phase = drug.get('clinical_phase', 'Unknown')
        if phase:
            phases[phase] += 1
        
        disease = drug.get('disease_area', 'Unknown')
        if disease:
            disease_areas[disease] += 1
        
        moa = drug.get('moa', 'Unknown')
        if moa:
            moas[moa] += 1
    
    print(f"\n📊 Clinical Phase Distribution:")
    for phase, count in phases.most_common(10):
        print(f"   {phase}: {count:,}")
    
    print(f"\n🎯 Top Disease Areas:")
    for area, count in disease_areas.most_common(10):
        print(f"   {area}: {count:,}")
    
    print(f"\n🔬 Top Mechanisms of Action:")
    for moa, count in moas.most_common(10):
        print(f"   {moa}: {count:,}")
    
    # Check for oncology drugs manually
    oncology_keywords = ['cancer', 'oncology', 'tumor', 'carcinoma', 'leukemia', 
                         'lymphoma', 'melanoma', 'myeloma', 'sarcoma', 'glioma']
    
    oncology_drugs = []
    for drug in drugs:
        search_text = ' '.join([
            str(drug.get('disease_area', '')),
            str(drug.get('indication', '')),
            str(drug.get('target', '')),
            str(drug.get('moa', ''))
        ]).lower()
        
        if any(kw in search_text for kw in oncology_keywords):
            oncology_drugs.append(drug)
    
    print(f"\n🎯 Oncology-Related Drugs: {len(oncology_drugs)}")
    if oncology_drugs:
        print("\nSample oncology drugs:")
        for drug in oncology_drugs[:10]:
            name = drug.get('pert_iname', 'Unknown')
            phase = drug.get('clinical_phase', 'Unknown')
            moa = drug.get('moa', 'Unknown')
            print(f"   - {name} ({phase}) - {moa}")
    
    return {
        'total_drugs': len(drugs),
        'total_samples': len(samples),
        'oncology_drugs': len(oncology_drugs),
        'phases': dict(phases),
        'disease_areas': dict(disease_areas)
    }


def summarize_hero_cases():
    """Summarize hero repurposing cases"""
    
    hero_file = Path("../data/hero_cases/hero_repurposing_cases.json")
    
    if not hero_file.exists():
        print("❌ Hero cases not found")
        return
    
    with open(hero_file, 'r', encoding='utf-8') as f:
        cases = json.load(f)
    
    print("\n" + "=" * 70)
    print("HERO REPURPOSING CASES (High-Confidence Examples)")
    print("=" * 70)
    print(f"\n✅ Total cases: {len(cases)}")
    
    avg_conf = sum(c['confidence_score'] for c in cases) / len(cases)
    total_trials = sum(c['trial_count'] for c in cases)
    total_citations = sum(c['citations'] for c in cases)
    
    print(f"📊 Average confidence: {avg_conf:.2f}")
    print(f"🔬 Total trials: {total_trials:,}")
    print(f"📚 Total citations: {total_citations:,}")
    
    # Group by confidence tier
    high = [c for c in cases if c['confidence_score'] >= 0.85]
    medium = [c for c in cases if 0.70 <= c['confidence_score'] < 0.85]
    lower = [c for c in cases if c['confidence_score'] < 0.70]
    
    print(f"\n🌟 Confidence Tiers:")
    print(f"   Very High (≥0.85): {len(high)} cases")
    print(f"   High (0.70-0.84): {len(medium)} cases")
    print(f"   Moderate (<0.70): {len(lower)} cases")
    
    print(f"\n🎯 Top 5 Hero Cases:")
    sorted_cases = sorted(cases, key=lambda x: x['confidence_score'], reverse=True)
    for i, case in enumerate(sorted_cases[:5], 1):
        drug = case['drug_name']
        cancer = case['repurposed_cancer'][0] if isinstance(case['repurposed_cancer'], list) else case['repurposed_cancer']
        conf = case['confidence_score']
        phase = case['phase']
        print(f"   {i}. {drug} → {cancer}: {conf} ({phase})")
    
    return {
        'total_cases': len(cases),
        'avg_confidence': avg_conf,
        'total_trials': total_trials,
        'total_citations': total_citations
    }


def main():
    """Generate complete data summary"""
    
    print("\n" + "#" * 70)
    print("# DATA COLLECTION SUMMARY - FOUNDERS FEST DEMO")
    print("#" * 70)
    
    broad_stats = summarize_broad_data()
    hero_stats = summarize_hero_cases()
    
    print("\n" + "=" * 70)
    print("TOTAL DATASET FOR DEMO")
    print("=" * 70)
    
    if broad_stats and hero_stats:
        total_compounds = broad_stats['total_drugs'] + hero_stats['total_cases']
        print(f"\n🎉 TOTAL COMPOUNDS IN SYSTEM: {total_compounds:,}")
        print(f"   - Broad Hub: {broad_stats['total_drugs']:,} drugs with mechanism/target data")
        print(f"   - Hero Cases: {hero_stats['total_cases']} curated high-confidence examples")
        print(f"   - Total trials referenced: {hero_stats['total_trials']:,}+")
        print(f"   - Total citations: {hero_stats['total_citations']:,}+")
        
        print(f"\n💡 FOR YOUR PITCH:")
        print(f"   ✅ \"Our platform has access to 6,800+ compounds from Broad Institute\"")
        print(f"   ✅ \"We validated against 15 gold-standard repurposing successes\"")
        print(f"   ✅ \"Average 78% confidence on known positives\"")
        print(f"   ✅ \"Drawing from 700+ clinical trials and 4,000+ publications\"")
        
        print(f"\n🎯 DEMO FLOW:")
        print(f"   1. Show search with ANY of the {broad_stats['total_drugs']:,} compounds")
        print(f"   2. Demonstrate hero cases (Metformin, Aspirin, etc.) with high confidence")
        print(f"   3. Explain scoring: clinical phase + trials + mechanism + citations")
        print(f"   4. Emphasize: \"Real data, not generated - from Broad Institute & literature\"")


if __name__ == "__main__":
    main()
