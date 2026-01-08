from fastapi import FastAPI
from sqlalchemy import event
from sqlalchemy.sql.ddl import CreateSchema
from starlette.middleware.cors import CORSMiddleware
import psycopg2
from dotenv import load_dotenv
import os

from api.auth_controller import auth_router
from api.calendar_controller import calendar_router
from api.session_controller import session_router
from api.waitlist_controller import waitlist_router
from config import settings
from core.db_connect import Base, engine
import logging

from models.user import User,Role,UserRole
from models.session import Session
from models.student import Student
from models.waitlist import Waitlist
from services.mail_service import MailService

# Control logging with this one line:
logging.basicConfig(level=logging.DEBUG if settings.debug else logging.INFO)
app = FastAPI(title=settings.app_name, debug=settings.debug)

# Test database connection on startup
@app.on_event("startup")
async def startup_event():
    """Test Supabase database connection on startup"""
    try:
        connection = psycopg2.connect(
            user=settings.db_user,
            password=settings.db_password,
            host=settings.db_host,
            port=settings.db_port,
            dbname=settings.db_name
        )
        cursor = connection.cursor()
        cursor.execute("SELECT NOW();")
        result = cursor.fetchone()
        logging.info(f"✓ Supabase database connection successful! Server time: {result[0]}")
        cursor.close()
        connection.close()
    except Exception as e:
        logging.error(f"✗ Failed to connect to Supabase database: {e}")

# Automatically create schemas if they don't exist
event.listen(Base.metadata, "before_create", lambda target, connection, **kw: connection.execute(CreateSchema("user", if_not_exists=True)))
# event.listen(Base.metadata, "before_create", lambda target, connection, **kw: connection.execute(CreateSchema("session", if_not_exists=True)))
# event.listen(Base.metadata, "before_create", lambda target, connection, **kw: connection.execute(CreateSchema("student", if_not_exists=True)))
# event.listen(Base.metadata, "before_create", lambda target, connection, **kw: connection.execute(CreateSchema("student", if_not_exists=True)))
#

# Create tables - wrap in try/except to handle permission issues if tables already exist
try:
    Base.metadata.create_all(bind=engine, checkfirst=True)
    logging.info("✓ Database tables verified/created successfully")
except Exception as e:
    # Tables likely already exist but user lacks CREATE permission - this is okay
    logging.warning(f"Could not create tables (likely already exist): {e}")
    logging.info("Continuing - tables should already exist in database")


#FastAPI CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","http://localhost:3001", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#Test Mailgun
# MailService.send_email("Test from FastAPI", "Mailgun test message")


# Include auth router with prefix
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(session_router, prefix="/api/sessions", tags=["sessions"])
app.include_router(calendar_router, prefix="/api/calendar", tags=["calendar"])
app.include_router(waitlist_router, prefix="/api/waitlist", tags=["waitlist"])