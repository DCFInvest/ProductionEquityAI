"""Database models for financial data ingestion."""
from datetime import date, datetime
from typing import Dict, Optional

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from db.base import Base


class TimestampMixin:
    """Mixin adding created/updated timestamps."""

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class Company(Base, TimestampMixin):
    """Company metadata keyed by ticker."""

    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    ticker = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    sector = Column(String(255), nullable=True)

    financial_statements = relationship("FinancialStatement", back_populates="company")
    prices = relationship("Price", back_populates="company")


class FinancialStatement(Base, TimestampMixin):
    """Historical financial statements stored as JSON payloads."""

    __tablename__ = "financial_statements"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    fiscal_date = Column(Date, nullable=False)
    statement_type = Column(String(50), nullable=False)
    data = Column(JSON, nullable=False)

    company = relationship("Company", back_populates="financial_statements")


class Price(Base, TimestampMixin):
    """Historical stock price record."""

    __tablename__ = "prices"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    adjusted_close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)

    company = relationship("Company", back_populates="prices")


class TreasuryRate(Base, TimestampMixin):
    """Treasury rates used for discounting cash flows."""

    __tablename__ = "treasury_rates"

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False, index=True)
    rate_type = Column(String(50), nullable=False)
    rate = Column(Float, nullable=False)


class IngestionRun(Base, TimestampMixin):
    """Metadata to track ingestion executions."""

    __tablename__ = "ingestion_runs"

    id = Column(Integer, primary_key=True)
    ticker = Column(String(10), nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    status = Column(String(20), nullable=False, default="started")
    message = Column(String(1024), nullable=True)


class DataQualityIssue(Base, TimestampMixin):
    """Data quality alerts raised during ingestion."""

    __tablename__ = "data_quality_issues"

    id = Column(Integer, primary_key=True)
    issue_type = Column(String(50), nullable=False)
    description = Column(String(1024), nullable=False)
    context = Column(JSON, nullable=True)
    resolved = Column(Integer, nullable=False, default=0)
