"""
Business intelligence and market analysis models
"""

# Copyright (c) 2025 OncoPurpose (trovesx)
# All Rights Reserved.
# For licensing info, see LICENSE or contact oncopurpose@trovesx.com

from typing import Optional

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin


class MarketAnalysis(Base, UUIDMixin):
    """Market analysis for drug-cancer opportunities"""
    
    __tablename__ = "market_analysis"
    
    drug_id: Mapped[str] = mapped_column(
        ForeignKey("drugs.id"),
        nullable=False,
    )
    cancer_id: Mapped[str] = mapped_column(
        ForeignKey("cancers.id"),
        nullable=False,
    )
    prediction_id: Mapped[str] = mapped_column(
        ForeignKey("drug_cancer_predictions.id"),
        nullable=False,
    )
    
    # Market size estimates (in USD)
    tam_estimate: Mapped[Optional[int]] = mapped_column(
        Integer
    )  # Total Addressable Market
    sam_estimate: Mapped[Optional[int]] = mapped_column(
        Integer
    )  # Serviceable Addressable Market
    som_estimate: Mapped[Optional[int]] = mapped_column(
        Integer
    )  # Serviceable Obtainable Market
    
    # Market metrics
    average_treatment_cost: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    patient_population: Mapped[Optional[int]] = mapped_column(Integer)
    market_growth_rate: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    
    # Competitive landscape
    competitive_landscape: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Timing
    calculated_at: Mapped[Date] = mapped_column(Date, nullable=False)
    
    # Relationships
    drug = relationship("Drug", back_populates="market_analyses")
    cancer = relationship("Cancer", back_populates="market_analyses")
    prediction = relationship("DrugCancerPrediction", back_populates="market_analyses")
    
    def __repr__(self) -> str:
        return (
            f"<MarketAnalysis(drug_id={self.drug_id}, "
            f"cancer_id={self.cancer_id})>"
        )


class ClinicalTrial(Base, UUIDMixin):
    """Clinical trials information"""
    
    __tablename__ = "clinical_trials"
    
    nct_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )  # ClinicalTrials.gov ID
    
    drug_id: Mapped[str] = mapped_column(
        ForeignKey("drugs.id"),
        nullable=False,
    )
    cancer_id: Mapped[str] = mapped_column(
        ForeignKey("cancers.id"),
        nullable=False,
    )
    
    # Trial information
    title: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )  # recruiting, active, completed, terminated
    phase: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True,
    )  # 1, 2, 3, 4
    sponsor: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Timeline
    start_date: Mapped[Optional[Date]] = mapped_column(Date)
    completion_date: Mapped[Optional[Date]] = mapped_column(Date)
    enrollment_count: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Outcomes
    primary_outcome: Mapped[Optional[str]] = mapped_column(Text)
    results_summary: Mapped[Optional[str]] = mapped_column(Text)
    trial_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Relationships
    drug = relationship("Drug", back_populates="clinical_trials")
    cancer = relationship("Cancer", back_populates="clinical_trials")
    
    def __repr__(self) -> str:
        return f"<ClinicalTrial(nct_id={self.nct_id}, title={self.title[:50]}...)>"


class Patent(Base, UUIDMixin):
    """Patent information for drugs"""
    
    __tablename__ = "patents"
    
    drug_id: Mapped[str] = mapped_column(
        ForeignKey("drugs.id"),
        nullable=False,
    )
    
    patent_number: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )
    
    patent_title: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Dates
    filing_date: Mapped[Optional[Date]] = mapped_column(Date)
    grant_date: Mapped[Optional[Date]] = mapped_column(Date)
    expiry_date: Mapped[Optional[Date]] = mapped_column(Date, index=True)
    
    # Status and ownership
    patent_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
    )  # active, expired, pending
    assignee: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Content
    claims: Mapped[Optional[str]] = mapped_column(Text)
    patent_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Relationships
    drug = relationship("Drug", back_populates="patents")
    
    def __repr__(self) -> str:
        return f"<Patent(patent_number={self.patent_number}, drug_id={self.drug_id})>"


class ROICalculation(Base, UUIDMixin):
    """ROI calculations for drug-cancer opportunities"""
    
    __tablename__ = "roi_calculations"
    
    drug_id: Mapped[str] = mapped_column(
        ForeignKey("drugs.id"),
        nullable=False,
    )
    cancer_id: Mapped[str] = mapped_column(
        ForeignKey("cancers.id"),
        nullable=False,
    )
    prediction_id: Mapped[str] = mapped_column(
        ForeignKey("drug_cancer_predictions.id"),
        nullable=False,
    )
    
    # Financial projections
    development_cost_estimate: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    development_timeline_months: Mapped[int] = mapped_column(Integer, nullable=False)
    projected_revenue_annual: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    projected_roi_5year: Mapped[float] = mapped_column(
        Numeric(5, 2),
        nullable=False,
    )
    
    # Assumptions used in calculation
    cost_assumptions: Mapped[dict] = mapped_column(JSONB, nullable=False)
    revenue_assumptions: Mapped[dict] = mapped_column(JSONB, nullable=False)
    
    # Timing
    calculated_at: Mapped[Date] = mapped_column(Date, nullable=False)
    
    # Relationships
    prediction = relationship("DrugCancerPrediction", back_populates="roi_calculations")
    
    def __repr__(self) -> str:
        return (
            f"<ROICalculation(drug_id={self.drug_id}, "
            f"cancer_id={self.cancer_id}, "
            f"roi_5year={self.projected_roi_5year})>"
        )


class RegulatoryPathway(Base, UUIDMixin):
    """Regulatory pathway recommendations"""
    
    __tablename__ = "regulatory_pathways"
    
    drug_id: Mapped[str] = mapped_column(
        ForeignKey("drugs.id"),
        nullable=False,
    )
    cancer_id: Mapped[str] = mapped_column(
        ForeignKey("cancers.id"),
        nullable=False,
    )
    prediction_id: Mapped[str] = mapped_column(
        ForeignKey("drug_cancer_predictions.id"),
        nullable=False,
    )
    
    regulatory_region: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )  # FDA, EMA, PMDA, etc
    pathway_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )  # 505b2, orphan, breakthrough, etc
    
    # Timeline and requirements
    estimated_timeline_months: Mapped[int] = mapped_column(Integer, nullable=False)
    required_studies: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    precedent_cases: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String))
    estimated_cost: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    
    # Relationships
    prediction = relationship("DrugCancerPrediction", back_populates="regulatory_pathways")
    
    def __repr__(self) -> str:
        return (
            f"<RegulatoryPathway(drug_id={self.drug_id}, "
            f"cancer_id={self.cancer_id}, "
            f"region={self.regulatory_region})>"
        )