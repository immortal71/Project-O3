"""
Machine Learning prediction engine for drug-cancer matches
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.core.logging import get_struct_logger, LoggerMixin
from app.models.drug import Drug
from app.models.cancer import Cancer
from app.models.prediction import DrugCancerPrediction

logger = get_struct_logger(__name__)


class DrugCancerPredictor(LoggerMixin):
    """ML predictor for drug-cancer compatibility"""
    
    def __init__(self):
        self.model = None
        self.model_version = "v1.0.0"
        self.feature_names = []
        self.is_trained = False
        
        # Define feature categories
        self.drug_features = [
            "molecular_weight",
            "logp",
            "hbd_count",
            "hba_count",
            "rotatable_bonds",
            "aromatic_rings",
            "fraction_csp3",
            "tpsa",
            "complexity",
        ]
        
        self.cancer_features = [
            "prevalence_global",
            "prevalence_us",
            "mortality_rate",
            "five_year_survival_rate",
        ]
        
        self.mechanism_features = [
            "target_pathway_score",
            "mechanism_similarity",
            "known_targets_count",
        ]
    
    def extract_drug_features(self, smiles: str) -> Dict[str, float]:
        """Extract molecular features from SMILES notation"""
        
        features = {}
        
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return self._get_default_drug_features()
            
            # Basic molecular descriptors
            features["molecular_weight"] = Descriptors.MolWt(mol)
            features["logp"] = Descriptors.MolLogP(mol)
            features["hbd_count"] = Descriptors.NumHDonors(mol)
            features["hba_count"] = Descriptors.NumHAcceptors(mol)
            features["rotatable_bonds"] = Descriptors.NumRotatableBonds(mol)
            features["aromatic_rings"] = Descriptors.NumAromaticRings(mol)
            features["fraction_csp3"] = Descriptors.FractionCSP3(mol)
            features["tpsa"] = Descriptors.TPSA(mol)
            features["complexity"] = Descriptors.BertzCT(mol)
            
        except Exception as e:
            self.log_error(
                "Error extracting drug features",
                extra={"error": str(e), "smiles": smiles},
            )
            features = self._get_default_drug_features()
        
        return features
    
    def _get_default_drug_features(self) -> Dict[str, float]:
        """Get default features for invalid molecules"""
        return {feature: 0.0 for feature in self.drug_features}
    
    def calculate_mechanism_features(
        self,
        drug_mechanism: str,
        cancer_type: str,
    ) -> Dict[str, float]:
        """Calculate mechanism-based features"""
        
        features = {
            "target_pathway_score": 0.0,
            "mechanism_similarity": 0.0,
            "known_targets_count": 0.0,
        }
        
        try:
            # Define known cancer pathways and their associated mechanisms
            pathway_mappings = {
                "breast": ["estrogen", "progesterone", "her2", "pi3k", "mtor"],
                "lung": ["egfr", "alk", "ros1", "pd-l1", "kras"],
                "colorectal": ["kras", "nras", "braf", "msi", "egfr"],
                "prostate": ["androgen", "ar", "psa"],
                "leukemia": ["bcr-abl", "jak2", "flt3", "kit"],
            }
            
            # Normalize inputs
            drug_mechanism_lower = drug_mechanism.lower() if drug_mechanism else ""
            cancer_type_lower = cancer_type.lower() if cancer_type else ""
            
            # Calculate pathway score
            pathway_keywords = pathway_mappings.get(cancer_type_lower, [])
            matching_keywords = [
                keyword
                for keyword in pathway_keywords
                if keyword in drug_mechanism_lower
            ]
            
            features["target_pathway_score"] = len(matching_keywords) / max(
                len(pathway_keywords), 1
            )
            
            # Calculate known targets count
            known_targets = [
                "mtor",
                "pi3k",
                "akt",
                "mapk",
                "ras",
                "raf",
                "mek",
                "er",
                "pr",
                "her2",
                "egfr",
                "vegfr",
                "pdgfr",
                "kit",
                "flt3",
                "jak",
                "stat",
                "hdac",
                "parp",
                "cdk",
                "chk",
                "atm",
                "atr",
                "dna",
                "rna",
                "protein",
                "enzyme",
                "receptor",
            ]
            
            features["known_targets_count"] = sum(
                1 for target in known_targets if target in drug_mechanism_lower
            )
            
            # Calculate mechanism similarity (simplified)
            if any(keyword in drug_mechanism_lower for keyword in ["inhibitor", "blocker"]):
                features["mechanism_similarity"] = 0.8
            elif any(keyword in drug_mechanism_lower for keyword in ["agonist", "activator"]):
                features["mechanism_similarity"] = 0.6
            else:
                features["mechanism_similarity"] = 0.4
                
        except Exception as e:
            self.log_error(
                "Error calculating mechanism features",
                extra={"error": str(e), "drug_mechanism": drug_mechanism, "cancer_type": cancer_type},
            )
        
        return features
    
    def prepare_features(
        self,
        drug: Drug,
        cancer: Cancer,
    ) -> np.ndarray:
        """Prepare feature vector for prediction"""
        
        features = []
        
        # Drug features
        drug_feats = self.extract_drug_features(drug.chemical_structure or "")
        features.extend([drug_feats[f] for f in self.drug_features])
        
        # Cancer features
        cancer_feats = [
            cancer.prevalence_global or 0,
            cancer.prevalence_us or 0,
            cancer.mortality_rate or 0,
            cancer.five_year_survival_rate or 0,
        ]
        features.extend(cancer_feats)
        
        # Mechanism features
        mech_feats = self.calculate_mechanism_features(
            drug.mechanism_of_action or "",
            cancer.cancer_type,
        )
        features.extend([mech_feats[f] for f in self.mechanism_features])
        
        return np.array(features).reshape(1, -1)
    
    async def train_model(self, db: AsyncSession) -> bool:
        """Train the prediction model with existing data"""
        
        try:
            self.log_info("Starting model training")
            
            # Get training data from database
            # For now, we'll use a simplified approach with synthetic data
            # In production, this would use real historical data
            
            # Generate synthetic training data based on known successful repurposing cases
            training_data = self._generate_training_data()
            
            X = np.array([sample["features"] for sample in training_data])
            y = np.array([sample["label"] for sample in training_data])
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Train model
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                class_weight="balanced",
            )
            
            self.model.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = self.model.predict(X_test)
            report = classification_report(y_test, y_pred, output_dict=True)
            
            self.log_info(
                "Model training completed",
                extra={
                    "accuracy": report["accuracy"],
                    "f1_score": report["weighted avg"]["f1-score"],
                },
            )
            
            self.is_trained = True
            return True
            
        except Exception as e:
            self.log_error("Model training failed", extra={"error": str(e)})
            return False
    
    def _generate_training_data(self) -> List[Dict]:
        """Generate synthetic training data based on known drug repurposing cases"""
        
        # Known successful repurposing cases
        successful_cases = [
            {
                "drug": "Metformin",
                "cancer": "Breast Cancer",
                "features": [
                    # Drug features (Metformin)
                    129.16,  # molecular_weight
                    -1.43,   # logp
                    4,       # hbd_count
                    2,       # hba_count
                    2,       # rotatable_bonds
                    0,       # aromatic_rings
                    0.25,    # fraction_csp3
                    63.18,   # tpsa
                    45.2,    # complexity
                    # Cancer features (Breast Cancer)
                    2100000,  # prevalence_global
                    280000,   # prevalence_us
                    15.4,     # mortality_rate
                    90.3,     # five_year_survival_rate
                    # Mechanism features
                    0.8,      # target_pathway_score
                    0.7,      # mechanism_similarity
                    2,        # known_targets_count
                ],
                "label": 1,  # Successful
            },
            {
                "drug": "Aspirin",
                "cancer": "Colorectal Cancer",
                "features": [
                    # Drug features (Aspirin)
                    180.16,  # molecular_weight
                    -1.24,   # logp
                    1,       # hbd_count
                    4,       # hba_count
                    2,       # rotatable_bonds
                    1,       # aromatic_rings
                    0.2,     # fraction_csp3
                    63.6,    # tpsa
                    120.5,   # complexity
                    # Cancer features (Colorectal Cancer)
                    1900000,  # prevalence_global
                    150000,   # prevalence_us
                    32.1,     # mortality_rate
                    65.1,     # five_year_survival_rate
                    # Mechanism features
                    0.6,      # target_pathway_score
                    0.5,      # mechanism_similarity
                    1,        # known_targets_count
                ],
                "label": 1,  # Successful
            },
            # Negative examples (less likely to work)
            {
                "drug": "Antibiotic",
                "cancer": "Leukemia",
                "features": [
                    # Drug features (representative antibiotic)
                    350.0,   # molecular_weight
                    1.5,     # logp
                    2,       # hbd_count
                    6,       # hba_count
                    5,       # rotatable_bonds
                    0,       # aromatic_rings
                    0.7,     # fraction_csp3
                    120.0,   # tpsa
                    200.0,   # complexity
                    # Cancer features (Leukemia)
                    450000,   # prevalence_global
                    60000,    # prevalence_us
                    45.2,     # mortality_rate
                    65.8,     # five_year_survival_rate
                    # Mechanism features
                    0.1,      # target_pathway_score
                    0.2,      # mechanism_similarity
                    0,        # known_targets_count
                ],
                "label": 0,  # Unsuccessful
            },
        ]
        
        # Add more synthetic examples for better training
        training_data = successful_cases.copy()
        
        # Generate variations of successful cases
        for case in successful_cases[:2]:  # Only for the successful cases
            for i in range(10):  # Generate 10 variations
                variation = case.copy()
                variation["features"] = case["features"].copy()
                
                # Add some noise to features
                for j in range(len(variation["features"])):
                    noise = np.random.normal(0, 0.1 * abs(variation["features"][j]))
                    variation["features"][j] += noise
                
                # Keep the label but with some probability of being negative
                if np.random.random() < 0.1:  # 10% chance of being negative
                    variation["label"] = 0
                
                training_data.append(variation)
        
        return training_data
    
    async def predict(
        self,
        drug: Drug,
        cancer: Cancer,
        db: AsyncSession,
    ) -> Dict[str, any]:
        """Make prediction for drug-cancer pair"""
        
        if not self.is_trained:
            # Train model if not already trained
            await self.train_model(db)
        
        try:
            # Prepare features
            features = self.prepare_features(drug, cancer)
            
            # Make prediction
            confidence = self.model.predict_proba(features)[0][1]  # Probability of success
            prediction = self.model.predict(features)[0]
            
            # Convert to confidence score (0-100)
            confidence_score = confidence * 100
            
            # Determine evidence strength
            if confidence_score >= 80:
                evidence_strength = "high"
            elif confidence_score >= 60:
                evidence_strength = "medium"
            else:
                evidence_strength = "low"
            
            # Generate mechanism hypothesis
            mechanism_hypothesis = self._generate_mechanism_hypothesis(
                drug.mechanism_of_action or "",
                cancer.cancer_type,
                confidence_score,
            )
            
            # Generate predicted efficacy
            predicted_efficacy = self._generate_predicted_efficacy(
                confidence_score,
                cancer.five_year_survival_rate,
            )
            
            # Generate safety concerns
            safety_concerns = self._generate_safety_concerns(drug, cancer)
            
            return {
                "confidence_score": confidence_score,
                "evidence_strength": evidence_strength,
                "mechanism_hypothesis": mechanism_hypothesis,
                "predicted_efficacy": predicted_efficacy,
                "safety_concerns": safety_concerns,
                "prediction_model_version": self.model_version,
            }
            
        except Exception as e:
            self.log_error(
                "Prediction failed",
                extra={
                    "error": str(e),
                    "drug_id": drug.id,
                    "cancer_id": cancer.id,
                },
            )
            
            # Return default prediction
            return {
                "confidence_score": 50.0,
                "evidence_strength": "low",
                "mechanism_hypothesis": "Unknown mechanism",
                "predicted_efficacy": "Efficacy data not available",
                "safety_concerns": ["Standard safety monitoring required"],
                "prediction_model_version": self.model_version,
            }
    
    def _generate_mechanism_hypothesis(
        self,
        drug_mechanism: str,
        cancer_type: str,
        confidence_score: float,
    ) -> str:
        """Generate mechanism hypothesis based on drug mechanism and cancer type"""
        
        if not drug_mechanism:
            return "Mechanism of action not specified"
        
        # Define cancer-specific pathways
        pathways = {
            "breast": "hormone receptor pathways",
            "lung": "EGFR and angiogenesis pathways",
            "colorectal": "Wnt and MAPK pathways",
            "prostate": "androgen receptor pathway",
            "leukemia": "cell cycle and apoptosis pathways",
        }
        
        cancer_pathway = pathways.get(cancer_type.lower(), "cancer-related pathways")
        
        if confidence_score >= 80:
            return (
                f"Strong evidence suggests {drug_mechanism} effectively targets "
                f"{cancer_pathway} in {cancer_type} cancer through direct pathway inhibition"
            )
        elif confidence_score >= 60:
            return (
                f"Moderate evidence indicates {drug_mechanism} may target "
                f"{cancer_pathway} in {cancer_type} cancer through indirect mechanisms"
            )
        else:
            return (
                f"Limited evidence suggests {drug_mechanism} might affect "
                f"{cancer_pathway} in {cancer_type} cancer, but mechanism is unclear"
            )
    
    def _generate_predicted_efficacy(
        self,
        confidence_score: float,
        survival_rate: Optional[float],
    ) -> str:
        """Generate predicted efficacy statement"""
        
        if confidence_score >= 80:
            efficacy = "High predicted efficacy"
            improvement = "significant improvement"
        elif confidence_score >= 60:
            efficacy = "Moderate predicted efficacy"
            improvement = "moderate improvement"
        else:
            efficacy = "Low predicted efficacy"
            improvement = "limited improvement"
        
        if survival_rate:
            return (
                f"{efficacy} with {improvement} in progression-free survival. "
                f"Expected to enhance current 5-year survival rate of {survival_rate:.1f}%"
            )
        else:
            return f"{efficacy} with {improvement} in clinical outcomes"
    
    def _generate_safety_concerns(self, drug: Drug, cancer: Cancer) -> List[str]:
        """Generate safety concerns based on drug and cancer"""
        
        concerns = []
        
        # Standard concerns
        concerns.append("Monitor for standard adverse events")
        
        # Cancer-specific concerns
        if "breast" in cancer.cancer_type.lower():
            concerns.append("Monitor for hormone-related side effects")
        elif "lung" in cancer.cancer_type.lower():
            concerns.append("Monitor for respiratory complications")
        elif "colorectal" in cancer.cancer_type.lower():
            concerns.append("Monitor for gastrointestinal toxicity")
        
        # Drug-specific concerns based on mechanism
        if drug.mechanism_of_action:
            mechanism_lower = drug.mechanism_of_action.lower()
            if any(word in mechanism_lower for word in ["kinase", "inhibitor"]):
                concerns.append("Monitor for kinase-related toxicities")
            elif any(word in mechanism_lower for word in ["hormone", "receptor"]):
                concerns.append("Monitor for endocrine dysfunction")
        
        return concerns
    
    async def save_prediction(
        self,
        db: AsyncSession,
        drug_id: str,
        cancer_id: str,
        prediction_data: Dict,
    ) -> Optional[str]:
        """Save prediction to database"""
        
        try:
            # Check if prediction already exists
            existing = await db.execute(
                select(DrugCancerPrediction).where(
                    DrugCancerPrediction.drug_id == drug_id,
                    DrugCancerPrediction.cancer_id == cancer_id,
                )
            )
            
            if existing.scalar_one_or_none():
                # Update existing prediction
                prediction = existing.scalar_one_or_none()
                prediction.confidence_score = prediction_data["confidence_score"]
                prediction.evidence_strength = prediction_data["evidence_strength"]
                prediction.mechanism_hypothesis = prediction_data["mechanism_hypothesis"]
                prediction.predicted_efficacy = prediction_data["predicted_efficacy"]
                prediction.safety_concerns = prediction_data["safety_concerns"]
                prediction.prediction_model_version = prediction_data["prediction_model_version"]
            else:
                # Create new prediction
                prediction = DrugCancerPrediction(
                    drug_id=drug_id,
                    cancer_id=cancer_id,
                    confidence_score=prediction_data["confidence_score"],
                    evidence_strength=prediction_data["evidence_strength"],
                    mechanism_hypothesis=prediction_data["mechanism_hypothesis"],
                    predicted_efficacy=prediction_data["predicted_efficacy"],
                    safety_concerns=prediction_data["safety_concerns"],
                    prediction_model_version=prediction_data["prediction_model_version"],
                )
                db.add(prediction)
            
            await db.commit()
            
            self.log_info(
                "Prediction saved to database",
                extra={
                    "drug_id": drug_id,
                    "cancer_id": cancer_id,
                    "confidence_score": prediction_data["confidence_score"],
                },
            )
            
            return prediction.id
            
        except Exception as e:
            await db.rollback()
            self.log_error(
                "Error saving prediction to database",
                extra={
                    "error": str(e),
                    "drug_id": drug_id,
                    "cancer_id": cancer_id,
                },
            )
            return None


# Global predictor instance
predictor = DrugCancerPredictor()