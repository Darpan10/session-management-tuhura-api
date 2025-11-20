from sqlalchemy.orm import Session
from core.db_connect import SessionLocal

def get_db():
    """
    Dependency to get a database session.
    Use with FastAPI's Depends in your route functions.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
