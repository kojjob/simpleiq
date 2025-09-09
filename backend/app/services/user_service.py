"""
User service for handling user operations
"""

from typing import Optional
from uuid import uuid4

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schemas.auth import UserCreate
from app.models.schemas.user import User, UserInDB


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory user storage (for development only)
USERS_DB = {}


class UserService:
    """Service for user-related operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    async def create_user(self, user_create: UserCreate) -> User:
        """Create a new user"""
        from datetime import datetime
        
        # Check if user already exists
        if user_create.email in USERS_DB:
            raise ValueError("User with this email already exists")
        
        user_id = str(uuid4())
        hashed_password = self.get_password_hash(user_create.password)
        
        # Store user in memory with password
        user_in_db = UserInDB(
            id=user_id,
            email=user_create.email,
            full_name=user_create.full_name,
            company_name=user_create.company_name,
            is_active=True,
            is_superuser=False,
            created_at=datetime.utcnow(),
            updated_at=None,
            hashed_password=hashed_password
        )
        
        USERS_DB[user_create.email] = user_in_db
        
        # Return user without password
        user = User(
            id=user_id,
            email=user_create.email,
            full_name=user_create.full_name,
            company_name=user_create.company_name,
            is_active=True,
            is_superuser=False,
            created_at=datetime.utcnow(),
            updated_at=None
        )
        
        return user
    
    async def get_by_email(self, email: str) -> Optional[UserInDB]:
        """Get user by email"""
        # Return user from in-memory storage
        return USERS_DB.get(email)
    
    async def authenticate(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user"""
        user_in_db = await self.get_by_email(email)
        if not user_in_db:
            return None
        if not self.verify_password(password, user_in_db.hashed_password):
            return None
        
        # Return User without password
        return User(
            id=user_in_db.id,
            email=user_in_db.email,
            full_name=user_in_db.full_name,
            company_name=user_in_db.company_name,
            is_active=user_in_db.is_active,
            is_superuser=user_in_db.is_superuser,
            created_at=user_in_db.created_at,
            updated_at=user_in_db.updated_at
        )