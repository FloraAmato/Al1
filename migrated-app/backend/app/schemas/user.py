"""User schemas."""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, UUID4, ConfigDict


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    username: str
    name: Optional[str] = None
    surname: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema."""
    password: str


class UserUpdate(BaseModel):
    """User update schema."""
    name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[EmailStr] = None


class UserInDB(UserBase):
    """User database schema."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    is_active: bool
    is_email_verified: bool
    created_at: datetime
    updated_at: datetime


class User(UserInDB):
    """User response schema."""
    roles: List["Role"] = []


class RoleBase(BaseModel):
    """Base role schema."""
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    """Role creation schema."""
    pass


class Role(RoleBase):
    """Role response schema."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    created_at: datetime


class PasswordResetRequest(BaseModel):
    """Password reset request schema."""
    email: EmailStr


class PasswordReset(BaseModel):
    """Password reset schema."""
    token: str
    new_password: str


class EmailVerification(BaseModel):
    """Email verification schema."""
    token: str
