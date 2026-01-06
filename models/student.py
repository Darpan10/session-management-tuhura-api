from sqlalchemy import Column, Integer, String, Boolean, Text, ARRAY, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from core.db_connect import Base
import enum


class SchoolYear(str, enum.Enum):
    YEAR_5 = "Year 5"
    YEAR_6 = "Year 6"
    YEAR_7 = "Year 7"
    YEAR_8 = "Year 8"
    YEAR_9 = "Year 9"
    YEAR_10 = "Year 10"
    YEAR_11 = "Year 11"
    YEAR_12 = "Year 12"
    YEAR_13 = "Year 13"
    OTHER = "Other"


class Student(Base):
    __tablename__ = "students"
    __table_args__ = {"schema": "student"}

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    family_name = Column(String, nullable=False)
    school_year = Column(SQLEnum(SchoolYear), nullable=False)
    school_year_other = Column(String, nullable=True)  # For "Other" school year
    
    # Experience as JSON array
    experience = Column(ARRAY(String), nullable=True)
    
    needs_device = Column(Boolean, nullable=False)
    medical_info = Column(Text, nullable=True)
    
    # Parent/Guardian details
    parent_name = Column(String, nullable=False)
    parent_phone = Column(String, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
