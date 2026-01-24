from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from app.core.rbac import Role


class UserBase(BaseModel):
    email: EmailStr
    role: Role = Role.CUSTOMER


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    role: Role | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    id: int
    email: str
    role: Role
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenRefresh(BaseModel):
    refresh_token: str
