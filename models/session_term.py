from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from core.db_connect import Base


class SessionTerm(Base):
    """Association table for many-to-many relationship between sessions and terms"""
    __tablename__ = "session_terms"

    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), primary_key=True)
    term_id = Column(Integer, ForeignKey("terms.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
