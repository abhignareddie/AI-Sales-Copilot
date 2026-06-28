from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, get_current_user
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, RefreshTokenRequest, ForgotPasswordRequest
from app.schemas.user import UserResponse
from app.schemas.common import MessageResponse
from app.services.auth_service import AuthService
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new user."""
    service = AuthService(db)
    return await service.register(data)


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login and receive JWT tokens."""
    service = AuthService(db)
    return await service.login(data)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Refresh an access token."""
    service = AuthService(db)
    return await service.refresh(data.refresh_token)


@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: User = Depends(get_current_user)):
    """Logout current user."""
    return MessageResponse(message="Successfully logged out")


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(data: ForgotPasswordRequest):
    """Send password reset email (mock)."""
    return MessageResponse(message="If the email exists, a reset link has been sent.")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user."""
    return current_user
