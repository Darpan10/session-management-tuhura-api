from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import logging
from typing import List, Optional

from models.session import Session as SessionModel
from models.session_staff import SessionStaff
from models.user.user import User
from schemas.session_schema import CreateSessionRequest, UpdateSessionRequest, SessionResponse

logger = logging.getLogger(__name__)


class SessionService:
    def __init__(self, db: Session):
        self.db = db

    def create_session(self, request: CreateSessionRequest, user_id: int) -> SessionModel:
        """Create a new session"""
        # Validate dates
        if request.endDate < request.startDate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End date must be after or equal to start date"
            )

        # Validate times (if same date)
        if request.startDate == request.endDate and request.endTime <= request.startTime:
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

        try:
            session = SessionModel(
                title=request.title,
                term=request.term,
                day_of_week=request.dayOfWeek,
                start_date=request.startDate,
                end_date=request.endDate,
                start_time=request.startTime,
                end_time=request.endTime,
                location=request.location,
                city=request.city,
                location_url=request.locationUrl,
                capacity=request.capacity,
                min_age=request.minAge,
                max_age=request.maxAge,
                created_by=user_id
            )

            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)

            # Assign staff members if provided
            if request.staffIds:
                self._assign_staff_to_session(session.id, request.staffIds)
                self.db.refresh(session)

            logger.info(f"Session created successfully: {session.id}")
            return session

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create session: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create session"
            )

    def get_all_sessions(self) -> List[SessionModel]:
        """Get all sessions"""
        try:
            sessions = self.db.query(SessionModel).order_by(SessionModel.start_date.desc()).all()
            return sessions
        except Exception as e:
            logger.error(f"Failed to fetch sessions: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch sessions"
            )

    def get_session_by_id(self, session_id: int) -> SessionModel:
        """Get a session by ID"""
        session = self.db.query(SessionModel).filter(SessionModel.id == session_id).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session with ID {session_id} not found"
            )
        
        return session

    def update_session(self, session_id: int, request: UpdateSessionRequest, user_id: int) -> SessionModel:
        """Update an existing session"""
        session = self.get_session_by_id(session_id)

        # Check if user is authorized to update (optional - you can add role checks here)
        # if session.created_by != user_id:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Not authorized to update this session"
        #     )

        try:
            # Update fields if provided
            if request.title is not None:
                session.title = request.title
            if request.term is not None:
                session.term = request.term
            if request.dayOfWeek is not None:
                session.day_of_week = request.dayOfWeek
            if request.startDate is not None:
                session.start_date = request.startDate
            if request.endDate is not None:
                session.end_date = request.endDate
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

            # Validate updated data
            if session.end_date < session.start_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="End date must be after or equal to start date"
                )

            if session.min_age >= session.max_age:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Maximum age must be greater than minimum age"
                )

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
        """Delete a session"""
        session = self.get_session_by_id(session_id)

        # Check if user is authorized to delete (optional)
        # if session.created_by != user_id:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Not authorized to delete this session"
        #     )

        try:
            self.db.delete(session)
            self.db.commit()
            logger.info(f"Session deleted successfully: {session_id}")

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete session: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete session"
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
            
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to assign staff to session: {e}")
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
