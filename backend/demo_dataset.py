"""
Pre-loaded Demo Dataset
Contains 15 well-known oncology drug repurposing examples
These are GUARANTEED to work in the demo - no ML/AI needed!

Based on:
- Published literature
- repoDB approved pairs
- Active clinical trials
- ReDO_DB oncology candidates
"""

DEMO_REPURPOSING_CASES = [
    {
        "id": "demo_001",
        "drug_name": "Metformin",
        "original_indication": "Type 2 Diabetes",
        "cancer_type": "Breast Cancer",
        "confidence_score": 0.87,
        "status": "Phase 3 Clinical Trials",
        "evidence": {
            "clinical_trials": 156,
            "pubmed_citations": 450,
            "mechanism": "AMPK activation, mTOR inhibition, reduces insulin/IGF-1 signaling",
            "pathways": ["AMPK signaling", "mTOR pathway", "Insulin/IGF-1 axis"],
            "phase": "Phase 3",
            "sources": ["repoDB", "ClinicalTrials.gov", "ReDO_DB"]
        },
        "market_potential": {
            "patient_population": 280000,
            "tam_usd": 4200000000,
            "avg_treatment_cost_usd": 15000,
            "competitive_landscape": "Low - generic drug, minimal competition"
        },
        "demo_priority": 1  # Most important demo case
    },
    {
        "id": "demo_002",
        "drug_name": "Aspirin",
        "original_indication": "Pain Relief, Cardiovascular Protection",
        "cancer_type": "Colorectal Cancer",
        "confidence_score": 0.92,
        "status": "Approved/Ongoing Studies",
        "evidence": {
            "clinical_trials": 89,
            "pubmed_citations": 320,
            "mechanism": "COX-2 inhibition, reduces prostaglandin E2, anti-inflammatory",
            "pathways": ["COX-2/prostaglandin pathway", "Inflammation", "Platelet aggregation"],
            "phase": "Phase 3/Prevention Studies",
            "sources": ["repoDB", "ClinicalTrials.gov", "Published meta-analyses"]
        },
        "market_potential": {
            "patient_population": 150000,
            "tam_usd": 2800000000,
            "avg_treatment_cost_usd": 18000,
            "competitive_landscape": "Very low - OTC drug"
        },
        "demo_priority": 1
    },
    {
        "id": "demo_003",
        "drug_name": "Atorvastatin",
        "original_indication": "High Cholesterol",
        "cancer_type": "Prostate Cancer",
        "confidence_score": 0.78,
        "status": "Phase 2 Clinical Trials",
        "evidence": {
            "clinical_trials": 45,
            "pubmed_citations": 180,
            "mechanism": "HMG-CoA reductase inhibition, reduces mevalonate pathway, anti-proliferative",
            "pathways": ["Mevalonate pathway", "RAS/RHO GTPases", "Cholesterol metabolism"],
            "phase": "Phase 2",
            "sources": ["ClinicalTrials.gov", "ReDO_DB", "Broad Drug Repurposing Hub"]
        },
        "market_potential": {
            "patient_population": 220000,
            "tam_usd": 3500000000,
            "avg_treatment_cost_usd": 16000,
            "competitive_landscape": "Low - generic statin"
        },
        "demo_priority": 1
    },
    {
        "id": "demo_004",
        "drug_name": "Ibuprofen",
        "original_indication": "Pain Relief, Inflammation",
        "cancer_type": "Lung Cancer",
        "confidence_score": 0.65,
        "status": "Preclinical/Early Phase",
        "evidence": {
            "clinical_trials": 23,
            "pubmed_citations": 95,
            "mechanism": "COX inhibition, reduces inflammation, induces apoptosis",
            "pathways": ["COX pathway", "NF-κB signaling", "Apoptosis"],
            "phase": "Phase 1/2",
            "sources": ["PubMed", "Preclinical studies", "ReDO_DB"]
        },
        "market_potential": {
            "patient_population": 230000,
            "tam_usd": 5200000000,
            "avg_treatment_cost_usd": 22000,
            "competitive_landscape": "Very low - OTC NSAID"
        },
        "demo_priority": 2
    },
    {
        "id": "demo_005",
        "drug_name": "Thalidomide",
        "original_indication": "Leprosy, Morning Sickness (withdrawn)",
        "cancer_type": "Multiple Myeloma",
        "confidence_score": 0.95,
        "status": "FDA Approved",
        "evidence": {
            "clinical_trials": 234,
            "pubmed_citations": 580,
            "mechanism": "Immunomodulation, anti-angiogenesis, TNF-α inhibition",
            "pathways": ["Angiogenesis", "Immune modulation", "TNF-α pathway"],
            "phase": "Approved",
            "sources": ["FDA", "repoDB", "ClinicalTrials.gov"]
        },
        "market_potential": {
            "patient_population": 32000,
            "tam_usd": 2400000000,
            "avg_treatment_cost_usd": 75000,
            "competitive_landscape": "Medium - approved but niche"
        },
        "demo_priority": 1
    },
    {
        "id": "demo_006",
        "drug_name": "Celecoxib",
        "original_indication": "Arthritis Pain",
        "cancer_type": "Colorectal Cancer",
        "confidence_score": 0.81,
        "status": "Phase 3 Clinical Trials",
        "evidence": {
            "clinical_trials": 67,
            "pubmed_citations": 210,
            "mechanism": "Selective COX-2 inhibition, reduces polyp formation",
            "pathways": ["COX-2 pathway", "Prostaglandin synthesis", "Apoptosis"],
            "phase": "Phase 3",
            "sources": ["ClinicalTrials.gov", "repoDB", "ReDO_DB"]
        },
        "market_potential": {
            "patient_population": 150000,
            "tam_usd": 2900000000,
            "avg_treatment_cost_usd": 19000,
            "competitive_landscape": "Low - generic available"
        },
        "demo_priority": 2
    },
    {
        "id": "demo_007",
        "drug_name": "Valproic Acid",
        "original_indication": "Epilepsy, Bipolar Disorder",
        "cancer_type": "Glioblastoma",
        "confidence_score": 0.72,
        "status": "Phase 2 Clinical Trials",
        "evidence": {
            "clinical_trials": 34,
            "pubmed_citations": 150,
            "mechanism": "HDAC inhibition, epigenetic modulation, induces differentiation",
            "pathways": ["HDAC pathway", "Epigenetic regulation", "Cell differentiation"],
            "phase": "Phase 2",
            "sources": ["ClinicalTrials.gov", "ReDO_DB", "Broad Drug Repurposing Hub"]
        },
        "market_potential": {
            "patient_population": 18000,
            "tam_usd": 1200000000,
            "avg_treatment_cost_usd": 65000,
            "competitive_landscape": "Medium - limited options for glioblastoma"
        },
        "demo_priority": 2
    },
    {
        "id": "demo_008",
        "drug_name": "Mebendazole",
        "original_indication": "Parasitic Worm Infections",
        "cancer_type": "Glioblastoma",
        "confidence_score": 0.68,
        "status": "Phase 1/2 Clinical Trials",
        "evidence": {
            "clinical_trials": 12,
            "pubmed_citations": 78,
            "mechanism": "Microtubule disruption, inhibits glucose uptake, anti-angiogenic",
            "pathways": ["Tubulin polymerization", "Glucose metabolism", "VEGF pathway"],
            "phase": "Phase 1/2",
            "sources": ["ClinicalTrials.gov", "ReDO_DB", "Case reports"]
        },
        "market_potential": {
            "patient_population": 18000,
            "tam_usd": 950000000,
            "avg_treatment_cost_usd": 52000,
            "competitive_landscape": "Low - generic antiparasitic"
        },
        "demo_priority": 2
    },
    {
        "id": "demo_009",
        "drug_name": "Propranolol",
        "original_indication": "High Blood Pressure, Anxiety",
        "cancer_type": "Melanoma",
        "confidence_score": 0.70,
        "status": "Phase 2 Clinical Trials",
        "evidence": {
            "clinical_trials": 28,
            "pubmed_citations": 120,
            "mechanism": "Beta-adrenergic blockade, reduces stress-induced tumor growth",
            "pathways": ["β-adrenergic signaling", "Stress response", "Angiogenesis"],
            "phase": "Phase 2",
            "sources": ["ClinicalTrials.gov", "ReDO_DB", "Preclinical studies"]
        },
        "market_potential": {
            "patient_population": 96000,
            "tam_usd": 1800000000,
            "avg_treatment_cost_usd": 19000,
            "competitive_landscape": "Low - generic beta-blocker"
        },
        "demo_priority": 2
    },
    {
        "id": "demo_010",
        "drug_name": "Metformin",
        "original_indication": "Type 2 Diabetes",
        "cancer_type": "Pancreatic Cancer",
        "confidence_score": 0.75,
        "status": "Phase 2 Clinical Trials",
        "evidence": {
            "clinical_trials": 34,
            "pubmed_citations": 180,
            "mechanism": "AMPK activation, reduces insulin resistance, metabolic stress",
            "pathways": ["AMPK signaling", "mTOR pathway", "Metabolic reprogramming"],
            "phase": "Phase 2",
            "sources": ["ClinicalTrials.gov", "ReDO_DB", "repoDB"]
        },
        "market_potential": {
            "patient_population": 62000,
            "tam_usd": 1900000000,
            "avg_treatment_cost_usd": 31000,
            "competitive_landscape": "Low - generic drug"
        },
        "demo_priority": 1
    },
    {
        "id": "demo_011",
        "drug_name": "Doxycycline",
        "original_indication": "Bacterial Infections",
        "cancer_type": "Breast Cancer",
        "confidence_score": 0.62,
        "status": "Preclinical/Phase 1",
        "evidence": {
            "clinical_trials": 15,
            "pubmed_citations": 85,
            "mechanism": "Inhibits mitochondrial protein synthesis, targets cancer stem cells",
            "pathways": ["Mitochondrial function", "Cancer stem cells", "MMP inhibition"],
            "phase": "Phase 1",
            "sources": ["ReDO_DB", "Preclinical studies", "Broad Drug Repurposing Hub"]
        },
        "market_potential": {
            "patient_population": 280000,
            "tam_usd": 3200000000,
            "avg_treatment_cost_usd": 11500,
            "competitive_landscape": "Very low - generic antibiotic"
        },
        "demo_priority": 3
    },
    {
        "id": "demo_012",
        "drug_name": "Simvastatin",
        "original_indication": "High Cholesterol",
        "cancer_type": "Liver Cancer",
        "confidence_score": 0.73,
        "status": "Phase 2 Clinical Trials",
        "evidence": {
            "clinical_trials": 31,
            "pubmed_citations": 140,
            "mechanism": "HMG-CoA reductase inhibition, reduces mevalonate pathway",
            "pathways": ["Mevalonate pathway", "RAS activation", "Cell proliferation"],
            "phase": "Phase 2",
            "sources": ["ClinicalTrials.gov", "ReDO_DB", "repoDB"]
        },
        "market_potential": {
            "patient_population": 42000,
            "tam_usd": 1600000000,
            "avg_treatment_cost_usd": 38000,
            "competitive_landscape": "Low - generic statin"
        },
        "demo_priority": 2
    },
    {
        "id": "demo_013",
        "drug_name": "Aspirin",
        "original_indication": "Pain Relief, Cardiovascular Protection",
        "cancer_type": "Lung Cancer",
        "confidence_score": 0.67,
        "status": "Phase 2/Prevention Studies",
        "evidence": {
            "clinical_trials": 42,
            "pubmed_citations": 190,
            "mechanism": "COX-2 inhibition, anti-inflammatory, platelet modulation",
            "pathways": ["COX pathway", "Inflammation", "Tumor microenvironment"],
            "phase": "Phase 2",
            "sources": ["ClinicalTrials.gov", "Prevention trials", "Meta-analyses"]
        },
        "market_potential": {
            "patient_population": 230000,
            "tam_usd": 4500000000,
            "avg_treatment_cost_usd": 19500,
            "competitive_landscape": "Very low - OTC drug"
        },
        "demo_priority": 1
    },
    {
        "id": "demo_014",
        "drug_name": "Sildenafil",
        "original_indication": "Erectile Dysfunction, Pulmonary Hypertension",
        "cancer_type": "Colorectal Cancer",
        "confidence_score": 0.58,
        "status": "Preclinical/Early Phase",
        "evidence": {
            "clinical_trials": 8,
            "pubmed_citations": 45,
            "mechanism": "PDE5 inhibition, enhances immune response, modulates MDSCs",
            "pathways": ["PDE5/cGMP pathway", "Immune modulation", "MDSC regulation"],
            "phase": "Preclinical/Phase 1",
            "sources": ["Preclinical studies", "ReDO_DB", "Broad Drug Repurposing Hub"]
        },
        "market_potential": {
            "patient_population": 150000,
            "tam_usd": 2100000000,
            "avg_treatment_cost_usd": 14000,
            "competitive_landscape": "Low - generic available"
        },
        "demo_priority": 3
    },
    {
        "id": "demo_015",
        "drug_name": "Chloroquine",
        "original_indication": "Malaria",
        "cancer_type": "Glioblastoma",
        "confidence_score": 0.64,
        "status": "Phase 1/2 Clinical Trials",
        "evidence": {
            "clinical_trials": 19,
            "pubmed_citations": 105,
            "mechanism": "Autophagy inhibition, lysosomotropic agent, sensitizes to chemo",
            "pathways": ["Autophagy", "Lysosomal function", "p53 pathway"],
            "phase": "Phase 1/2",
            "sources": ["ClinicalTrials.gov", "ReDO_DB", "Preclinical studies"]
        },
        "market_potential": {
            "patient_population": 18000,
            "tam_usd": 850000000,
            "avg_treatment_cost_usd": 47000,
            "competitive_landscape": "Low - generic antimalarial"
        },
        "demo_priority": 3
    }
]


# Export as JSON for easy import
if __name__ == "__main__":
    import json
    from pathlib import Path
    
    output_dir = Path("../data/demo")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "demo_dataset.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(DEMO_REPURPOSING_CASES, f, indent=2)
    
    print(f"✅ Demo dataset created: {output_file}")
    print(f"   - {len(DEMO_REPURPOSING_CASES)} pre-loaded repurposing cases")
    print(f"   - Priority 1 cases: {len([c for c in DEMO_REPURPOSING_CASES if c['demo_priority'] == 1])}")
    print(f"   - Avg confidence: {sum(c['confidence_score'] for c in DEMO_REPURPOSING_CASES) / len(DEMO_REPURPOSING_CASES):.2f}")
