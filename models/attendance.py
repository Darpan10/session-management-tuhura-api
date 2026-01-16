from sqlalchemy import Column, Integer, ForeignKey, Date, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.db_connect import Base

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False)
    waitlist_id = Column(Integer, ForeignKey('waitlist.id', ondelete='CASCADE'), nullable=False)
    attendance_date = Column(Date, nullable=False)
    is_present = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    session = relationship("Session", back_populates="attendance_records")
    waitlist_entry = relationship("Waitlist")