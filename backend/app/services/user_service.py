"""
User service for handling user operations
"""


from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schemas.auth import UserCreate
from app.models.schemas.user import User as UserSchema
from app.models.user import User as UserModel

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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
    
    async def create_user(self, user_create: UserCreate) -> UserSchema:
        """Create a new user"""
        # Check if user already exists
        existing_user = await self.get_by_email(user_create.email)
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Create new user in database
        hashed_password = self.get_password_hash(user_create.password)
        
        db_user = UserModel(
            email=user_create.email,
            hashed_password=hashed_password,
            full_name=user_create.full_name,
            company_name=user_create.company_name,
            is_active=True,
            is_superuser=False
        )
        
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        
        # Return user schema without password
        return UserSchema(
            id=str(db_user.id),
            email=db_user.email,
            full_name=db_user.full_name,
            company_name=db_user.company_name,
            is_active=db_user.is_active,
            is_superuser=db_user.is_superuser,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at
        )
    
    async def get_by_email(self, email: str) -> UserModel | None:
        """Get user by email from database"""
        result = await self.db.execute(
            select(UserModel).where(UserModel.email == email)
        )
        return result.scalar_one_or_none()
    
    async def authenticate(self, email: str, password: str) -> UserSchema | None:
        """Authenticate a user"""
        user = await self.get_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        
        # Return User schema without password
        return UserSchema(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            company_name=user.company_name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            updated_at=user.updated_at
        )