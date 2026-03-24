"""
SQLAlchemy ORM models for the AI API Platform.
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Text, Boolean, DateTime, JSON, ForeignKey
)
from sqlalchemy.orm import relationship
from database import Base


class APICategory(Base):
    __tablename__ = "api_categories"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    name          = Column(String(100), unique=True, nullable=False)
    display_name  = Column(String(150), nullable=False)
    description   = Column(Text, default="")
    icon          = Column(String(10), default="🔗")
    keywords      = Column(JSON, default=list)          # list[str] for matching

    apis          = relationship("APIEntry", back_populates="category")


class APIEntry(Base):
    __tablename__ = "api_entries"

    id                 = Column(Integer, primary_key=True, autoincrement=True)
    name               = Column(String(200), nullable=False)
    slug               = Column(String(200), unique=True, nullable=False)
    provider           = Column(String(200), default="")
    description        = Column(Text, default="")
    category_id        = Column(Integer, ForeignKey("api_categories.id"))

    # Discovery metadata
    free_tier           = Column(Boolean, default=False)
    pricing_model       = Column(String(50), default="freemium")   # free, freemium, paid, open-source
    pricing_details     = Column(Text, default="")
    auth_type           = Column(String(50), default="api_key")    # api_key, oauth2, none, basic
    documentation_url   = Column(String(500), default="")
    base_url            = Column(String(500), default="")
    sdk_languages       = Column(JSON, default=list)               # ["python","js","go"]
    request_limit       = Column(String(100), default="")
    github_url          = Column(String(500), default="")

    # Scoring
    popularity_score    = Column(Float, default=50.0)
    doc_quality_score   = Column(Float, default=50.0)
    reliability_score   = Column(Float, default=50.0)
    latency_score       = Column(Float, default=50.0)
    pricing_score       = Column(Float, default=50.0)
    composite_score     = Column(Float, default=50.0)

    # Status
    is_active           = Column(Boolean, default=True)
    last_verified       = Column(DateTime, nullable=True)
    last_response_ms    = Column(Integer, nullable=True)
    tags                = Column(JSON, default=list)
    alternatives        = Column(JSON, default=list)               # list of slugs

    created_at          = Column(DateTime, default=datetime.utcnow)
    updated_at          = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category            = relationship("APICategory", back_populates="apis")
    health_checks       = relationship("HealthCheck", back_populates="api_entry")


class HealthCheck(Base):
    __tablename__ = "health_checks"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    api_entry_id   = Column(Integer, ForeignKey("api_entries.id"))
    checked_at     = Column(DateTime, default=datetime.utcnow)
    is_reachable   = Column(Boolean, default=False)
    status_code    = Column(Integer, nullable=True)
    response_ms    = Column(Integer, nullable=True)
    doc_reachable  = Column(Boolean, default=False)
    error          = Column(Text, default="")

    api_entry      = relationship("APIEntry", back_populates="health_checks")


class GeneratedProject(Base):
    __tablename__ = "generated_projects"

    id               = Column(Integer, primary_key=True, autoincrement=True)
    project_name     = Column(String(200), nullable=False)
    original_files   = Column(JSON, default=dict)          # {filename: code}
    analysis_result  = Column(JSON, default=dict)
    framework        = Column(String(50), default="fastapi")
    generated_files  = Column(JSON, default=dict)          # {filename: code}
    openapi_spec     = Column(JSON, default=dict)
    deployment_configs = Column(JSON, default=dict)
    created_at       = Column(DateTime, default=datetime.utcnow)

class UserSettings(Base):
    __tablename__ = "user_settings"

    id               = Column(Integer, primary_key=True, autoincrement=True)
    github_token     = Column(String(500), nullable=True)
    default_repo     = Column(String(200), nullable=True)
    updated_at       = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
