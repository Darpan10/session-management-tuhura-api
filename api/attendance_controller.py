from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies.db_dependency import get_db
from services.attendance_service import AttendanceService
from schemas.attendance_schema import (
    AttendanceCreate,
    AttendanceResponse,
    BulkAttendanceUpdate,
    BulkAttendanceSaveAll
)
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/attendance", tags=["Attendance"])

@router.get("/session/{session_id}", response_model=List[AttendanceResponse])
def get_session_attendance(session_id: int, db: Session = Depends(get_db)):
    """Get all attendance records for a session"""
    try:
        attendance = AttendanceService.get_session_attendance(db, session_id)
        return attendance
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}/student/{waitlist_id}", response_model=List[AttendanceResponse])
def get_student_attendance(session_id: int, waitlist_id: int, db: Session = Depends(get_db)):
    """Get attendance records for a specific student in a session"""
    try:
        attendance = AttendanceService.get_student_attendance(db, session_id, waitlist_id)
        return attendance
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mark", response_model=AttendanceResponse)
def mark_attendance(attendance: AttendanceCreate, db: Session = Depends(get_db)):
    """Mark or update attendance for a student on a specific date"""
    try:
        result = AttendanceService.mark_attendance(db, attendance)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}/date/{attendance_date}")
def get_attendance_for_date(session_id: int, attendance_date: str, db: Session = Depends(get_db)):
    """Get attendance status for all students on a specific date"""
    try:
        from datetime import date
        parsed_date = date.fromisoformat(attendance_date)
        attendance_list = AttendanceService.get_attendance_for_date(db, session_id, parsed_date)
        return attendance_list
    except Exception as e:
        logger.error(f"Get attendance error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bulk-update")
def bulk_update_attendance(bulk_data: BulkAttendanceUpdate, db: Session = Depends(get_db)):
    """Bulk update attendance - saves all student records (present and absent)"""
    try:
        logger.info(f"Bulk update request - Session ID: {bulk_data.session_id}, Date: {bulk_data.attendance_date}, Records: {len(bulk_data.attendance_records)}")
        
        # Convert Pydantic models to dicts for the service
        attendance_dicts = [record.model_dump() for record in bulk_data.attendance_records]
        
        result = AttendanceService.bulk_update_attendance(
            db, 
            bulk_data.session_id,
            bulk_data.attendance_date,
            attendance_dicts
        )
        logger.info(f"Successfully updated attendance")
        return result
    except Exception as e:
        logger.error(f"Bulk update error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bulk-save-all")
def bulk_save_all_attendance(bulk_data: BulkAttendanceSaveAll, db: Session = Depends(get_db)):
    """OPTIMIZED: Bulk save ALL attendance for all dates in ONE call - much faster!"""
    try:
        logger.info(f"Bulk save all request - Session ID: {bulk_data.session_id}, Total records: {len(bulk_data.attendance_records)}")
        
        # Convert Pydantic models to dicts for the service
        attendance_dicts = [record.model_dump() for record in bulk_data.attendance_records]
        
        result = AttendanceService.bulk_save_all_attendance(
            db,
            bulk_data.session_id,
            attendance_dicts
        )
        logger.info(f"Successfully saved all attendance")
        return result
    except Exception as e:
        logger.error(f"Bulk save all error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{attendance_id}")
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
