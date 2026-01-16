from pydantic import BaseModel
from datetime import date
from typing import Optional

class AttendanceBase(BaseModel):
    session_id: int
    waitlist_id: int
    attendance_date: date
    is_present: bool

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceUpdate(BaseModel):
    is_present: bool

class AttendanceResponse(AttendanceBase):
    id: int

    class Config:
        from_attributes = True

class BulkAttendanceUpdate(BaseModel):
    session_id: int
    records: list[dict]  # [{waitlist_id, attendance_date, is_present}]