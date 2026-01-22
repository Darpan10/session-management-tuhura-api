from sqlalchemy import Column, Integer, String, Date, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.db_connect import Base


class Term(Base):
    """Global term configuration with fixed start/end dates"""
    __tablename__ = "terms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)  # e.g., "Term 1", "Term 2"
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    year = Column(Integer, nullable=False)  # e.g., 2026
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Many-to-many relationship to sessions
    sessions = relationship("Session", secondary="session_terms", back_populates="terms")
