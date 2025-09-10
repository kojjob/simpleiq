"""
Data processing job model for tracking async data processing tasks
"""

from uuid import uuid4

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base
from app.models.data_source import ProcessingStatus


class DataProcessingJob(Base):
    """
    Model for tracking data processing jobs with comprehensive monitoring
    Supports async processing, progress tracking, and error handling
    """
    
    __tablename__ = "data_processing_jobs"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    
    # Foreign keys
    data_source_id = Column(UUID(as_uuid=True), ForeignKey("data_sources.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id", ondelete="SET NULL"), nullable=True)
    
    # Job information
    job_type = Column(String(50), nullable=False, index=True)  # upload, sync, refresh, validate, transform
    status = Column(String(50), default=ProcessingStatus.QUEUED.value, nullable=False, index=True)
    priority = Column(Integer, default=5, nullable=False)  # 1-10, higher is more urgent
    
    # File information (for uploads)
    file_name = Column(String(255), nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    file_path = Column(String(500), nullable=True)  # S3 or local path
    file_mime_type = Column(String(100), nullable=True)
    
    # Processing configuration
    processing_config = Column(JSON, nullable=True)  # Custom config per job type
    
    # Processing details
    total_rows = Column(Integer, nullable=True)
    rows_processed = Column(Integer, default=0, nullable=False)
    rows_succeeded = Column(Integer, default=0, nullable=False)
    rows_failed = Column(Integer, default=0, nullable=False)
    rows_skipped = Column(Integer, default=0, nullable=False)
    
    # Performance metrics
    memory_usage_mb = Column(Float, nullable=True)
    cpu_usage_percent = Column(Float, nullable=True)
    
    # Timing
    queued_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    processing_time_seconds = Column(Float, nullable=True)
    estimated_completion_at = Column(DateTime(timezone=True), nullable=True)
    
    # Error tracking
    error_message = Column(Text, nullable=True)
    error_details = Column(JSON, nullable=True)  # Stack trace, error codes, etc.
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    
    # Progress tracking
    progress_percentage = Column(Float, default=0.0, nullable=False)
    current_step = Column(String(255), nullable=True)
    steps_completed = Column(JSON, nullable=True)  # List of completed step names
    
    # Worker information
    worker_id = Column(String(100), nullable=True)  # Celery/RQ worker ID
    worker_hostname = Column(String(255), nullable=True)
    
    # Result storage
    result_summary = Column(JSON, nullable=True)  # Summary statistics, metrics
    result_location = Column(String(500), nullable=True)  # S3 path to detailed results
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True)
    
    # Relationships
    data_source = relationship("DataSource", back_populates="processing_jobs")
    dataset = relationship("Dataset", backref="processing_jobs")
    user = relationship("User", backref="processing_jobs")
    
    # Indexes for performance
    __table_args__ = (
        Index("idx_job_status_priority", "status", "priority"),
        Index("idx_job_user_status", "user_id", "status"),
        Index("idx_job_source_status", "data_source_id", "status"),
        Index("idx_job_created_status", "created_at", "status"),
        Index("idx_job_type_status", "job_type", "status"),
    )
    
    def __repr__(self) -> str:
        return f"<DataProcessingJob(id={self.id}, type={self.job_type}, status={self.status}, progress={self.progress_percentage}%)>"
    
    @property
    def is_complete(self) -> bool:
        """Check if job is complete"""
        return self.status in [ProcessingStatus.COMPLETED.value, ProcessingStatus.FAILED.value, ProcessingStatus.CANCELLED.value]
    
    @property
    def is_running(self) -> bool:
        """Check if job is currently running"""
        return self.status in [ProcessingStatus.PROCESSING.value, ProcessingStatus.VALIDATING.value]
    
    @property
    def can_retry(self) -> bool:
        """Check if job can be retried"""
        return self.status == ProcessingStatus.FAILED.value and self.retry_count < self.max_retries
    
    @property
    def estimated_time_remaining(self) -> float:
        """Estimate remaining processing time in seconds"""
        if self.progress_percentage > 0 and self.processing_time_seconds:
            total_estimated = self.processing_time_seconds / (self.progress_percentage / 100)
            return total_estimated - self.processing_time_seconds
        return None