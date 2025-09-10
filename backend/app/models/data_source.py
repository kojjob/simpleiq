"""
Data source database models for managing connected data sources
Production-ready with proper async support, validation, and security
"""

from enum import Enum as PyEnum
from uuid import uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class DataSourceType(str, PyEnum):
    """Enumeration of supported data source types"""
    # File-based sources
    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"
    PARQUET = "parquet"
    
    # Cloud sources
    GOOGLE_SHEETS = "google_sheets"
    S3 = "s3"
    
    # Databases
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    MONGODB = "mongodb"
    BIGQUERY = "bigquery"
    SNOWFLAKE = "snowflake"
    
    # APIs
    REST_API = "rest_api"
    GRAPHQL = "graphql"


class ConnectionStatus(str, PyEnum):
    """Enumeration of connection statuses"""
    PENDING = "pending"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    SYNCING = "syncing"
    ERROR = "error"
    DISCONNECTED = "disconnected"
    UNAUTHORIZED = "unauthorized"


class ProcessingStatus(str, PyEnum):
    """Enumeration of data processing statuses"""
    QUEUED = "queued"
    VALIDATING = "validating"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DataSource(Base):
    """
    Data source model for managing user data connections
    Supports multi-tenancy, encryption, and comprehensive metadata
    """
    
    __tablename__ = "data_sources"
    
    # Primary key - Using UUID for better security and scalability
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    
    # User relationship for multi-tenancy
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Basic information
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(Enum(DataSourceType), nullable=False, index=True)
    status = Column(Enum(ConnectionStatus), default=ConnectionStatus.PENDING, nullable=False, index=True)
    
    # Connection configuration (will be encrypted in production)
    connection_config = Column(JSON, nullable=True)  # Stores encrypted credentials
    
    # File-specific fields (for CSV, Excel, etc.)
    file_path = Column(String(500), nullable=True)  # S3 path or local storage
    file_size_bytes = Column(Integer, nullable=True)
    file_hash = Column(String(64), nullable=True)  # SHA-256 for integrity
    
    # Google Sheets specific
    google_sheet_id = Column(String(255), nullable=True)
    google_sheet_name = Column(String(255), nullable=True)
    
    # Schema and metadata
    schema_info = Column(JSON, nullable=True)  # Column names, types, constraints
    
    # Statistics
    row_count = Column(Integer, nullable=True)
    column_count = Column(Integer, nullable=True)
    size_mb = Column(Float, nullable=True)
    
    # Sync configuration
    sync_enabled = Column(Boolean, default=False, nullable=False)
    sync_frequency_minutes = Column(Integer, nullable=True)
    last_synced_at = Column(DateTime(timezone=True), nullable=True)
    next_sync_at = Column(DateTime(timezone=True), nullable=True)
    
    # Data quality metrics
    quality_score = Column(Float, nullable=True)  # 0.0 to 1.0
    validation_errors = Column(JSON, nullable=True)
    
    # Error tracking
    error_message = Column(Text, nullable=True)
    error_count = Column(Integer, default=0, nullable=False)
    last_error_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True)
    
    # Soft delete for data retention
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", backref="data_sources", lazy="joined")
    datasets = relationship("Dataset", back_populates="data_source", cascade="all, delete-orphan")
    processing_jobs = relationship("DataProcessingJob", back_populates="data_source", cascade="all, delete-orphan")
    
    # Constraints for data integrity
    __table_args__ = (
        UniqueConstraint("user_id", "name", "is_deleted", name="uq_user_data_source_name"),
        Index("idx_data_source_user_status", "user_id", "status"),
        Index("idx_data_source_type_status", "type", "status"),
        Index("idx_data_source_sync", "sync_enabled", "next_sync_at"),
    )
    
    def __repr__(self) -> str:
        return f"<DataSource(id={self.id}, name={self.name}, type={self.type}, status={self.status})>"
    
    @property
    def is_file_based(self) -> bool:
        """Check if this is a file-based data source"""
        return self.type in [DataSourceType.CSV, DataSourceType.EXCEL, 
                            DataSourceType.JSON, DataSourceType.PARQUET]
    
    @property
    def requires_auth(self) -> bool:
        """Check if this data source requires authentication"""
        return self.type in [DataSourceType.GOOGLE_SHEETS, DataSourceType.POSTGRESQL,
                            DataSourceType.MYSQL, DataSourceType.MONGODB,
                            DataSourceType.BIGQUERY, DataSourceType.SNOWFLAKE,
                            DataSourceType.REST_API, DataSourceType.GRAPHQL]