from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    email: str = Field(..., description="User email")
    password: str = Field(..., min_length=6, description="User password")


class RegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    email: str = Field(..., description="User email")
    password: str = Field(..., min_length=6, description="User password")
    role: str = Field(default="sales_rep", description="User role")


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: str
