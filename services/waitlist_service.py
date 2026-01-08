from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import logging
from typing import List

from models.student import Student
from models.waitlist import Waitlist, WaitlistStatus
from models.session import Session as SessionModel
from schemas.waitlist_schema import StudentSignupRequest, WaitlistEntryWithDetails, StudentResponse, \
    StudentUpdateRequest

logger = logging.getLogger(__name__)


class WaitlistService:
    def __init__(self, db: Session):
        self.db = db

    def create_signup(self, request: StudentSignupRequest) -> Waitlist:
        """Create a new student signup and add to waitlist"""
        try:
            # Check if session exists
            session = self.db.query(SessionModel).filter(SessionModel.id == request.session_id).first()
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Session with ID {request.session_id} not found"
                )

            # Check if student already exists by email
            student = self.db.query(Student).filter(Student.email == request.email).first()

            if student:
                # Check if student is already on waitlist for this session
                existing_waitlist = self.db.query(Waitlist).filter(
                    Waitlist.student_id == student.id,
                    Waitlist.session_id == request.session_id
                ).first()

                if existing_waitlist:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Student is already registered for this session"
                    )

                # Update existing student details
                student.first_name = request.first_name
                student.family_name = request.family_name
                student.school_year = request.school_year
                student.school_year_other = request.school_year_other
                student.experience = request.experience
                student.needs_device = request.needs_device
                student.medical_info = request.medical_info
                student.parent_name = request.parent_name
                student.parent_phone = request.parent_phone
            else:
                # Create new student
                student = Student(
                    email=request.email,
                    first_name=request.first_name,
                    family_name=request.family_name,
                    school_year=request.school_year,
                    school_year_other=request.school_year_other,
                    experience=request.experience,
                    needs_device=request.needs_device,
                    medical_info=request.medical_info,
                    parent_name=request.parent_name,
                    parent_phone=request.parent_phone
                )
                self.db.add(student)
                self.db.flush()  # Get student.id

            # Create waitlist entry
            waitlist_entry = Waitlist(
                student_id=student.id,
                session_id=request.session_id,
                consent_share_details=request.consent_share_details,
                consent_photos=request.consent_photos,
                heard_from=request.heard_from,
                heard_from_other=request.heard_from_other,
                newsletter_subscribe=request.newsletter_subscribe,
                status=WaitlistStatus.WAITLIST
            )

            self.db.add(waitlist_entry)
            self.db.commit()
            self.db.refresh(waitlist_entry)

            logger.info(f"Student {student.email} added to waitlist for session {request.session_id}")
            return waitlist_entry

        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create signup: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create signup"
            )

    def get_waitlist_by_session(self, session_id: int) -> List[WaitlistEntryWithDetails]:
        """Get all waitlist entries for a specific session"""
        try:
            results = (
                self.db.query(
                    Waitlist.id,
                    Student.first_name,
                    Student.family_name,
                    Student.email,
                    Student.parent_name,
                    Student.parent_phone,
                    Student.school_year,
                    Student.needs_device,
                    Waitlist.status,
                    Waitlist.created_at
                )
                .join(Student, Waitlist.student_id == Student.id)
                .filter(Waitlist.session_id == session_id)
                .order_by(Waitlist.created_at.asc())
                .all()
            )

            return [
                WaitlistEntryWithDetails(
                    id=r.id,
                    student_name=f"{r.first_name} {r.family_name}",
                    student_email=r.email,
                    parent_name=r.parent_name,
                    parent_phone=r.parent_phone,
                    school_year=r.school_year,
                    needs_device=r.needs_device,
                    status=r.status,
                    created_at=r.created_at
                )
                for r in results
            ]
        except Exception as e:
            logger.error(f"Failed to fetch waitlist: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch waitlist"
            )

    def update_waitlist_status(self, waitlist_id: int, new_status: WaitlistStatus) -> Waitlist:
        """Update waitlist entry status"""
        try:
            waitlist_entry = self.db.query(Waitlist).filter(Waitlist.id == waitlist_id).first()

            if not waitlist_entry:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Waitlist entry with ID {waitlist_id} not found"
                )

            waitlist_entry.status = new_status
            self.db.commit()
            self.db.refresh(waitlist_entry)

            logger.info(f"Waitlist entry {waitlist_id} status updated to {new_status}")
            return waitlist_entry

        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update waitlist status: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update waitlist status"
            )

    def get_all_students(self) -> List[StudentResponse]:
        """Get all students"""
        try:
            students = self.db.query(Student).order_by(Student.created_at.desc()).all()
            return [StudentResponse.from_orm(student) for student in students]
        except Exception as e:
            logger.error(f"Failed to fetch students: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch students"
            )

    def get_student_by_id(self, student_id: int) -> StudentResponse:
        """Get a specific student by ID"""
        try:
            student = self.db.query(Student).filter(Student.id == student_id).first()
            if not student:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Student with ID {student_id} not found"
                )
            return StudentResponse.from_orm(student)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to fetch student: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch student"
            )

    def update_student(self, student_id: int, request: StudentUpdateRequest) -> StudentResponse:
        """Update student details"""
        try:
            student = self.db.query(Student).filter(Student.id == student_id).first()
            if not student:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Student with ID {student_id} not found"
                )

            # Update student fields
            student.first_name = request.first_name
            student.last_name = request.last_name
            student.date_of_birth = request.date_of_birth
            student.school_year = request.school_year
            student.school_name = request.school_name
            student.previous_experience = request.previous_experience
            student.heard_from = request.heard_from
            student.needs_device = request.needs_device
            student.parent_first_name = request.parent_first_name
            student.parent_last_name = request.parent_last_name
            student.parent_email = request.parent_email
            student.parent_phone = request.parent_phone
            student.emergency_contact_name = request.emergency_contact_name
            student.emergency_contact_phone = request.emergency_contact_phone
            student.medical_info = request.medical_info
            student.dietary_requirements = request.dietary_requirements
            student.consent_share_details = request.consent_share_details
            student.newsletter_subscribe = request.newsletter_subscribe

            self.db.commit()
            self.db.refresh(student)

            logger.info(f"Student {student_id} details updated")
            return StudentResponse.from_orm(student)

        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update student: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update student"
            )
