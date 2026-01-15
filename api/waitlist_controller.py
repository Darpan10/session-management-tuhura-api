from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from dependencies.db_dependency import get_db
from schemas.waitlist_schema import (
    StudentSignupRequest,
    WaitlistResponse,
    WaitlistEntryWithDetails,
    StudentResponse,
    StudentUpdateRequest,
    BulkStatusUpdateRequest,
    BulkStatusUpdateResponse
)
from services.waitlist_service import WaitlistService
from utils.jwt_utils import get_current_user
from models.waitlist import WaitlistStatus

waitlist_router = APIRouter()


@waitlist_router.post("/signup", response_model=WaitlistResponse, status_code=status.HTTP_201_CREATED)
def student_signup(
        request: StudentSignupRequest,
        db: Session = Depends(get_db)
):
    """Public endpoint for student signup (no authentication required)"""
    waitlist_service = WaitlistService(db)
    waitlist_entry = waitlist_service.create_signup(request)

    return WaitlistResponse(
        id=waitlist_entry.id,
        student_id=waitlist_entry.student_id,
        session_id=waitlist_entry.session_id,
        consent_share_details=waitlist_entry.consent_share_details,
        consent_photos=waitlist_entry.consent_photos,
        heard_from=waitlist_entry.heard_from,
        heard_from_other=waitlist_entry.heard_from_other,
        newsletter_subscribe=waitlist_entry.newsletter_subscribe,
        status=waitlist_entry.status,
        created_at=waitlist_entry.created_at
    )


@waitlist_router.get("/session/{session_id}", response_model=List[WaitlistEntryWithDetails])
def get_session_waitlist(
        session_id: int,
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    """Get all waitlist entries for a specific session (requires authentication)"""
    waitlist_service = WaitlistService(db)
    return waitlist_service.get_waitlist_by_session(session_id)


@waitlist_router.patch("/{waitlist_id}/status", response_model=WaitlistResponse)
def update_waitlist_status(
        waitlist_id: int,
        new_status: WaitlistStatus,
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    """Update waitlist entry status (requires authentication)"""
    waitlist_service = WaitlistService(db)
    waitlist_entry = waitlist_service.update_waitlist_status(waitlist_id, new_status)

    return WaitlistResponse(
        id=waitlist_entry.id,
        student_id=waitlist_entry.student_id,
        session_id=waitlist_entry.session_id,
        consent_share_details=waitlist_entry.consent_share_details,
        consent_photos=waitlist_entry.consent_photos,
        heard_from=waitlist_entry.heard_from,
        heard_from_other=waitlist_entry.heard_from_other,
        newsletter_subscribe=waitlist_entry.newsletter_subscribe,
        status=waitlist_entry.status,
        created_at=waitlist_entry.created_at
    )


@waitlist_router.get("/students", response_model=List[StudentResponse])
def get_all_students(
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    """Get all students who have signed up (requires authentication)"""
    waitlist_service = WaitlistService(db)
    return waitlist_service.get_all_students()


@waitlist_router.get("/students/{student_id}", response_model=StudentResponse)
def get_student_by_id(
        student_id: int,
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    """Get a specific student's details (requires authentication)"""
    waitlist_service = WaitlistService(db)
    student = waitlist_service.get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@waitlist_router.put("/students/{student_id}", response_model=StudentResponse)
def update_student(
        student_id: int,
        request: StudentUpdateRequest,
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    """Update student details (requires authentication)"""
    waitlist_service = WaitlistService(db)
    return waitlist_service.update_student(student_id, request)


@waitlist_router.post("/bulk-status", response_model=BulkStatusUpdateResponse)
def bulk_update_status(
        request: BulkStatusUpdateRequest,
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    """Update status for multiple waitlist entries (requires authentication)"""
    waitlist_service = WaitlistService(db)
    status_enum = WaitlistStatus(request.new_status)
    updated_count = waitlist_service.bulk_update_status(request.waitlist_ids, status_enum)
    
    return BulkStatusUpdateResponse(
        updated_count=updated_count,
        message=f"Successfully updated {updated_count} waitlist entries to {request.new_status}"
    )


@waitlist_router.get("/session/{session_id}/status/{status_value}", response_model=List[WaitlistEntryWithDetails])
def get_waitlist_by_status(
        session_id: int,
        status_value: str,
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    """Get waitlist entries for a specific session filtered by status (requires authentication)"""
    try:
        status_enum = WaitlistStatus(status_value)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status value. Must be one of: waitlist, admitted, withdrawn"
        )
    
    waitlist_service = WaitlistService(db)
    return waitlist_service.get_waitlist_by_status(session_id, status_enum)


@waitlist_router.get("/session/{session_id}/admitted-count")
def get_admitted_count(
        session_id: int,
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    """Get count of admitted students for a specific session (requires authentication)"""
    waitlist_service = WaitlistService(db)
    count = waitlist_service.get_admitted_count(session_id)
    return {"session_id": session_id, "admitted_count": count}


@waitlist_router.get("/{waitlist_id}", response_model=WaitlistEntryWithDetails)
def get_waitlist_entry(
        waitlist_id: int,
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    """Get detailed information for a specific waitlist entry (requires authentication)"""
    waitlist_service = WaitlistService(db)
    entry = waitlist_service.get_waitlist_entry_by_id(waitlist_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Waitlist entry not found")
    return entry

