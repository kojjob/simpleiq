"""
Dataset model for storing processed data from data sources
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Dataset(Base):
    """
    Dataset model for storing processed data from data sources
    Tracks versions, quality metrics, and relationships to source data
    """
    
    __tablename__ = "datasets"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    
    # Foreign keys
    data_source_id = Column(UUID(as_uuid=True), ForeignKey("data_sources.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Dataset information
    name = Column(String(255), nullable=False)
    table_name = Column(String(255), nullable=False, unique=True)  # Physical table in data warehouse
    description = Column(String(500), nullable=True)
    
    # Schema information
    schema_info = Column(JSON, nullable=False)  # Column names, types, constraints
    
    # Statistics
    row_count = Column(Integer, nullable=True)
    column_count = Column(Integer, nullable=True)
    size_mb = Column(Float, nullable=True)
    
    # Data quality metrics
    quality_score = Column(Float, nullable=True)  # 0.0 to 1.0
    completeness_score = Column(Float, nullable=True)  # Percentage of non-null values
    null_percentages = Column(JSON, nullable=True)  # Per column null percentages
    duplicate_count = Column(Integer, nullable=True)
    
    # Data profiling
    column_statistics = Column(JSON, nullable=True)  # Min, max, mean, median, std for numeric columns
    value_distributions = Column(JSON, nullable=True)  # Top N values per column
    
    # Versioning
    version = Column(Integer, default=1, nullable=False)
    is_current = Column(Boolean, default=True, nullable=False, index=True)
    parent_dataset_id = Column(UUID(as_uuid=True), nullable=True)  # For tracking lineage
    
    # Processing metadata
    processing_time_seconds = Column(Float, nullable=True)
    processing_config = Column(JSON, nullable=True)  # Configuration used for processing
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)  # For temporary datasets
    
    # Soft delete
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    data_source = relationship("DataSource", back_populates="datasets")
    user = relationship("User", backref="datasets")
    
    # Indexes for performance
    __table_args__ = (
        Index("idx_dataset_source_current", "data_source_id", "is_current"),
        Index("idx_dataset_user_current", "user_id", "is_current"),
        Index("idx_dataset_version", "data_source_id", "version"),
    )
    
    def __repr__(self) -> str:
        return f"<Dataset(id={self.id}, name={self.name}, version={self.version})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if dataset has expired"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False