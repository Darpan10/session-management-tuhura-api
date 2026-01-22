from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import logging
from typing import List

from models.term import Term
from schemas.term_schema import TermCreate, TermUpdate

logger = logging.getLogger(__name__)


class TermService:
    def __init__(self, db: Session):
        self.db = db

    def create_term(self, request: TermCreate) -> Term:
        """Create a new term"""
        # Auto-calculate year from start_date
        year = request.start_date.year
        
        # Check if term with same name and year already exists
        existing = self.db.query(Term).filter(
            Term.name == request.name,
            Term.year == year
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Term {request.name} for year {year} already exists"
            )
        
        # Validate dates
        if request.end_date <= request.start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End date must be after start date"
            )
        
        term = Term(
            name=request.name,
            start_date=request.start_date,
            end_date=request.end_date,
            year=year
        )
        
        self.db.add(term)
        self.db.commit()
        self.db.refresh(term)
        
        logger.info(f"Created term: {term.name} ({term.year})")
        return term

    def get_all_terms(self) -> List[Term]:
        """Get all terms ordered by year and start date"""
        return self.db.query(Term).order_by(Term.year.desc(), Term.start_date).all()

    def get_term_by_id(self, term_id: int) -> Term:
        """Get term by ID"""
        term = self.db.query(Term).filter(Term.id == term_id).first()
        if not term:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Term with ID {term_id} not found"
            )
        return term

    def update_term(self, term_id: int, request: TermUpdate) -> Term:
        """Update term"""
        term = self.get_term_by_id(term_id)
        
        # Track if dates are being updated
        update_year = False
        
        if request.name is not None:
            term.name = request.name
        if request.start_date is not None:
            term.start_date = request.start_date
            update_year = True
        if request.end_date is not None:
            term.end_date = request.end_date
        
        # Auto-calculate year from start_date if dates were updated
        if update_year:
            term.year = term.start_date.year
        elif request.year is not None:
            term.year = request.year
        
        # Validate dates
        if term.end_date <= term.start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End date must be after start date"
            )
        
        # Mark as updated
        from datetime import datetime
        term.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(term)
        
        logger.info(f"Updated term: {term.name} ({term.year})")
        return term

    def delete_term(self, term_id: int) -> bool:
        """Delete term"""
        term = self.get_term_by_id(term_id)
        
        # Check if any sessions are using this term
        if term.sessions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete term {term.name} - it is being used by {len(term.sessions)} session(s)"
            )
        
        self.db.delete(term)
        self.db.commit()
        
        logger.info(f"Deleted term: {term.name} ({term.year})")
        return True
