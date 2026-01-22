from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from dependencies.db_dependency import get_db
from schemas.term_schema import TermCreate, TermUpdate
from services.term_service import TermService
from utils.jwt_utils import get_current_user

term_router = APIRouter()


def _build_term_response(term):
    """Helper to build term response dict with camelCase keys"""
    return {
        "id": term.id,
        "name": term.name,
        "startDate": term.start_date.isoformat(),
        "endDate": term.end_date.isoformat(),
        "year": term.year,
        "createdAt": term.created_at.isoformat() if term.created_at else None,
        "updatedAt": term.updated_at.isoformat() if term.updated_at else None,
    }


@term_router.post("", status_code=201)
def create_term(
    request: TermCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new term (Admin only)"""
    term_service = TermService(db)
    term = term_service.create_term(request)
    return _build_term_response(term)


@term_router.get("")
def get_all_terms(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all terms"""
    term_service = TermService(db)
    terms = term_service.get_all_terms()
    return [_build_term_response(term) for term in terms]


@term_router.get("/{term_id}")
def get_term(
    term_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get term by ID"""
    term_service = TermService(db)
    term = term_service.get_term_by_id(term_id)
    return _build_term_response(term)


@term_router.put("/{term_id}")
def update_term(
    term_id: int,
    request: TermUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update term (Admin only)"""
    term_service = TermService(db)
    term = term_service.update_term(term_id, request)
    return _build_term_response(term)


@term_router.delete("/{term_id}")
def delete_term(
    term_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete term (Admin only)"""
    term_service = TermService(db)
    term_service.delete_term(term_id)
    return {"message": "Term deleted successfully"}
