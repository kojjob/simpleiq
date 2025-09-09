"""
Data connectivity API endpoints
"""

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.schemas.data import (
    DataSourceCreate,
    DataSourceResponse,
    DataSourceType,
    GoogleSheetsConfig,
)

router = APIRouter()


@router.get("/sources", response_model=List[DataSourceResponse])
async def list_data_sources(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    List all data sources for the current user
    """
    # Placeholder response
    return [
        {
            "id": "1",
            "name": "Sales Data",
            "type": DataSourceType.GOOGLE_SHEETS,
            "status": "active",
            "last_sync": "2024-01-15T10:30:00Z",
            "created_at": "2024-01-01T00:00:00Z",
        }
    ]


@router.post("/sources", response_model=DataSourceResponse)
async def create_data_source(
    data_source: DataSourceCreate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create a new data source connection
    """
    # Validate based on source type
    if data_source.type == DataSourceType.GOOGLE_SHEETS:
        if not data_source.config.get("spreadsheet_id"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google Sheets requires spreadsheet_id",
            )
    
    # Create data source (placeholder)
    return {
        "id": "new-source-id",
        "name": data_source.name,
        "type": data_source.type,
        "status": "pending",
        "created_at": "2024-01-15T10:30:00Z",
    }


@router.post("/sources/{source_id}/sync")
async def sync_data_source(
    source_id: str,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Trigger a manual sync for a data source
    """
    # Trigger sync job (placeholder)
    return {
        "message": f"Sync initiated for source {source_id}",
        "job_id": "sync-job-123",
        "status": "queued",
    }


@router.post("/upload/csv")
async def upload_csv(
    file: UploadFile = File(...),
    name: str = "Uploaded CSV",
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Upload a CSV file as a data source
    """
    # Validate file type
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV",
        )
    
    # Process CSV upload (placeholder)
    contents = await file.read()
    
    return {
        "id": "csv-source-id",
        "name": name,
        "type": DataSourceType.CSV,
        "status": "processing",
        "file_size": len(contents),
        "created_at": "2024-01-15T10:30:00Z",
    }


@router.delete("/sources/{source_id}")
async def delete_data_source(
    source_id: str,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Delete a data source
    """
    # Delete data source (placeholder)
    return {"message": f"Data source {source_id} deleted successfully"}