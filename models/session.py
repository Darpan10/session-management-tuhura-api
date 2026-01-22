from sqlalchemy import Column, Integer, String, Text, Date, Time, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.db_connect import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    term = Column(String(100), nullable=False)  # Term name for backward compatibility
    description = Column(Text, nullable=True)  # New description field
    term_id = Column(Integer, ForeignKey("terms.id"), nullable=True)  # Keep for backward compatibility
    day_of_week = Column(String(20), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    location = Column(String(500), nullable=False)
    city = Column(String(200), nullable=False)
    location_url = Column(String(1000), nullable=True)
    capacity = Column(Integer, nullable=False)
    min_age = Column(Integer, nullable=False)
    max_age = Column(Integer, nullable=False)
    rrule = Column(Text, nullable=False)  # Precomputed RRULE
    is_deleted = Column(Boolean, default=False, nullable=False)  # Soft delete flag
    created_by = Column(Integer, ForeignKey("user.users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    term_ref = relationship("Term", back_populates="sessions")  # Old single term (backward compatibility)
    
    # Many-to-many relationship with terms
    terms = relationship(
        "Term",
        secondary="session_terms",
        backref="term_sessions"
    )
    
    # Relationship to staff members
    staff_members = relationship(
        "User",
        secondary="session_staff",
        backref="assigned_sessions"
    )

    # Relationship to attendance records
    attendance_records = relationship("Attendance", back_populates="session", cascade="all, delete-orphan")
