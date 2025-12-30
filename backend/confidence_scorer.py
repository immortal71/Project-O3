"""
Rule-Based Confidence Scoring Engine
NO ML/AI - just smart heuristics based on real data

Scoring factors:
1. Clinical trial phase (40%)
2. Number of trials (20%)
3. Publication citations (15%)
4. Data source credibility (15%)
5. Mechanism strength (10%)
"""

from enum import Enum
from typing import Dict, List


class ClinicalPhase(Enum):
    """Clinical trial phases with scoring weights"""
    APPROVED = 1.0
    PHASE_3 = 0.85
    PHASE_2 = 0.65
    PHASE_1 = 0.45
    PRECLINICAL = 0.25
    UNKNOWN = 0.1


class DataSource(Enum):
    """Data source credibility weights"""
    REPODB = 0.95
    FDA = 1.0
    CLINICALTRIALS_GOV = 0.90
    REDO_DB = 0.85
    BROAD_HUB = 0.80
    PUBMED = 0.75
    PRECLINICAL = 0.50


class ConfidenceScorer:
    """Rule-based confidence scorer for drug repurposing"""
    
    def __init__(self):
        self.weights = {
            'phase': 0.40,
            'trial_count': 0.20,
            'citations': 0.15,
            'sources': 0.15,
            'mechanism': 0.10
        }
    
    def score_clinical_phase(self, phase_str: str) -> float:
        """Score based on clinical development phase"""
        phase_map = {
            'approved': ClinicalPhase.APPROVED,
            'phase 3': ClinicalPhase.PHASE_3,
            'phase 2': ClinicalPhase.PHASE_2,
            'phase 1': ClinicalPhase.PHASE_1,
            'preclinical': ClinicalPhase.PRECLINICAL
        }
        
        phase_str_lower = phase_str.lower()
        
        for key, phase in phase_map.items():
            if key in phase_str_lower:
                return phase.value
        
        return ClinicalPhase.UNKNOWN.value
    
    def score_trial_count(self, count: int) -> float:
        """Score based on number of clinical trials"""
        if count >= 100:
            return 1.0
        elif count >= 50:
            return 0.85
        elif count >= 20:
            return 0.70
        elif count >= 10:
            return 0.55
        elif count >= 5:
            return 0.40
        elif count >= 1:
            return 0.25
        else:
            return 0.0
    
    def score_citations(self, count: int) -> float:
        """Score based on PubMed citations"""
        if count >= 300:
            return 1.0
        elif count >= 150:
            return 0.85
        elif count >= 75:
            return 0.70
        elif count >= 30:
            return 0.55
        elif count >= 10:
            return 0.40
        elif count >= 1:
            return 0.25
        else:
            return 0.0
    
    def score_sources(self, sources: List[str]) -> float:
        """Score based on data source credibility"""
        if not sources:
            return 0.0
        
        source_scores = []
        
        for source in sources:
            source_lower = source.lower()
            
            if 'repodb' in source_lower:
                source_scores.append(DataSource.REPODB.value)
            elif 'fda' in source_lower:
                source_scores.append(DataSource.FDA.value)
            elif 'clinicaltrials' in source_lower:
                source_scores.append(DataSource.CLINICALTRIALS_GOV.value)
            elif 'redo' in source_lower:
                source_scores.append(DataSource.REDO_DB.value)
            elif 'broad' in source_lower:
                source_scores.append(DataSource.BROAD_HUB.value)
            elif 'pubmed' in source_lower:
                source_scores.append(DataSource.PUBMED.value)
            else:
                source_scores.append(DataSource.PRECLINICAL.value)
        
        # Average of top 3 sources
        source_scores.sort(reverse=True)
        top_sources = source_scores[:3]
        
        return sum(top_sources) / len(top_sources)
    
    def score_mechanism(self, pathways: List[str]) -> float:
        """Score based on mechanism complexity/clarity"""
        if not pathways:
            return 0.3
        
        # More pathways = better understood mechanism
        pathway_count = len(pathways)
        
        if pathway_count >= 4:
            return 1.0
        elif pathway_count == 3:
            return 0.85
        elif pathway_count == 2:
            return 0.70
        elif pathway_count == 1:
            return 0.55
        else:
            return 0.3
    
    def calculate_confidence(self, evidence: Dict) -> float:
        """
        Calculate overall confidence score
        
        Args:
            evidence: Dict with keys:
                - phase: Clinical phase string
                - clinical_trials: Number of trials
                - pubmed_citations: Number of citations
                - sources: List of data sources
                - pathways: List of mechanism pathways
        
        Returns:
            Confidence score between 0 and 1
        """
        
        # Score each component
        phase_score = self.score_clinical_phase(evidence.get('phase', ''))
        trial_score = self.score_trial_count(evidence.get('clinical_trials', 0))
        citation_score = self.score_citations(evidence.get('pubmed_citations', 0))
        source_score = self.score_sources(evidence.get('sources', []))
        mechanism_score = self.score_mechanism(evidence.get('pathways', []))
        
        # Weighted combination
        confidence = (
            phase_score * self.weights['phase'] +
            trial_score * self.weights['trial_count'] +
            citation_score * self.weights['citations'] +
            source_score * self.weights['sources'] +
            mechanism_score * self.weights['mechanism']
        )
        
        # Ensure bounds
        return max(0.0, min(1.0, confidence))
    
    def get_confidence_tier(self, score: float) -> str:
        """Get human-readable confidence tier"""
        if score >= 0.85:
            return "Very High"
        elif score >= 0.70:
            return "High"
        elif score >= 0.55:
            return "Moderate"
        elif score >= 0.40:
            return "Low"
        else:
            return "Very Low"
    
    def explain_score(self, evidence: Dict) -> Dict:
        """
        Provide detailed explanation of confidence score
        
        Returns breakdown of all scoring components
        """
        
        phase_score = self.score_clinical_phase(evidence.get('phase', ''))
        trial_score = self.score_trial_count(evidence.get('clinical_trials', 0))
        citation_score = self.score_citations(evidence.get('pubmed_citations', 0))
        source_score = self.score_sources(evidence.get('sources', []))
        mechanism_score = self.score_mechanism(evidence.get('pathways', []))
        
        total_score = self.calculate_confidence(evidence)
        
        return {
            'overall_score': round(total_score, 2),
            'tier': self.get_confidence_tier(total_score),
            'breakdown': {
                'clinical_phase': {
                    'score': round(phase_score, 2),
                    'weight': self.weights['phase'],
                    'contribution': round(phase_score * self.weights['phase'], 2)
                },
                'trial_count': {
                    'score': round(trial_score, 2),
                    'weight': self.weights['trial_count'],
                    'contribution': round(trial_score * self.weights['trial_count'], 2)
                },
                'citations': {
                    'score': round(citation_score, 2),
                    'weight': self.weights['citations'],
                    'contribution': round(citation_score * self.weights['citations'], 2)
                },
                'data_sources': {
                    'score': round(source_score, 2),
                    'weight': self.weights['sources'],
                    'contribution': round(source_score * self.weights['sources'], 2)
                },
                'mechanism': {
                    'score': round(mechanism_score, 2),
                    'weight': self.weights['mechanism'],
                    'contribution': round(mechanism_score * self.weights['mechanism'], 2)
                }
            }
        }


# Example usage and testing
if __name__ == "__main__":
    scorer = ConfidenceScorer()
    
    # Test with metformin-breast cancer example
    metformin_evidence = {
        'phase': 'Phase 3',
        'clinical_trials': 156,
        'pubmed_citations': 450,
        'sources': ['repoDB', 'ClinicalTrials.gov', 'ReDO_DB'],
        'pathways': ['AMPK signaling', 'mTOR pathway', 'Insulin/IGF-1 axis']
    }
    
    score = scorer.calculate_confidence(metformin_evidence)
    explanation = scorer.explain_score(metformin_evidence)
    
    print("🧪 Test: Metformin for Breast Cancer")
    print(f"   Overall Score: {score:.2f}")
    print(f"   Tier: {scorer.get_confidence_tier(score)}")
    print("\n   Breakdown:")
    for component, details in explanation['breakdown'].items():
        print(f"      {component}: {details['score']:.2f} × {details['weight']:.2f} = {details['contribution']:.2f}")
