# backend/models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy import JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .db import Base


class Upload(Base):
    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    backtests = relationship("BacktestRun", back_populates="upload")


class BacktestRun(Base):
    __tablename__ = "backtest_runs"

    id = Column(Integer, primary_key=True, index=True)
    upload_id = Column(Integer, ForeignKey("uploads.id"), nullable=False)
    metrics = Column(JSON, nullable=False)
    equity_curve_path = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    upload = relationship("Upload", back_populates="backtests")
    suggestions = relationship("Suggestion", back_populates="backtest_run")


class Suggestion(Base):
    __tablename__ = "suggestions"

    id = Column(Integer, primary_key=True, index=True)
    backtest_run_id = Column(Integer, ForeignKey("backtest_runs.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    risk_note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    backtest_run = relationship("BacktestRun", back_populates="suggestions")