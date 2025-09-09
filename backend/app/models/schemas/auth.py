"""
Authentication schemas
"""

from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data"""
    email: Optional[str] = None


class UserCreate(BaseModel):
    """User registration schema"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str = Field(..., min_length=1, max_length=100)
    company_name: Optional[str] = Field(None, max_length=100)


class UserResponse(BaseModel):
    """User response schema"""
    id: str
    email: EmailStr
    full_name: str
    company_name: Optional[str] = None
    is_active: bool = True
    
    class Config:
        from_attributes = True