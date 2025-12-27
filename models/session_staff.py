from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from core.db_connect import Base


class SessionStaff(Base):
    """Association table for sessions and staff members"""
    __tablename__ = "session_staff"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    staff_id = Column(Integer, ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
