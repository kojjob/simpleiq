"""
Database models initialization
"""

# Import all models here to ensure they are registered with SQLAlchemy
from app.models.user import User
from app.models.data_source import DataSource, DataSourceType, ConnectionStatus, ProcessingStatus
from app.models.dataset import Dataset
from app.models.data_processing_job import DataProcessingJob

__all__ = [
    "User",
    "DataSource",
    "DataSourceType", 
    "ConnectionStatus",
    "ProcessingStatus",
    "Dataset",
    "DataProcessingJob"
]