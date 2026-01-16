from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies.db_dependency import get_db
from services.attendance_service import AttendanceService
from schemas.attendance_schema import (
    AttendanceCreate,
    AttendanceResponse,
    BulkAttendanceUpdate
)
from typing import List

attendance_router = APIRouter()


@attendance_router.get("/session/{session_id}", response_model=List[AttendanceResponse])
def get_session_attendance(session_id: int, db: Session = Depends(get_db)):
    """Get all attendance records for a session"""
    try:
        attendance = AttendanceService.get_session_attendance(db, session_id)
        return attendance
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@attendance_router.get("/session/{session_id}/student/{waitlist_id}", response_model=List[AttendanceResponse])
def get_student_attendance(session_id: int, waitlist_id: int, db: Session = Depends(get_db)):
    """Get attendance records for a specific student in a session"""
    try:
        attendance = AttendanceService.get_student_attendance(db, session_id, waitlist_id)
        return attendance
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@attendance_router.post("/mark", response_model=AttendanceResponse)
def mark_attendance(attendance: AttendanceCreate, db: Session = Depends(get_db)):
    """Mark or update attendance for a student on a specific date"""
    try:
        result = AttendanceService.mark_attendance(db, attendance)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@attendance_router.post("/bulk-update", response_model=List[AttendanceResponse])
def bulk_update_attendance(bulk_data: BulkAttendanceUpdate, db: Session = Depends(get_db)):
    """Bulk update attendance records"""
    try:
        results = AttendanceService.bulk_update_attendance(
            db,
            bulk_data.session_id,
            bulk_data.records
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@attendance_router.delete("/{attendance_id}")
def delete_attendance(attendance_id: int, db: Session = Depends(get_db)):
    """Delete an attendance record"""
    try:
        success = AttendanceService.delete_attendance(db, attendance_id)
        if not success:
            raise HTTPException(status_code=404, detail="Attendance record not found")
        return {"message": "Attendance record deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))