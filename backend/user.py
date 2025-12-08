"""
User model and related schemas
"""

# Copyright (c) 2025 OncoPurpose (trovesx)
# All Rights Reserved.
# For licensing info, see LICENSE or contact oncopurpose@trovesx.com

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin


class User(Base, UUIDMixin):
    """User model for authentication and user management"""
    
    __tablename__ = "users"
    
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Role-based access control
    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="researcher",
    )  # admin, researcher, viewer
    
    # Subscription management
    subscription_tier: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="basic",
    )  # basic, professional, enterprise
    
    # User status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
    
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Relationships
    saved_opportunities = relationship(
        "UserSavedOpportunity",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    
    search_history = relationship(
        "UserSearch",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"


class UserSavedOpportunity(Base, UUIDMixin):
    """User's saved drug-cancer opportunities"""
    
    __tablename__ = "user_saved_opportunities"
    
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    drug_id: Mapped[str] = mapped_column(
        ForeignKey("drugs.id"),
        nullable=False,
    )
    cancer_id: Mapped[str] = mapped_column(
        ForeignKey("cancers.id"),
        nullable=False,
    )
    
    notes: Mapped[Optional[str]] = mapped_column(Text)
    tags: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String))
    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="medium",
    )  # low, medium, high
    
    # Relationships
    user = relationship("User", back_populates="saved_opportunities")
    drug = relationship("Drug", back_populates="saved_by_users")
    cancer = relationship("Cancer", back_populates="saved_by_users")
    
    def __repr__(self) -> str:
        return (
            f"<UserSavedOpportunity(user_id={self.user_id}, "
            f"drug_id={self.drug_id}, cancer_id={self.cancer_id}, "
            f"priority={self.priority})>"
        )


class UserSearch(Base, UUIDMixin):
    """User search history"""
    
    __tablename__ = "user_searches"
    
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    
    # Store search parameters as JSON
    search_query: Mapped[dict] = mapped_column(JSONB, nullable=False)
    results_count: Mapped[int] = mapped_column(nullable=False, default=0)
    
    # Relationships
    user = relationship("User", back_populates="search_history")
    
    def __repr__(self) -> str:
        return f"<UserSearch(user_id={self.user_id}, results_count={self.results_count})>"