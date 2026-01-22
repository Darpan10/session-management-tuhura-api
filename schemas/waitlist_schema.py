from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional
from datetime import datetime


class StudentSignupRequest(BaseModel):
    # Student details
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    family_name: str = Field(..., min_length=1, max_length=100)
    session_id: int
    school_year: str
    school_year_other: Optional[str] = None
    experience: List[str] = []
    needs_device: bool
    medical_info: Optional[str] = None

    # Parent/Guardian details
    parent_name: str = Field(..., min_length=1, max_length=100)
    parent_phone: str = Field(..., min_length=1, max_length=20)

    # Consents
    consent_share_details: bool
    consent_photos: bool

    # Marketing
    heard_from: str
    heard_from_other: Optional[str] = None
    newsletter_subscribe: bool

    @validator('school_year_other')
    def validate_school_year_other(cls, v, values):
        if values.get('school_year') == 'Other' and not v:
            raise ValueError('school_year_other is required when school_year is Other')
        return v

    @validator('heard_from_other')
    def validate_heard_from_other(cls, v, values):
        if values.get('heard_from') == 'Other' and not v:
            raise ValueError('heard_from_other is required when heard_from is Other')
        return v

    class Config:
        from_attributes = True


class StudentResponse(BaseModel):
    id: int
    email: str
    first_name: str
    family_name: str
    school_year: str
    school_year_other: Optional[str]
    experience: List[str]
    needs_device: bool
    medical_info: Optional[str]
    parent_name: str
    parent_phone: str
    created_at: datetime

    class Config:
        from_attributes = True


class WaitlistResponse(BaseModel):
    id: int
    student_id: int
    session_id: int
    consent_share_details: bool
    consent_photos: bool
    heard_from: str
    heard_from_other: Optional[str]
    newsletter_subscribe: bool
    status: str
    created_at: datetime

    # Include student and session details
    student: Optional[StudentResponse] = None

    class Config:
        from_attributes = True


class WaitlistEntryWithDetails(BaseModel):
    id: int
    student_id: Optional[int] = None
    first_name: Optional[str] = None
    family_name: Optional[str] = None
    student_name: str
    student_email: str
    parent_name: str
    parent_phone: str
    school_year: str
    school_year_other: Optional[str] = None
    experience: Optional[List[str]] = []
    needs_device: bool
    medical_info: Optional[str] = None
    consent_share_details: Optional[bool] = None
    consent_photos: Optional[bool] = None
    heard_from: Optional[str] = None
    heard_from_other: Optional[str] = None
    newsletter_subscribe: Optional[bool] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class StudentUpdateRequest(BaseModel):
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    family_name: str = Field(..., min_length=1, max_length=100)
    school_year: str
    school_year_other: Optional[str] = None
    experience: List[str] = []
    needs_device: bool
    medical_info: Optional[str] = None
    parent_name: str = Field(..., min_length=1, max_length=100)
    parent_phone: str = Field(..., min_length=1, max_length=20)

    class Config:
        from_attributes = True


class BulkStatusUpdateRequest(BaseModel):
    waitlist_ids: List[int] = Field(..., min_items=1)
    new_status: str = Field(..., pattern="^(waitlist|admitted|withdrawn)$")

    class Config:
        from_attributes = True


class BulkStatusUpdateResponse(BaseModel):
    updated_count: int
    message: str

class SessionStudentCount(BaseModel):
    """Session with student count for a specific status"""
    id: int
    title: str
    term: str
    dayOfWeek: str = Field(alias='day_of_week')
    startDate: str = Field(alias='start_date')
    endDate: str = Field(alias='end_date')
    startTime: str = Field(alias='start_time')
    endTime: str = Field(alias='end_time')
    location: str
    city: str
    studentCount: int = Field(alias='student_count')
    
    class Config:
        from_attributes = True
        populate_by_name = True
        by_alias = False  # Serialize using field names (camelCase), not aliases (snake_case)

class AllSessionsStudentCountResponse(BaseModel):
    """Response with all sessions and their student counts for a status"""
    status: str
    totalStudents: int
    sessions: List[SessionStudentCount]

    class Config:
        from_attributes = True
