from sqlalchemy.orm import Session
from sqlalchemy import and_
from models.attendance import Attendance
from models.waitlist import Waitlist
from schemas.attendance_schema import AttendanceCreate, AttendanceUpdate, StudentAttendanceStatus
from datetime import date
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class AttendanceService:
    @staticmethod
    def get_session_attendance(db: Session, session_id: int) -> List[Attendance]:
        """Get all attendance records for a session"""
        return db.query(Attendance).filter(Attendance.session_id == session_id).all()

    @staticmethod
    def get_attendance_for_date(db: Session, session_id: int, attendance_date: date) -> List[StudentAttendanceStatus]:
        """Get attendance status for all admitted students on a specific date.
        Returns all students with is_present flag from database records."""
        
        from datetime import date as date_type
        today = date_type.today()
        
        # Get all admitted students for this session
        admitted_students = db.query(Waitlist).filter(
            and_(
                Waitlist.session_id == session_id,
                Waitlist.status == 'admitted'
            )
        ).all()
        
        # Get attendance records for this date
        attendance_records = db.query(Attendance).filter(
            and_(
                Attendance.session_id == session_id,
                Attendance.attendance_date == attendance_date
            )
        ).all()
        
        # Create a map of waitlist_id to is_present status
        attendance_map = {record.waitlist_id: record.is_present for record in attendance_records}
        
        # Build response with derived attendance status
        result = []
        for student in admitted_students:
            # Check if attendance record exists
            if student.id in attendance_map:
                is_present = attendance_map[student.id]
            else:
                # No record - only mark present if admitted before date and date has occurred
                admission_date = student.created_at.date() if student.created_at else attendance_date
                was_admitted = admission_date <= attendance_date
                has_occurred = attendance_date <= today
                is_present = was_admitted and has_occurred
            
            result.append(StudentAttendanceStatus(
                waitlist_id=student.id,
                student_name=student.student_name,
                student_email=student.student_email,
                is_present=is_present
            ))
        
        return result

    @staticmethod
    def get_student_attendance(db: Session, session_id: int, waitlist_id: int) -> List[Attendance]:
        """Get absence records for a specific student in a session"""
        return db.query(Attendance).filter(
            Attendance.session_id == session_id,
            Attendance.waitlist_id == waitlist_id
        ).all()

    @staticmethod
    def mark_attendance(db: Session, attendance_data: AttendanceCreate) -> Attendance:
        """Mark a student as absent on a specific date"""
        # Check if absence record already exists
        existing = db.query(Attendance).filter(
            Attendance.session_id == attendance_data.session_id,
            Attendance.waitlist_id == attendance_data.waitlist_id,
            Attendance.attendance_date == attendance_data.attendance_date
        ).first()

        if existing:
            # Already marked as absent
            return existing
        else:
            new_attendance = Attendance(**attendance_data.model_dump())
            db.add(new_attendance)
            db.commit()
            db.refresh(new_attendance)
            return new_attendance

    @staticmethod
    def bulk_update_attendance(db: Session, session_id: int, attendance_date_str: str, attendance_records: List[dict]) -> Dict:
        """Bulk update attendance - saves all student records (present and absent) efficiently.
        Uses upsert pattern: delete existing records for the date, then bulk insert new ones."""
        try:
            # Parse date
            attendance_date = date.fromisoformat(attendance_date_str)
            
            logger.info(f"Bulk update - Session: {session_id}, Date: {attendance_date}, Records: {len(attendance_records)}")
            
            # Delete existing attendance records for this date
            db.query(Attendance).filter(
                and_(
                    Attendance.session_id == session_id,
                    Attendance.attendance_date == attendance_date
                )
            ).delete(synchronize_session=False)
            
            # Bulk insert all new attendance records
            if attendance_records:
                attendance_objects = [
                    Attendance(
                        session_id=session_id,
                        waitlist_id=record['waitlist_id'],
                        attendance_date=attendance_date,
                        is_present=record['is_present']
                    )
                    for record in attendance_records
                ]
                db.bulk_save_objects(attendance_objects)
            
            db.commit()
            logger.info(f"Successfully saved {len(attendance_records)} attendance records")
            
            return {
                "success": True,
                "record_count": len(attendance_records),
                "date": attendance_date_str
            }
        except Exception as e:
            db.rollback()
            logger.error(f"Error in bulk update: {str(e)}", exc_info=True)
            raise Exception(f"Error in bulk update: {str(e)}")

    @staticmethod
    def bulk_save_all_attendance(db: Session, session_id: int, all_records: List[dict]) -> Dict:
        """OPTIMIZED: Bulk save ALL attendance records for all dates in ONE transaction.
        Much faster than saving date-by-date. Uses efficient delete + bulk insert."""
        try:
            logger.info(f"Bulk save all - Session: {session_id}, Total records: {len(all_records)}")
            
            # Group records by date for deletion
            dates_to_clear = set()
            records_by_date = {}
            
            for record in all_records:
                attendance_date = date.fromisoformat(record['attendance_date'])
                dates_to_clear.add(attendance_date)
                
                if attendance_date not in records_by_date:
                    records_by_date[attendance_date] = []
                records_by_date[attendance_date].append(record)
            
            # Delete all existing records for these dates in one query
            if dates_to_clear:
                db.query(Attendance).filter(
                    and_(
                        Attendance.session_id == session_id,
                        Attendance.attendance_date.in_(dates_to_clear)
                    )
                ).delete(synchronize_session=False)
            
            # Bulk insert all records at once using executemany (fastest method)
            if all_records:
                from sqlalchemy import insert
                stmt = insert(Attendance).values([
                    {
                        'session_id': session_id,
                        'waitlist_id': record['waitlist_id'],
                        'attendance_date': date.fromisoformat(record['attendance_date']),
                        'is_present': record['is_present']
                    }
                    for record in all_records
                ])
                db.execute(stmt)
            
            db.commit()
            logger.info(f"Successfully saved {len(all_records)} attendance records across {len(dates_to_clear)} dates")
            
            return {
                "success": True,
                "total_records": len(all_records),
                "dates_updated": len(dates_to_clear),
                "message": f"Saved {len(all_records)} records across {len(dates_to_clear)} dates"
            }
        except Exception as e:
            db.rollback()
            logger.error(f"Error in bulk save all: {str(e)}", exc_info=True)
            raise Exception(f"Error in bulk save all: {str(e)}")

    @staticmethod
    def delete_attendance(db: Session, attendance_id: int) -> bool:
        """Delete an attendance record"""
        attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
        if attendance:
            db.delete(attendance)
            db.commit()
            return True
        return False
