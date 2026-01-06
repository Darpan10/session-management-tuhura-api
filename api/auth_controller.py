from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from pydantic import BaseModel

from dependencies.db_dependency import get_db
from schemas.user_schema import RegisterRequest, LoginRequest
from services.auth_service import AuthService
from utils.jwt_utils import get_current_user

auth_router = APIRouter()


# Pydantic model for password change request
class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


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


@auth_router.post("/change-password")
def change_password(
    request: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change password for authenticated user."""
    auth_service = AuthService(db)
    user_id = current_user["user_id"]
    
    result = auth_service.change_password(
        user_id=user_id,
        current_password=request.current_password,
        new_password=request.new_password
    )
    
    return result
