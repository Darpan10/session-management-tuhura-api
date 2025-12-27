from sqlalchemy import Column, Integer, String, Text, Date, Time, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.db_connect import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    term = Column(String(50), nullable=False)
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
    created_by = Column(Integer, ForeignKey("auth.users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship to staff members
    staff_members = relationship(
        "User",
        secondary="session_staff",
        backref="assigned_sessions"
    )
