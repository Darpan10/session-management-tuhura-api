from fastapi import FastAPI
from sqlalchemy import event
from sqlalchemy.sql.ddl import CreateSchema
from starlette.middleware.cors import CORSMiddleware
import psycopg2
from dotenv import load_dotenv
import os

from api.auth_controller import auth_router
from api.session_controller import session_router
from config import settings
from core.db_connect import Base, engine
import logging

from models.user import User,Role,UserRole
from models.session import Session
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

# Automatically create schema if it doesn't exist
event.listen(Base.metadata, "before_create", lambda target, connection, **kw: connection.execute(CreateSchema("auth", if_not_exists=True)))


# Create tables
Base.metadata.create_all(bind=engine)


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