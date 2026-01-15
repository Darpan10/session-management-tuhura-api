from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.db_connect import Base
import enum


class WaitlistStatus(str, enum.Enum):
    WAITLIST = "waitlist"
    ADMITTED = "admitted"
    WITHDRAWN = "withdrawn"


class HeardFrom(str, enum.Enum):
    NEWSLETTER = "Newsletter"
    SCHOOL = "School"
    POSTER = "Poster"
    INSTAGRAM = "Instagram"
    FACEBOOK = "Facebook"
    WORD_OF_MOUTH = "Word of mouth"
    INTERNET_SEARCH = "Internet Search"
    RETURNING = "Returning"
    OTHER = "Other"


class Waitlist(Base):
    __tablename__ = "waitlist"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)

    # Consents
    consent_share_details = Column(Boolean, nullable=False)
    consent_photos = Column(Boolean, nullable=False)

    # How did you hear about us
    heard_from = Column(SQLEnum(HeardFrom, values_callable=lambda x: [e.value for e in x]), nullable=False)
    heard_from_other = Column(String, nullable=True)  # For "Other" option

    # Newsletter subscription
    newsletter_subscribe = Column(Boolean, nullable=False)

    # Status
    status = Column(SQLEnum(WaitlistStatus, values_callable=lambda x: [e.value for e in x]), default=WaitlistStatus.WAITLIST, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    student = relationship("Student", backref="waitlist_entries")
    session = relationship("Session", backref="waitlist_entries")