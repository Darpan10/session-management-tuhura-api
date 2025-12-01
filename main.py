from fastapi import FastAPI
from sqlalchemy import event
from sqlalchemy.sql.ddl import CreateSchema
from starlette.middleware.cors import CORSMiddleware

from api.auth_controller import auth_router
from config import settings
from core.db_connect import Base, engine
import logging

from models.user import User,Role,UserRole
from services.mail_service import MailService

# Control logging with this one line:
logging.basicConfig(level=logging.DEBUG if settings.debug else logging.INFO)
app = FastAPI(title=settings.app_name, debug=settings.debug)

# Automatically create schema if it doesn't exist
event.listen(Base.metadata, "before_create", lambda target, connection, **kw: connection.execute(CreateSchema("user", if_not_exists=True)))


# Create tables
Base.metadata.create_all(bind=engine)


#FastAPI CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#Test Mailgun
# MailService.send_email("Test from FastAPI", "Mailgun test message")


# Include auth router with prefix
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])