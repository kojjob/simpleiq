"""
Base connector class for all data source connectors
"""

import logging
import re
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.data_processing_job import DataProcessingJob
from app.models.data_source import ConnectionStatus, DataSource

logger = logging.getLogger(__name__)


class BaseConnector(ABC):
    """
    Abstract base class for all data connectors
    Provides common interface and utility methods
    """
    
    def __init__(self, data_source: DataSource, db_session: AsyncSession):
        """
        Initialize connector with data source and database session
        
        Args:
            data_source: DataSource model instance
            db_session: Async database session
        """
        self.data_source = data_source
        self.db_session = db_session
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    async def validate_connection(self) -> tuple[bool, str | None]:
        """
        Validate connection to the data source
        
        Returns:
            Tuple of (success, error_message)
        """
    
    @abstractmethod
    async def fetch_schema(self) -> dict[str, Any]:
        """
        Fetch schema information from the data source
        
        Returns:
            Dictionary containing schema information
        """
    
    @abstractmethod
    async def fetch_data(
        self, 
        limit: int | None = None,
        offset: int | None = None,
        filters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """
        Fetch data from the source
        
        Args:
            limit: Maximum number of rows to fetch
            offset: Number of rows to skip
            filters: Optional filters to apply
            
        Returns:
            List of dictionaries representing rows
        """
    
    @abstractmethod
    async def count_rows(self) -> int:
        """
        Count total number of rows in the data source
        
        Returns:
            Total row count
        """
    
    @abstractmethod
    async def validate_data(self, data: list[dict[str, Any]]) -> tuple[bool, list[str]]:
        """
        Validate data quality and integrity
        
        Args:
            data: Data to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
    
    async def update_connection_status(
        self, 
        status: ConnectionStatus, 
        error_message: str | None = None
    ) -> None:
        """
        Update connection status in database
        
        Args:
            status: New connection status
            error_message: Optional error message
        """
        self.data_source.status = status
        if error_message:
            self.data_source.error_message = error_message
            self.data_source.error_count += 1
            self.data_source.last_error_at = datetime.now(datetime.UTC)
        
        await self.db_session.commit()
        self.logger.info(f"Updated connection status to {status} for data source {self.data_source.id}")
    
    async def create_processing_job(
        self,
        job_type: str,
        **kwargs
    ) -> DataProcessingJob:
        """
        Create a new processing job for this data source
        
        Args:
            job_type: Type of processing job
            **kwargs: Additional job parameters
            
        Returns:
            Created DataProcessingJob instance
        """
        job = DataProcessingJob(
            data_source_id=self.data_source.id,
            user_id=self.data_source.user_id,
            job_type=job_type,
            **kwargs
        )
        self.db_session.add(job)
        await self.db_session.commit()
        await self.db_session.refresh(job)
        
        self.logger.info(f"Created processing job {job.id} of type {job_type}")
        return job
    
    def get_type_mapping(self, pandas_dtype: str) -> str:
        """
        Map pandas data types to database types
        
        Args:
            pandas_dtype: Pandas data type string
            
        Returns:
            Database type string
        """
        type_map = {
            "int64": "INTEGER",
            "float64": "FLOAT",
            "object": "VARCHAR",
            "bool": "BOOLEAN",
            "datetime64": "TIMESTAMP",
            "datetime64[ns]": "TIMESTAMP",
            "timedelta64": "INTERVAL",
            "category": "VARCHAR"
        }
        return type_map.get(str(pandas_dtype), "VARCHAR")
    
    def sanitize_column_name(self, name: str) -> str:
        """
        Sanitize column name for database compatibility
        
        Args:
            name: Original column name
            
        Returns:
            Sanitized column name
        """
        # Replace spaces and special characters with underscores
        sanitized = re.sub(r"[^a-zA-Z0-9_]", "_", name)
        # Ensure it doesn't start with a number
        if sanitized and sanitized[0].isdigit():
            sanitized = f"col_{sanitized}"
        # Ensure it's not empty
        if not sanitized:
            sanitized = "column"
        # Truncate if too long (PostgreSQL limit is 63 characters)
        return sanitized[:63].lower()