"""
Prediction models for drug-cancer matches
"""

from typing import Optional

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin


class DrugCancerPrediction(Base, UUIDMixin):
    """ML predictions for drug-cancer matches"""
    
    __tablename__ = "drug_cancer_predictions"
    
    drug_id: Mapped[str] = mapped_column(
        ForeignKey("drugs.id"),
        nullable=False,
    )
    cancer_id: Mapped[str] = mapped_column(
        ForeignKey("cancers.id"),
        nullable=False,
    )
    
    # Prediction results
    confidence_score: Mapped[float] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        index=True,
    )  # 0-100 scale
    
    prediction_model_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    
    evidence_strength: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )  # low, medium, high
    
    # Supporting information
    mechanism_hypothesis: Mapped[Optional[str]] = mapped_column(Text)
    predicted_efficacy: Mapped[Optional[str]] = mapped_column(Text)
    safety_concerns: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String))
    
    # Relationships
    drug = relationship("Drug", back_populates="predictions")
    cancer = relationship("Cancer", back_populates="predictions")
    
    market_analyses = relationship(
        "MarketAnalysis",
        back_populates="prediction",
        cascade="all, delete-orphan",
    )
    
    roi_calculations = relationship(
        "ROICalculation",
        back_populates="prediction",
        cascade="all, delete-orphan",
    )
    
    regulatory_pathways = relationship(
        "RegulatoryPathway",
        back_populates="prediction",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        return (
            f"<DrugCancerPrediction(drug_id={self.drug_id}, "
            f"cancer_id={self.cancer_id}, "
            f"confidence_score={self.confidence_score})>"
        )
    
    @property
    def confidence_category(self) -> str:
        """Categorize confidence score"""
        if self.confidence_score >= 90:
            return "Very High"
        elif self.confidence_score >= 80:
            return "High"
        elif self.confidence_score >= 70:
            return "Medium"
        elif self.confidence_score >= 60:
            return "Low"
        else:
            return "Very Low"