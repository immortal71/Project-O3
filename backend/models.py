"""
Database models for OncoPurpose
SQLAlchemy ORM models matching the MySQL schema
"""

from sqlalchemy import Column, Integer, String, Text, DECIMAL, TIMESTAMP, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Drug(Base):
    __tablename__ = 'drugs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    drug_name = Column(String(255), nullable=False, index=True)
    clinical_phase = Column(String(50), index=True)
    mechanism_of_action = Column(Text)
    target = Column(String(500))
    disease_area = Column(String(255))
    indication = Column(Text)
    source = Column(String(50), default='broad_hub', index=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    mechanisms = relationship('DrugMechanism', back_populates='drug', cascade='all, delete-orphan')
    targets = relationship('DrugTarget', back_populates='drug', cascade='all, delete-orphan')


class HeroCase(Base):
    __tablename__ = 'hero_cases'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    drug_name = Column(String(255), nullable=False, index=True)
    original_indication = Column(String(255))
    repurposed_cancer = Column(String(255), nullable=False)
    confidence_score = Column(DECIMAL(3, 2), index=True)
    trial_count = Column(Integer, default=0)
    citations = Column(Integer, default=0)
    mechanism = Column(Text)
    pathways = Column(Text)
    evidence_level = Column(String(50))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)


class GeneratedOutput(Base):
    __tablename__ = 'generated_outputs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    output_type = Column(String(50), nullable=False, index=True)
    drug_name = Column(String(255), index=True)
    cancer_type = Column(String(255))
    input_parameters = Column(JSON)
    output_data = Column(JSON)
    file_path = Column(String(500))
    confidence_score = Column(DECIMAL(3, 2))
    status = Column(String(50), default='completed')
    user_id = Column(String(100))
    session_id = Column(String(100), index=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, index=True)


class Mechanism(Base):
    __tablename__ = 'mechanisms'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    mechanism_name = Column(String(255), nullable=False, unique=True, index=True)
    drug_count = Column(Integer, default=0)
    description = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    drugs = relationship('DrugMechanism', back_populates='mechanism')


class Target(Base):
    __tablename__ = 'targets'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    target_name = Column(String(255), nullable=False, unique=True, index=True)
    drug_count = Column(Integer, default=0)
    description = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    drugs = relationship('DrugTarget', back_populates='target')


class DrugMechanism(Base):
    __tablename__ = 'drug_mechanisms'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    drug_id = Column(Integer, ForeignKey('drugs.id', ondelete='CASCADE'), nullable=False)
    mechanism_id = Column(Integer, ForeignKey('mechanisms.id', ondelete='CASCADE'), nullable=False)
    
    # Relationships
    drug = relationship('Drug', back_populates='mechanisms')
    mechanism = relationship('Mechanism', back_populates='drugs')
    
    __table_args__ = (
        Index('unique_drug_mechanism', 'drug_id', 'mechanism_id', unique=True),
    )


class DrugTarget(Base):
    __tablename__ = 'drug_targets'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    drug_id = Column(Integer, ForeignKey('drugs.id', ondelete='CASCADE'), nullable=False)
    target_id = Column(Integer, ForeignKey('targets.id', ondelete='CASCADE'), nullable=False)
    
    # Relationships
    drug = relationship('Drug', back_populates='targets')
    target = relationship('Target', back_populates='drugs')
    
    __table_args__ = (
        Index('unique_drug_target', 'drug_id', 'target_id', unique=True),
    )


class AnalyticsCache(Base):
    __tablename__ = 'analytics_cache'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cache_key = Column(String(255), nullable=False, unique=True, index=True)
    cache_value = Column(JSON)
    expires_at = Column(TIMESTAMP, index=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)


class ActivityLog(Base):
    __tablename__ = 'activity_log'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), index=True)
    action = Column(String(100), index=True)
    endpoint = Column(String(255))
    parameters = Column(JSON)
    response_time_ms = Column(Integer)
    status_code = Column(Integer)
    ip_address = Column(String(45))
    created_at = Column(TIMESTAMP, default=datetime.utcnow, index=True)
