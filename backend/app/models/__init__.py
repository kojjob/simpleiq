"""
Database models initialization
"""

# Import all models here to ensure they are registered with SQLAlchemy
from app.models.data_processing_job import DataProcessingJob
from app.models.data_source import (
    ConnectionStatus,
    DataSource,
    DataSourceType,
    ProcessingStatus,
)
from app.models.dataset import Dataset
from app.models.user import User

__all__ = [
    "ConnectionStatus",
    "DataProcessingJob",
    "DataSource",
    "DataSourceType",
    "Dataset",
    "ProcessingStatus",
    "User"
]