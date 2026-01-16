from sqlalchemy.orm import Session
from models.attendance import Attendance
from schemas.attendance_schema import AttendanceCreate, AttendanceUpdate
from datetime import date
from typing import List, Dict

class AttendanceService:
    @staticmethod
    def get_session_attendance(db: Session, session_id: int) -> List[Attendance]:
        """Get all attendance records for a session"""
        return db.query(Attendance).filter(Attendance.session_id == session_id).all()

    @staticmethod
    def get_student_attendance(db: Session, session_id: int, waitlist_id: int) -> List[Attendance]:
        """Get attendance records for a specific student in a session"""
        return db.query(Attendance).filter(
            Attendance.session_id == session_id,
            Attendance.waitlist_id == waitlist_id
        ).all()

    @staticmethod
    def mark_attendance(db: Session, attendance_data: AttendanceCreate) -> Attendance:
        """Mark or update attendance for a student on a specific date"""
        # Check if record already exists
        existing = db.query(Attendance).filter(
            Attendance.session_id == attendance_data.session_id,
            Attendance.waitlist_id == attendance_data.waitlist_id,
            Attendance.attendance_date == attendance_data.attendance_date
        ).first()

        if existing:
            existing.is_present = attendance_data.is_present
            db.commit()
            db.refresh(existing)
            return existing
        else:
            new_attendance = Attendance(**attendance_data.model_dump())
            db.add(new_attendance)
            db.commit()
            db.refresh(new_attendance)
            return new_attendance

    @staticmethod
    def bulk_update_attendance(db: Session, session_id: int, records: List[Dict]) -> List[Attendance]:
        """Bulk update attendance records"""
        results = []
        for record in records:
            attendance_data = AttendanceCreate(
                session_id=session_id,
                waitlist_id=record['waitlist_id'],
                attendance_date=date.fromisoformat(record['attendance_date']),
                is_present=record['is_present']
            )
            result = AttendanceService.mark_attendance(db, attendance_data)
            results.append(result)
        return results

    @staticmethod
    def delete_attendance(db: Session, attendance_id: int) -> bool:
        """Delete an attendance record"""
        attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
        if attendance:
            db.delete(attendance)
            db.commit()
            return True
        return False