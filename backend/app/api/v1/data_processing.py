"""
Data Processing API endpoints for async job management
"""

import logging
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_async_db
from app.models.data_processing_job import DataProcessingJob
from app.models.data_source import DataSource
from app.models.user import User
from app.services.data_processor import DataProcessingService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/data-processing", tags=["data-processing"])


class JobCreateRequest(BaseModel):
    """Request model for creating a data processing job"""
    data_source_id: str = Field(..., description="UUID of the data source to process")
    job_type: str = Field(..., description="Type of job: upload, sync, validate")
    config: dict[str, Any] | None = Field(None, description="Optional job configuration")

    class Config:
        json_schema_extra = {
            "example": {
                "data_source_id": "550e8400-e29b-41d4-a716-446655440000",
                "job_type": "upload",
                "config": {
                    "chunk_size": 10000,
                    "validate_quality": True,
                    "create_dataset": True
                }
            }
        }


class JobResponse(BaseModel):
    """Response model for job operations"""
    job_id: str
    data_source_id: str
    user_id: str
    job_type: str
    status: str
    progress_percentage: float
    current_step: str | None
    started_at: str | None
    completed_at: str | None
    processing_time_seconds: float | None
    error_message: str | None
    can_retry: bool
    retry_count: int
    result_summary: dict[str, Any] | None

    class Config:
        from_attributes = True


class JobStatusResponse(BaseModel):
    """Simplified response model for job status checks"""
    job_id: str
    status: str
    progress_percentage: float
    current_step: str | None
    error_message: str | None
    can_retry: bool


@router.post("/jobs", response_model=dict[str, str], status_code=status.HTTP_201_CREATED)
async def create_job(
    request: JobCreateRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Create a new data processing job
    
    This endpoint creates a data processing job and starts processing in the background.
    The job will be executed asynchronously, and clients can poll the status endpoint
    to check progress.
    """
    try:
        # Validate data source exists and belongs to user
        data_source = await db.get(DataSource, request.data_source_id)
        if not data_source:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data source not found"
            )
        
        if data_source.user_id != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to data source"
            )
        
        # Validate job type
        valid_job_types = ["upload", "sync", "validate"]
        if request.job_type not in valid_job_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid job type. Must be one of: {', '.join(valid_job_types)}"
            )
        
        # Create data processing service
        service = DataProcessingService(db)
        
        # Create the job
        job = await service.create_processing_job(
            data_source_id=request.data_source_id,
            user_id=str(current_user.id),
            job_type=request.job_type,
            config=request.config
        )
        
        # Start processing in background
        background_tasks.add_task(
            process_job_background,
            str(job.id),
            db
        )
        
        logger.info(f"Created job {job.id} for user {current_user.id}")
        
        return {
            "job_id": str(job.id),
            "status": "created",
            "message": "Job created successfully and processing started"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to create job for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create processing job"
        )


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get the current status of a data processing job
    
    Returns the current progress, status, and any error information for the job.
    """
    try:
        # Get the job
        job = await db.get(DataProcessingJob, job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        # Verify ownership
        if job.user_id != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to job"
            )
        
        # Create service to get detailed status
        service = DataProcessingService(db)
        status_info = await service.get_job_status(job_id)
        
        return JobStatusResponse(
            job_id=status_info["job_id"],
            status=status_info["status"],
            progress_percentage=status_info["progress_percentage"],
            current_step=status_info.get("current_step"),
            error_message=status_info.get("error_message"),
            can_retry=status_info.get("can_retry", False)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to get job status for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve job status"
        )


@router.post("/jobs/{job_id}/retry", response_model=dict[str, str])
async def retry_job(
    job_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Retry a failed data processing job
    
    Resets the job status and starts processing again. Only works for failed jobs
    that haven't exceeded the maximum retry count.
    """
    try:
        # Get the job
        job = await db.get(DataProcessingJob, job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        # Verify ownership
        if job.user_id != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to job"
            )
        
        # Check if job can be retried
        if job.status != "failed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only failed jobs can be retried"
            )
        
        if not job.can_retry:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Job has exceeded maximum retry attempts"
            )
        
        # Start retry in background
        background_tasks.add_task(
            retry_job_background,
            job_id,
            db
        )
        
        logger.info(f"Retrying job {job_id} for user {current_user.id}")
        
        return {
            "job_id": job_id,
            "status": "retry_initiated",
            "message": "Job retry started successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to retry job for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retry job"
        )


@router.get("/jobs", response_model=list[JobResponse])
async def list_jobs(
    status_filter: str | None = None,
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    List data processing jobs for the current user
    
    Returns a paginated list of jobs with optional status filtering.
    """
    try:
        from sqlalchemy import desc, select
        
        # Build query
        query = select(DataProcessingJob).where(
            DataProcessingJob.user_id == str(current_user.id)
        )
        
        # Apply status filter if provided
        if status_filter:
            query = query.where(DataProcessingJob.status == status_filter)
        
        # Add pagination and ordering
        query = query.order_by(desc(DataProcessingJob.created_at)).limit(limit).offset(offset)
        
        # Execute query
        result = await db.execute(query)
        jobs = result.scalars().all()
        
        # Convert to response model
        job_responses = []
        for job in jobs:
            job_responses.append(JobResponse(
                job_id=str(job.id),
                data_source_id=job.data_source_id,
                user_id=job.user_id,
                job_type=job.job_type,
                status=job.status,
                progress_percentage=job.progress_percentage,
                current_step=job.current_step,
                started_at=job.started_at.isoformat() if job.started_at else None,
                completed_at=job.completed_at.isoformat() if job.completed_at else None,
                processing_time_seconds=job.processing_time_seconds,
                error_message=job.error_message,
                can_retry=job.can_retry,
                retry_count=job.retry_count,
                result_summary=job.result_summary
            ))
        
        return job_responses
        
    except Exception as e:
        logger.exception(f"Failed to list jobs for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve jobs"
        )


async def process_job_background(job_id: str, db: AsyncSession):
    """
    Background task to process a data processing job
    """
    try:
        service = DataProcessingService(db)
        result = await service.process_data_source(job_id)
        
        if result["success"]:
            logger.info(f"Job {job_id} completed successfully")
        else:
            logger.error(f"Job {job_id} failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        logger.exception(f"Background job {job_id} failed with exception: {e}")


async def retry_job_background(job_id: str, db: AsyncSession):
    """
    Background task to retry a failed job
    """
    try:
        service = DataProcessingService(db)
        result = await service.retry_failed_job(job_id)
        
        if result["success"]:
            logger.info(f"Job {job_id} retry completed successfully")
        else:
            logger.error(f"Job {job_id} retry failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        logger.exception(f"Background job retry {job_id} failed with exception: {e}")