from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from starlette import status

from dependencies.db_dependency import get_db
from schemas.user_schema import RegisterRequest, LoginRequest
from services.auth_service import AuthService
from utils.ical_utils import generate_ical

auth_router = APIRouter()


@auth_router.post("/register")
def register_user(request: RegisterRequest, db: Session = Depends(get_db)):
    # Instantiate the service with DB session
    auth_service = AuthService(db)

    # Call the service method to register the user
    result = auth_service.register_user(request)

    # Return the result (status, message, user_id)
    return result


@auth_router.post("/login")
def login_user(request: LoginRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    result = auth_service.login(request)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    return result


@auth_router.get("/download")
def download_calendar():
    ical_data = generate_ical()

    return Response(
        content=ical_data,
        media_type="text/calendar",
        headers={
            "Content-Disposition": "attachment; filename=poc_event.ics"
        },
    )