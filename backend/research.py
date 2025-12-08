"""
Research paper and evidence models
"""

from typing import Optional

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin


class ResearchPaper(Base, UUIDMixin):
    """Research papers from various sources"""
    
    __tablename__ = "research_papers"
    
    pubmed_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )
    
    title: Mapped[str] = mapped_column(Text, nullable=False)
    authors: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    journal: Mapped[str] = mapped_column(String(255), nullable=False)
    publication_date: Mapped[Date] = mapped_column(Date, nullable=False, index=True)
    doi: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    abstract: Mapped[Optional[str]] = mapped_column(Text)
    full_text_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Metrics
    citation_count: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    relevance_score: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2),
        index=True,
    )
    
    # Classification
    paper_type: Mapped[Optional[str]] = mapped_column(
        String(50)
    )  # clinical_trial, review, case_study, etc
    
    # Relationships
    drug_associations = relationship(
        "DrugPaperAssociation",
        back_populates="paper",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        return f"<ResearchPaper(pubmed_id={self.pubmed_id}, title={self.title[:50]}...)>"


class DrugPaperAssociation(Base, UUIDMixin):
    """Association between drugs and research papers"""
    
    __tablename__ = "drug_paper_associations"
    
    drug_id: Mapped[str] = mapped_column(
        ForeignKey("drugs.id"),
        nullable=False,
    )
    paper_id: Mapped[str] = mapped_column(
        ForeignKey("research_papers.id"),
        nullable=False,
    )
    
    relevance_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    key_findings: Mapped[Optional[str]] = mapped_column(Text)
    
    # Evidence type
    evidence_type: Mapped[Optional[str]] = mapped_column(
        String(50)
    )  # mechanism, efficacy, safety, etc
    
    # Relationships
    drug = relationship("Drug", back_populates="papers")
    paper = relationship("ResearchPaper", back_populates="drug_associations")
    
    def __repr__(self) -> str:
        return (
            f"<DrugPaperAssociation(drug_id={self.drug_id}, "
            f"paper_id={self.paper_id})>"
        )