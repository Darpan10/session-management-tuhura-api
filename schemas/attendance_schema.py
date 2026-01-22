from pydantic import BaseModel
from datetime import date
from typing import Optional, List

class AttendanceBase(BaseModel):
    session_id: int
    waitlist_id: int
    attendance_date: date
    is_present: bool  # True = Present, False = Absent

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceUpdate(BaseModel):
    is_present: Optional[bool] = None

class AttendanceResponse(AttendanceBase):
    id: int

    class Config:
        from_attributes = True

class AttendanceRecord(BaseModel):
    """Single attendance record for bulk update"""
    waitlist_id: int
    is_present: bool

class AttendanceRecordWithDate(BaseModel):
    """Single attendance record with date for bulk save all"""
    attendance_date: str
    waitlist_id: int
    is_present: bool

class BulkAttendanceUpdate(BaseModel):
    session_id: int
    attendance_date: str
    attendance_records: List[AttendanceRecord]  # All student records (present and absent)

class BulkAttendanceSaveAll(BaseModel):
    """Optimized: Save all dates and students in one call"""
    session_id: int
    attendance_records: List[AttendanceRecordWithDate]  # All records with dates

class StudentAttendanceStatus(BaseModel):
    waitlist_id: int
    student_name: str
    student_email: str
    is_present: bool
