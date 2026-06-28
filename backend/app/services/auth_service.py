from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.services.audit_service import AuditService
from app.models.user import User


class AuthService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)
        self.audit_service = AuditService(db)

    async def register(self, data: RegisterRequest) -> User:
        existing = await self.user_repo.get_by_email(data.email)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        user = await self.user_repo.create({
            "full_name": data.full_name, "email": data.email,
            "password_hash": hash_password(data.password), "role": data.role,
        })
        await self.audit_service.log("register", "user", user.id, user.id)
        return user

    async def login(self, data: LoginRequest) -> TokenResponse:
        user = await self.user_repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
        access_token = create_access_token({"sub": str(user.id), "role": user.role})
        refresh_token = create_refresh_token({"sub": str(user.id), "role": user.role})
        await self.audit_service.log("login", "user", user.id, user.id)
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    async def refresh(self, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        user_id = payload.get("sub")
        user = await self.user_repo.get_by_id(int(user_id))
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        new_access = create_access_token({"sub": str(user.id), "role": user.role})
        new_refresh = create_refresh_token({"sub": str(user.id), "role": user.role})
        return TokenResponse(access_token=new_access, refresh_token=new_refresh)
