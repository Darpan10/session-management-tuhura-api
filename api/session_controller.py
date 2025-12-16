from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from dependencies.db_dependency import get_db
from schemas.session_schema import (
    CreateSessionRequest,
    UpdateSessionRequest,
    SessionResponse,
    CreateSessionResponse,
    StaffMember
)
from services.session_service import SessionService
from utils.jwt_utils import get_current_user

session_router = APIRouter()


def _build_session_response(session) -> SessionResponse:
    """Helper to build SessionResponse with staff members"""
    return SessionResponse(
        id=session.id,
        title=session.title,
        term=session.term,
        dayOfWeek=session.day_of_week,
        startDate=session.start_date,
        endDate=session.end_date,
        startTime=session.start_time,
        endTime=session.end_time,
        location=session.location,
        city=session.city,
        locationUrl=session.location_url,
        capacity=session.capacity,
        minAge=session.min_age,
        maxAge=session.max_age,
        createdBy=session.created_by,
        createdAt=session.created_at,
        updatedAt=session.updated_at,
        staff=[
            StaffMember(
                id=staff.id,
                userName=staff.user_name,
                email=staff.email
            )
            for staff in session.staff_members
        ]
    )


@session_router.get("/staff", response_model=List[StaffMember])
def get_staff_members(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all staff members who can be assigned to sessions"""
    session_service = SessionService(db)
    staff = session_service.get_all_staff()
    
    return [
        StaffMember(
            id=user.id,
            userName=user.user_name,
            email=user.email
        )
        for user in staff
    ]


@session_router.post("", response_model=CreateSessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(
    request: CreateSessionRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new session"""
    session_service = SessionService(db)
    user_id = int(current_user["sub"])
    
    session = session_service.create_session(request, user_id)
    
    return CreateSessionResponse(
        status="success",
        message="Session created successfully",
        session=_build_session_response(session)
    )


@session_router.get("", response_model=List[SessionResponse])
def get_all_sessions(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all sessions"""
    session_service = SessionService(db)
    sessions = session_service.get_all_sessions()
    
    return [_build_session_response(session) for session in sessions]


@session_router.get("/{session_id}", response_model=SessionResponse)
def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a session by ID"""
    session_service = SessionService(db)
    session = session_service.get_session_by_id(session_id)
    
    return _build_session_response(session)


@session_router.put("/{session_id}", response_model=SessionResponse)
def update_session(
    session_id: int,
    request: UpdateSessionRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a session"""
    session_service = SessionService(db)
    user_id = int(current_user["sub"])
    
    session = session_service.update_session(session_id, request, user_id)
    
    return _build_session_response(session)


@session_router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a session"""
    session_service = SessionService(db)
    user_id = int(current_user["sub"])
    
    session_service.delete_session(session_id, user_id)
    return None
