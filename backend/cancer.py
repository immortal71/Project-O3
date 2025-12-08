"""
Cancer model and related schemas
"""

from typing import Optional

from sqlalchemy import ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin


class Cancer(Base, UUIDMixin):
    """Cancer types and related information"""
    
    __tablename__ = "cancers"
    
    cancer_type: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    cancer_subtype: Mapped[Optional[str]] = mapped_column(String(255))
    icd_code: Mapped[Optional[str]] = mapped_column(String(20), index=True)
    
    # Epidemiology data
    prevalence_global: Mapped[Optional[int]] = mapped_column(Integer)
    prevalence_us: Mapped[Optional[int]] = mapped_column(Integer)
    mortality_rate: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    five_year_survival_rate: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    
    # Clinical information
    standard_treatments: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String))
    biomarkers: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String))
    
    # Relationships
    predictions = relationship(
        "DrugCancerPrediction",
        back_populates="cancer",
        cascade="all, delete-orphan",
    )
    
    clinical_trials = relationship(
        "ClinicalTrial",
        back_populates="cancer",
        cascade="all, delete-orphan",
    )
    
    market_analyses = relationship(
        "MarketAnalysis",
        back_populates="cancer",
        cascade="all, delete-orphan",
    )
    
    saved_by_users = relationship(
        "UserSavedOpportunity",
        back_populates="cancer",
        cascade="all, delete-orphan",
    )
    
    dosing_recommendations = relationship(
        "DosingRecommendation",
        back_populates="cancer",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        return f"<Cancer(id={self.id}, type={self.cancer_type})>"
    
    @property
    def full_name(self) -> str:
        """Get full cancer name including subtype"""
        if self.cancer_subtype:
            return f"{self.cancer_type} - {self.cancer_subtype}"
        return self.cancer_type