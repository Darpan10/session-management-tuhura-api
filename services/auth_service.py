from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import bcrypt
import logging  # Add this import

from models.user import User
from models.user import Role
from schemas.user_schema import RegisterRequest, LoginRequest
from utils.jwt_utils import create_access_token, create_refresh_token

# Create logger instance
logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    # PASSWORD HASHING
    def get_password_hash(self, password: str) -> str:
        """Hash password using bcrypt."""
        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode("utf-8")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify plain password against hashed password."""
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                hashed_password.encode("utf-8")
            )
        except Exception as e:
            logger.debug("Password verification failed: %s", e)
            return False

    # REGISTRATION
    def register_user(self, request: RegisterRequest):
        # Check for duplicate email
        existing_user = (
            self.db.query(User).filter((User.email == request.email) |
                                       (User.user_name == request.username)).first()
        )
        if existing_user:
            logger.warning("Registration attempt with existing email: %s", request.email)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create user
        hashed_password = self.get_password_hash(request.password)
        user = User(
            email=request.email,
            hashed_password=hashed_password,
            user_name=request.username
        )

        # Assign default role "STAFF" (id = 1)
        staff_role = self.db.query(Role).filter(Role.id == 1).first()
        if not staff_role:
            logger.error("Default role (ID: 1) not found in database")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="System configuration error"
            )

        user.roles.append(staff_role)

        # Save new user
        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            logger.info("User registered successfully: %s", request.email)
        except Exception as e:
            self.db.rollback()
            logger.error("Failed to register user %s: %s", request.email, e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration failed"
            )

        return {
            "status": "success",
            "message": "User registered successfully"
        }

    # LOGIN WITH JWT
    def login(self, request: LoginRequest):
        user = self.authenticate_user(request)
        if not user:
            logger.warning("Failed login attempt for email: %s", request.email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})

        logger.info("User logged in successfully: %s", user.email)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "roles": [role.name for role in user.roles]
            }
        }

    # AUTHENTICATION
    def authenticate_user(self, request: LoginRequest):
        user = self.db.query(User).filter(User.email == request.email).first()
        if not user:
            logger.debug("User not found with email: %s", request.email)
            return None
        if not self.verify_password(request.password, user.hashed_password):
            logger.debug("Password verification failed for user: %s", request.email)
            return None

        logger.debug("User authenticated successfully: %s", request.email)
        return user

    # CHANGE PASSWORD
    def change_password(self, user_id: int, current_password: str, new_password: str):
        """Change user password after verifying current password."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning("Password change attempt for non-existent user ID: %s", user_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Verify current password
        if not self.verify_password(current_password, user.hashed_password):
            logger.warning("Failed password change attempt for user %s: incorrect current password", user.email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect"
            )

        # Check if new password is the same as current
        if self.verify_password(new_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be different from current password"
            )

        # Hash new password and update
        user.hashed_password = self.get_password_hash(new_password)
        
        try:
            self.db.commit()
            logger.info("Password changed successfully for user: %s", user.email)
        except Exception as e:
            self.db.rollback()
            logger.error("Failed to change password for user %s: %s", user.email, e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to change password"
            )

        return {
            "status": "success",
            "message": "Password changed successfully"
        }
