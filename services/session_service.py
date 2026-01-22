from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import logging
from typing import List, Optional

from models.session import Session as SessionModel
from models.session_staff import SessionStaff
from models.term import Term
from models.user.user import User
from models.waitlist import Waitlist
from models.attendance import Attendance
from schemas.session_schema import CreateSessionRequest, UpdateSessionRequest, SessionResponse
from utils.rrule_util import generate_rrule

logger = logging.getLogger(__name__)


class SessionService:
    def __init__(self, db: Session):
        self.db = db

    # TODO: yet to send staff id from front end - session staff table not being populated

    def create_session(self, request: CreateSessionRequest, user_id: int) -> SessionModel:
        """Create a new session"""
        # Fetch the selected terms
        terms = self.db.query(Term).filter(Term.id.in_(request.termIds)).all()
        if len(terms) != len(request.termIds):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"One or more term IDs not found"
            )

        # Calculate combined date range from all selected terms
        start_date = min(term.start_date for term in terms)
        end_date = max(term.end_date for term in terms)

        # Validate times
        if request.endTime <= request.startTime:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End time must be after start time"
            )

        # Validate age range
        if request.minAge >= request.maxAge:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum age must be greater than minimum age"
            )
        
        # Generate rrule with combined date range
        rrule_str = generate_rrule(
            start_date=start_date,
            end_date=end_date,
            start_time=request.startTime,
            end_time=request.endTime,
            day_of_week=request.dayOfWeek
        )

        try:
            session = SessionModel(
                title=request.title,
                term=terms[0].name,  # Set first term name for backward compatibility
                description=request.description,
                term_id=terms[0].id,  # Set first term as primary for backward compatibility
                day_of_week=request.dayOfWeek,
                start_date=start_date,
                end_date=end_date,
                start_time=request.startTime,
                end_time=request.endTime,
                location=request.location,
                city=request.city,
                location_url=request.locationUrl,
                capacity=request.capacity,
                min_age=request.minAge,
                max_age=request.maxAge,
                rrule=rrule_str,
                created_by=user_id
            )

            self.db.add(session)
            self.db.flush()  # Get the session ID
            
            # Clear any existing term associations (in case of retry after failed attempt)
            from models.session_term import SessionTerm
            self.db.query(SessionTerm).filter(SessionTerm.session_id == session.id).delete()
            self.db.flush()  # Ensure delete is committed before inserts
            
            # Manually add term associations to avoid duplicate key errors
            for term in terms:
                session_term = SessionTerm(session_id=session.id, term_id=term.id)
                self.db.add(session_term)

            # Assign staff members if provided
            if request.staffIds:
                self._assign_staff_to_session(session.id, request.staffIds)

            self.db.commit()
            self.db.refresh(session)

            logger.info(f"Session created successfully: {session.id}")
            return session

        except HTTPException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create session: {e}", exc_info=True)
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Exception details: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create session: {str(e)}"
            )

    def get_all_sessions(self) -> List[SessionModel]:
        """Get all sessions (including archived ones - frontend will filter)"""
        from sqlalchemy.orm import joinedload
        
        try:
            sessions = self.db.query(SessionModel).options(
                joinedload(SessionModel.terms),
                joinedload(SessionModel.staff_members)
            ).order_by(
                SessionModel.start_date.desc()
            ).all()
            return sessions
        except Exception as e:
            logger.error(f"Failed to fetch sessions: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch sessions: {str(e)}"
            )

    def get_session_by_id(self, session_id: int) -> SessionModel:
        """Get a session by ID"""
        from sqlalchemy.orm import joinedload
        
        session = self.db.query(SessionModel).options(
            joinedload(SessionModel.terms),
            joinedload(SessionModel.staff_members)
        ).filter(SessionModel.id == session_id).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session with ID {session_id} not found"
            )
        
        return session

    def update_session(self, session_id: int, request: UpdateSessionRequest, user_id: int) -> SessionModel:
        """Update an existing session"""
        session = self.get_session_by_id(session_id)

        try:
            # If terms are being updated, fetch new terms and update dates
            if request.termIds is not None:
                from models.session_term import SessionTerm
                
                terms = self.db.query(Term).filter(Term.id.in_(request.termIds)).all()
                if len(terms) != len(request.termIds):
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"One or more term IDs not found"
                    )
                
                # Clear existing term associations
                self.db.query(SessionTerm).filter(SessionTerm.session_id == session_id).delete()
                self.db.flush()  # Ensure delete is committed before inserts
                
                # Manually add new term associations
                for term in terms:
                    session_term = SessionTerm(session_id=session_id, term_id=term.id)
                    self.db.add(session_term)
                
                # Update primary term for backward compatibility
                session.term = terms[0].name
                session.term_id = terms[0].id
                
                # Update date range
                session.start_date = min(term.start_date for term in terms)
                session.end_date = max(term.end_date for term in terms)

            # Update fields if provided
            if request.title is not None:
                session.title = request.title
            if request.description is not None:
                session.description = request.description
            if request.dayOfWeek is not None:
                session.day_of_week = request.dayOfWeek
            if request.startTime is not None:
                session.start_time = request.startTime
            if request.endTime is not None:
                session.end_time = request.endTime
            if request.location is not None:
                session.location = request.location
            if request.city is not None:
                session.city = request.city
            if request.locationUrl is not None:
                session.location_url = request.locationUrl
            if request.capacity is not None:
                session.capacity = request.capacity
            if request.minAge is not None:
                session.min_age = request.minAge
            if request.maxAge is not None:
                session.max_age = request.maxAge

            # Validate age range
            if session.min_age >= session.max_age:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Maximum age must be greater than minimum age"
                )

            # Validate times
            if session.end_time <= session.start_time:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="End time must be after start time"
                )

            # Regenerate rrule with updated values
            rrule_str = generate_rrule(
                start_date=session.start_date,
                end_date=session.end_date,
                start_time=session.start_time,
                end_time=session.end_time,
                day_of_week=session.day_of_week
            )
            session.rrule = rrule_str

            # Update staff assignments if provided
            if request.staffIds is not None:
                self._assign_staff_to_session(session.id, request.staffIds)

            self.db.commit()
            self.db.refresh(session)

            logger.info(f"Session updated successfully: {session.id}")
            return session

        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update session: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update session"
            )

    def delete_session(self, session_id: int, user_id: int) -> None:
        """Soft delete a session and withdraw all enrolled students"""
        session = self.get_session_by_id(session_id)

        # Check if user is authorized to delete (optional)
        # if session.created_by != user_id:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Not authorized to delete this session"
        #     )

        try:
            logger.info(f"Starting soft deletion of session {session_id}")
            
            # Withdraw all students who are admitted or on waitlist
            withdrawn_count = self.db.query(Waitlist).filter(
                Waitlist.session_id == session_id,
                Waitlist.status.in_(['admitted', 'waitlist'])
            ).update({'status': 'withdrawn'}, synchronize_session=False)
            logger.info(f"Withdrew {withdrawn_count} students from session {session_id}")
            
            # Mark session as deleted (soft delete)
            session.is_deleted = True
            
            self.db.commit()
            logger.info(f"Session {session_id} marked as deleted (soft delete)")

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete session {session_id}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete session: {str(e)}"
            )

    def _assign_staff_to_session(self, session_id: int, staff_ids: List[int]) -> None:
        """Assign staff members to a session"""
        try:
            # Remove existing staff assignments
            self.db.query(SessionStaff).filter(SessionStaff.session_id == session_id).delete()
            
            # Add new staff assignments
            for staff_id in staff_ids:
                session_staff = SessionStaff(session_id=session_id, staff_id=staff_id)
                self.db.add(session_staff)
            
            # Don't commit here - let the parent method handle it
        except Exception as e:
            logger.error(f"Failed to assign staff to session: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to assign staff members"
            )

    def get_all_staff(self) -> List[User]:
        """Get all users with STAFF role"""
        try:
            from models.user.role import Role
            from models.user.user_role import UserRole
            
            # Query users who have the STAFF role
            staff_users = (
                self.db.query(User)
                .join(UserRole, User.id == UserRole.user_id)
                .join(Role, UserRole.role_id == Role.id)
                .filter(Role.name == "STAFF")
                .all()
            )
            return staff_users
        except Exception as e:
            logger.error(f"Failed to fetch staff: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch staff members"
            )
