from pydantic import BaseModel, Field
from datetime import date, time, datetime
from typing import Optional, List


class StaffMember(BaseModel):
    """Simple staff member representation"""
    id: int
    userName: str
    email: str

    class Config:
        from_attributes = True


class CreateSessionRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    term: str = Field(..., min_length=1, max_length=50)
    dayOfWeek: str = Field(..., min_length=1, max_length=20, alias="dayOfWeek")
    startDate: date = Field(..., alias="startDate")
    endDate: date = Field(..., alias="endDate")
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
    term: Optional[str] = Field(None, min_length=1, max_length=50)
    dayOfWeek: Optional[str] = Field(None, min_length=1, max_length=20, alias="dayOfWeek")
    startDate: Optional[date] = Field(None, alias="startDate")
    endDate: Optional[date] = Field(None, alias="endDate")
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
    term: str
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
    rrule: Optional[str] = None
    createdBy: int
    createdAt: datetime
    updatedAt: Optional[datetime] = None
    staff: List[StaffMember] = []

    class Config:
        from_attributes = True
        populate_by_name = True


class CreateSessionResponse(BaseModel):
    status: str
    message: str
    session: SessionResponse
