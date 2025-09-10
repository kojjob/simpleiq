"""
Async data processing service for handling data ingestion and transformation
"""

import asyncio
import logging
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.connectors.base import BaseConnector
from app.connectors.csv_connector import CSVConnector
from app.core.database import get_async_db
from app.models.data_processing_job import DataProcessingJob
from app.models.data_source import ConnectionStatus, DataSource, DataSourceType
from app.models.dataset import Dataset

logger = logging.getLogger(__name__)


class DataProcessingService:
    """
    Service for processing data from various sources asynchronously
    Handles job execution, progress tracking, and error management
    """
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def create_processing_job(
        self,
        data_source_id: str,
        user_id: str,
        job_type: str,
        config: dict[str, Any] | None = None
    ) -> DataProcessingJob:
        """
        Create a new data processing job
        
        Args:
            data_source_id: UUID of the data source
            user_id: UUID of the user
            job_type: Type of job (upload, sync, validate, etc.)
            config: Optional job configuration
            
        Returns:
            Created DataProcessingJob instance
        """
        job = DataProcessingJob(
            data_source_id=data_source_id,
            user_id=user_id,
            job_type=job_type,
            processing_config=config or {}
        )
        
        self.db_session.add(job)
        await self.db_session.commit()
        await self.db_session.refresh(job)
        
        self.logger.info(f"Created processing job {job.id} of type {job_type}")
        return job
    
    async def process_data_source(self, job_id: str) -> dict[str, Any]:
        """
        Process a data source asynchronously
        
        Args:
            job_id: UUID of the processing job
            
        Returns:
            Processing result dictionary
        """
        # Get the job
        job = await self.db_session.get(DataProcessingJob, job_id)
        if not job:
            msg = f"Job {job_id} not found"
            self.logger.error(msg)
            return {"success": False, "error": msg}
        
        # Update job status to processing
        job.status = "processing"
        job.started_at = datetime.now(datetime.UTC)
        job.current_step = "Initializing"
        await self.db_session.commit()
        
        try:
            # Get the data source
            data_source = await self.db_session.get(DataSource, job.data_source_id)
            if not data_source:
                return await self._handle_job_error(job, "Data source not found")
            
            # Get appropriate connector
            connector = await self._get_connector(data_source)
            if not connector:
                return await self._handle_job_error(job, f"No connector available for {data_source.type}")
            
            # Process based on job type
            result = await self._execute_job(job, connector)
            
            # Update job completion
            job.status = "completed"
            job.completed_at = datetime.now(datetime.UTC)
            job.processing_time_seconds = (job.completed_at - job.started_at).total_seconds()
            job.progress_percentage = 100.0
            job.result_summary = result
            
            await self.db_session.commit()
            
            self.logger.info(f"Job {job_id} completed successfully")
            return {"success": True, "job_id": job_id, "result": result}
            
        except Exception as e:
            self.logger.exception(f"Job {job_id} failed with error: {e}")
            return await self._handle_job_error(job, str(e))
    
    async def _get_connector(self, data_source: DataSource) -> BaseConnector | None:
        """Get appropriate connector for data source type"""
        if data_source.type == DataSourceType.csv:
            return CSVConnector(data_source, self.db_session)
        
        # Add other connectors here as implemented
        return None
    
    async def _execute_job(self, job: DataProcessingJob, connector: BaseConnector) -> dict[str, Any]:
        """Execute the actual job processing"""
        job_type = job.job_type
        
        if job_type == "upload":
            return await self._process_upload(job, connector)
        elif job_type == "sync":
            return await self._process_sync(job, connector)
        elif job_type == "validate":
            return await self._process_validation(job, connector)
        else:
            msg = f"Unknown job type: {job_type}"
            raise ValueError(msg)
    
    async def _process_upload(self, job: DataProcessingJob, connector: BaseConnector) -> dict[str, Any]:
        """Process file upload"""
        job.current_step = "Validating connection"
        job.progress_percentage = 10.0
        await self.db_session.commit()
        
        # Validate connection
        is_valid, error = await connector.validate_connection()
        if not is_valid:
            raise ValueError(f"Connection validation failed: {error}")
        
        job.current_step = "Analyzing schema"
        job.progress_percentage = 30.0
        await self.db_session.commit()
        
        # Get schema
        schema = await connector.fetch_schema()
        
        job.current_step = "Processing data"
        job.progress_percentage = 50.0
        await self.db_session.commit()
        
        # Validate data quality
        sample_data = await connector.fetch_data(limit=1000)
        is_valid, errors = await connector.validate_data(sample_data)
        
        if not is_valid:
            self.logger.warning(f"Data quality issues found: {errors}")
        
        job.current_step = "Creating dataset"
        job.progress_percentage = 80.0
        await self.db_session.commit()
        
        # Create dataset
        dataset = await self._create_dataset(job, schema, len(sample_data))
        
        job.current_step = "Finalizing"
        job.progress_percentage = 95.0
        await self.db_session.commit()
        
        return {
            "schema": schema,
            "dataset_id": str(dataset.id),
            "rows_processed": len(sample_data),
            "quality_issues": errors if not is_valid else [],
            "processing_time": job.processing_time_seconds
        }
    
    async def _process_sync(self, job: DataProcessingJob, connector: BaseConnector) -> dict[str, Any]:
        """Process data synchronization"""
        job.current_step = "Syncing data"
        job.progress_percentage = 20.0
        await self.db_session.commit()
        
        # Count total rows
        total_rows = await connector.count_rows()
        job.total_rows = total_rows
        
        # Fetch data in chunks
        chunk_size = 10000
        rows_processed = 0
        
        for offset in range(0, total_rows, chunk_size):
            chunk_data = await connector.fetch_data(limit=chunk_size, offset=offset)
            rows_processed += len(chunk_data)
            
            # Update progress
            job.rows_processed = rows_processed
            job.progress_percentage = (rows_processed / total_rows) * 80 + 20
            await self.db_session.commit()
            
            # Simulate processing delay
            await asyncio.sleep(0.1)
        
        return {
            "total_rows": total_rows,
            "rows_processed": rows_processed,
            "sync_completed": True
        }
    
    async def _process_validation(self, job: DataProcessingJob, connector: BaseConnector) -> dict[str, Any]:
        """Process data validation"""
        job.current_step = "Validating data quality"
        job.progress_percentage = 25.0
        await self.db_session.commit()
        
        # Get sample data
        sample_data = await connector.fetch_data(limit=5000)
        
        job.progress_percentage = 75.0
        await self.db_session.commit()
        
        # Validate data
        is_valid, errors = await connector.validate_data(sample_data)
        
        return {
            "is_valid": is_valid,
            "errors": errors,
            "sample_size": len(sample_data),
            "validation_completed": True
        }
    
    async def _create_dataset(self, job: DataProcessingJob, schema: dict[str, Any], row_count: int) -> Dataset:
        """Create a dataset from processed data"""
        data_source = await self.db_session.get(DataSource, job.data_source_id)
        
        dataset = Dataset(
            data_source_id=job.data_source_id,
            user_id=job.user_id,
            name=f"{data_source.name} Dataset",
            table_name=f"dataset_{job.data_source_id}".replace("-", "_"),
            description=f"Processed dataset from {data_source.name}",
            schema_info=schema,
            row_count=row_count,
            column_count=len(schema.get("columns", [])),
            quality_score=schema.get("quality_score", 0.8)
        )
        
        self.db_session.add(dataset)
        await self.db_session.commit()
        await self.db_session.refresh(dataset)
        
        return dataset
    
    async def _handle_job_error(self, job: DataProcessingJob, error_message: str) -> dict[str, Any]:
        """Handle job errors and update status"""
        job.status = "failed"
        job.error_message = error_message
        job.completed_at = datetime.now(datetime.UTC)
        
        if job.started_at:
            job.processing_time_seconds = (job.completed_at - job.started_at).total_seconds()
        
        # Increment retry count
        job.retry_count += 1
        
        await self.db_session.commit()
        
        return {
            "success": False,
            "error": error_message,
            "job_id": str(job.id),
            "can_retry": job.can_retry
        }
    
    async def get_job_status(self, job_id: str) -> dict[str, Any]:
        """Get current status of a processing job"""
        job = await self.db_session.get(DataProcessingJob, job_id)
        if not job:
            return {"error": "Job not found"}
        
        return {
            "job_id": str(job.id),
            "status": job.status,
            "progress_percentage": job.progress_percentage,
            "current_step": job.current_step,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "processing_time_seconds": job.processing_time_seconds,
            "error_message": job.error_message,
            "can_retry": job.can_retry if job.status == "failed" else False,
            "result_summary": job.result_summary
        }
    
    async def retry_failed_job(self, job_id: str) -> dict[str, Any]:
        """Retry a failed job"""
        job = await self.db_session.get(DataProcessingJob, job_id)
        if not job:
            return {"success": False, "error": "Job not found"}
        
        if not job.can_retry:
            return {"success": False, "error": "Job cannot be retried"}
        
        # Reset job status
        job.status = "queued"
        job.error_message = None
        job.started_at = None
        job.completed_at = None
        job.progress_percentage = 0.0
        job.current_step = None
        
        await self.db_session.commit()
        
        # Reprocess the job
        return await self.process_data_source(str(job.id))