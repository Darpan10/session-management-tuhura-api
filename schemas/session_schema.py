from pydantic import BaseModel, Field
from datetime import date, time, datetime
from typing import Optional, List


class TermDetail(BaseModel):
    """Term with dates for session response"""
    id: int
    name: str
    startDate: date
    endDate: date
    year: int

    class Config:
        from_attributes = True


class StaffMember(BaseModel):
    """Simple staff member representation"""
    id: int
    userName: str
    email: str

    class Config:
        from_attributes = True


class CreateSessionRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    termIds: List[int] = Field(..., min_items=1, alias="termIds")
    dayOfWeek: str = Field(..., min_length=1, max_length=20, alias="dayOfWeek")
    startTime: time = Field(..., alias="startTime")
    endTime: time = Field(..., alias="endTime")
    location: str = Field(..., min_length=3, max_length=500)
    city: str = Field(..., min_length=2, max_length=200)
    locationUrl: Optional[str] = Field(None, alias="locationUrl", max_length=1000)
    capacity: int = Field(..., ge=1, le=200)
    minAge: int = Field(..., ge=0, le=100, alias="minAge")
    maxAge: int = Field(..., ge=0, le=100, alias="maxAge")
    staffIds: List[int] = Field(default=[], alias="staffIds")

    class Config:
        populate_by_name = True


class UpdateSessionRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    termIds: Optional[List[int]] = Field(None, min_items=1, alias="termIds")
    dayOfWeek: Optional[str] = Field(None, min_length=1, max_length=20, alias="dayOfWeek")
    startTime: Optional[time] = Field(None, alias="startTime")
    endTime: Optional[time] = Field(None, alias="endTime")
    location: Optional[str] = Field(None, min_length=3, max_length=500)
    city: Optional[str] = Field(None, min_length=2, max_length=200)
    locationUrl: Optional[str] = Field(None, alias="locationUrl", max_length=1000)
    capacity: Optional[int] = Field(None, ge=1, le=200)
    minAge: Optional[int] = Field(None, ge=0, le=100, alias="minAge")
    maxAge: Optional[int] = Field(None, ge=0, le=100, alias="maxAge")
    staffIds: Optional[List[int]] = Field(None, alias="staffIds")

    class Config:
        populate_by_name = True


class SessionResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    termIds: List[int] = []
    termNames: List[str] = []
    terms: List[TermDetail] = []  # Full term details with dates
    dayOfWeek: str
    startDate: date
    endDate: date
    startTime: time
    endTime: time
    location: str
    city: str
    locationUrl: Optional[str] = None
    capacity: int
    minAge: int
    maxAge: int
    rrule: str
    isDeleted: bool
    createdBy: int
    createdAt: datetime
    updatedAt: Optional[datetime] = None
    staff: List[StaffMember] = []

    class Config:
        from_attributes = True
        populate_by_name = True
        
        # This ensures proper serialization to camelCase
        json_schema_extra = {
            "example": {
                "isDeleted": False
            }
        }


class CreateSessionResponse(BaseModel):
    status: str
    message: str
    session: SessionResponse