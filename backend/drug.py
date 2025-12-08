"""
Drug model and related schemas
"""

from typing import Optional

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin


class Drug(Base, UUIDMixin):
    """Drug information and properties"""
    
    __tablename__ = "drugs"
    
    drug_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    drugbank_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )
    pubchem_id: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    
    # Chemical properties
    chemical_structure: Mapped[Optional[str]] = mapped_column(
        Text
    )  # SMILES notation
    molecular_weight: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    
    # Clinical information
    primary_indication: Mapped[str] = mapped_column(String(500), nullable=False)
    approval_status: Mapped[Optional[str]] = mapped_column(
        String(100)
    )  # FDA, EMA, etc
    patent_expiry_date: Mapped[Optional[Date]] = mapped_column(Date)
    manufacturer: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Mechanism and classification
    mechanism_of_action: Mapped[Optional[str]] = mapped_column(Text)
    drug_class: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Relationships
    predictions = relationship(
        "DrugCancerPrediction",
        back_populates="drug",
        cascade="all, delete-orphan",
    )
    
    papers = relationship(
        "DrugPaperAssociation",
        back_populates="drug",
        cascade="all, delete-orphan",
    )
    
    clinical_trials = relationship(
        "ClinicalTrial",
        back_populates="drug",
        cascade="all, delete-orphan",
    )
    
    patents = relationship(
        "Patent",
        back_populates="drug",
        cascade="all, delete-orphan",
    )
    
    market_analyses = relationship(
        "MarketAnalysis",
        back_populates="drug",
        cascade="all, delete-orphan",
    )
    
    saved_by_users = relationship(
        "UserSavedOpportunity",
        back_populates="drug",
        cascade="all, delete-orphan",
    )
    
    safety_profiles = relationship(
        "SafetyProfile",
        back_populates="drug",
        cascade="all, delete-orphan",
    )
    
    dosing_recommendations = relationship(
        "DosingRecommendation",
        back_populates="drug",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        return f"<Drug(id={self.id}, name={self.drug_name}, drugbank_id={self.drugbank_id})>"


class SafetyProfile(Base, UUIDMixin):
    """Drug safety information and adverse events"""
    
    __tablename__ = "safety_profiles"
    
    drug_id: Mapped[str] = mapped_column(
        ForeignKey("drugs.id"),
        nullable=False,
    )
    
    # Adverse events with frequency
    adverse_events: Mapped[Optional[list[dict]]] = mapped_column(JSONB)
    
    # Contraindications
    contraindications: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String))
    
    # Drug interactions
    drug_interactions: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String))
    
    # Warnings
    black_box_warnings: Mapped[Optional[str]] = mapped_column(Text)
    
    # Monitoring requirements
    monitoring_requirements: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String))
    
    # Pregnancy and organ impairment
    pregnancy_category: Mapped[Optional[str]] = mapped_column(String(10))
    hepatic_impairment_guidance: Mapped[Optional[str]] = mapped_column(Text)
    renal_impairment_guidance: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relationships
    drug = relationship("Drug", back_populates="safety_profiles")
    
    def __repr__(self) -> str:
        return f"<SafetyProfile(drug_id={self.drug_id})>"


class DosingRecommendation(Base, UUIDMixin):
    """Dosing recommendations for drug-cancer combinations"""
    
    __tablename__ = "dosing_recommendations"
    
    drug_id: Mapped[str] = mapped_column(
        ForeignKey("drugs.id"),
        nullable=False,
    )
    cancer_id: Mapped[str] = mapped_column(
        ForeignKey("cancers.id"),
        nullable=False,
    )
    
    # Dosing information
    recommended_dose: Mapped[str] = mapped_column(String(100), nullable=False)
    dose_unit: Mapped[str] = mapped_column(String(50), nullable=False)
    frequency: Mapped[str] = mapped_column(String(100), nullable=False)
    route_of_administration: Mapped[str] = mapped_column(String(100), nullable=False)
    duration_weeks: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Source information
    based_on_indication: Mapped[str] = mapped_column(String(255), nullable=False)
    source_references: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String))
    
    # Relationships
    drug = relationship("Drug", back_populates="dosing_recommendations")
    cancer = relationship("Cancer", back_populates="dosing_recommendations")
    
    def __repr__(self) -> str:
        return (
            f"<DosingRecommendation(drug_id={self.drug_id}, "
            f"cancer_id={self.cancer_id})>"
        )