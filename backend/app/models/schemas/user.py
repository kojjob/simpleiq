"""
User model schemas
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    full_name: str
    company_name: str | None = None


class User(UserBase):
    """User model"""
    id: str
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime
    updated_at: datetime | None = None
    
    class Config:
        from_attributes = True


class UserInDB(User):
    """User in database with hashed password"""
    hashed_password: str