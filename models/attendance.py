from sqlalchemy import Column, Integer, ForeignKey, Date, DateTime, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.db_connect import Base

class Attendance(Base):
    """Attendance table - stores both PRESENT and ABSENT records.
    is_present: True for present, False for absent."""
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False)
    waitlist_id = Column(Integer, ForeignKey('waitlist.id', ondelete='CASCADE'), nullable=False)
    attendance_date = Column(Date, nullable=False)
    is_present = Column(Boolean, nullable=False, default=True)  # True = Present, False = Absent
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    session = relationship("Session", back_populates="attendance_records")
    waitlist_entry = relationship("Waitlist")
    
    # Ensure one attendance record per student per date
    __table_args__ = (
        UniqueConstraint('session_id', 'waitlist_id', 'attendance_date', name='uix_attendance'),
    )
