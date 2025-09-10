"""
Data connectivity API endpoints
"""

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db as get_async_db
from app.database import get_db as get_sync_db
from app.services.data_source_service import DataSourceService
from app.models.schemas.data import (
    DataSourceCreate,
    DataSourceResponse,
    DataSourceUpdate,
    DataSourceType,
    DataSourceStatus,
    ConnectionTestResponse,
    TableInfo,
)

router = APIRouter()


@router.get("/sources", response_model=List[DataSourceResponse])
async def list_data_sources(
    db: Session = Depends(get_sync_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    List all data sources for the current user
    """
    service = DataSourceService(db)
    data_sources = service.get_data_sources(skip=skip, limit=limit)
    
    # Convert to response format
    response = []
    for ds in data_sources:
        response.append({
            "id": str(ds.id),
            "name": ds.name,
            "type": ds.type.value,
            "status": ds.status.value,
            "host": ds.host,
            "port": ds.port,
            "database": ds.database,
            "username": ds.username,
            "connection_string": ds.connection_string,
            "description": ds.description,
            "tables_count": ds.tables_count,
            "size": ds.size,
            "last_connected": ds.last_connected,
            "created_at": ds.created_at,
            "updated_at": ds.updated_at,
        })
    
    return response


@router.post("/sources", response_model=DataSourceResponse)
async def create_data_source(
    data_source: DataSourceCreate,
    db: Session = Depends(get_sync_db),
) -> Any:
    """
    Create a new data source connection
    """
    service = DataSourceService(db)
    
    try:
        # Create the data source
        ds = service.create_data_source(data_source)
        
        return {
            "id": str(ds.id),
            "name": ds.name,
            "type": ds.type.value,
            "status": ds.status.value,
            "host": ds.host,
            "port": ds.port,
            "database": ds.database,
            "username": ds.username,
            "connection_string": ds.connection_string,
            "description": ds.description,
            "tables_count": ds.tables_count,
            "size": ds.size,
            "last_connected": ds.last_connected,
            "created_at": ds.created_at,
            "updated_at": ds.updated_at,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create data source: {str(e)}",
        )


@router.post("/sources/{source_id}/test", response_model=ConnectionTestResponse)
async def test_connection(
    source_id: str,
    db: Session = Depends(get_sync_db),
) -> Any:
    """
    Test connection to a data source
    """
    service = DataSourceService(db)
    
    try:
        source_id_int = int(source_id)
        result = service.test_connection(source_id_int)
        return result
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid source ID format",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Connection test failed: {str(e)}",
        )


@router.post("/sources/{source_id}/sync")
async def sync_data_source(
    source_id: str,
    db: Session = Depends(get_sync_db),
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
    db: Session = Depends(get_sync_db),
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


@router.put("/sources/{source_id}", response_model=DataSourceResponse)
async def update_data_source(
    source_id: str,
    data_source: DataSourceUpdate,
    db: Session = Depends(get_sync_db),
) -> Any:
    """
    Update a data source
    """
    service = DataSourceService(db)
    
    try:
        source_id_int = int(source_id)
        ds = service.update_data_source(source_id_int, data_source)
        
        if not ds:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data source not found",
            )
        
        return {
            "id": str(ds.id),
            "name": ds.name,
            "type": ds.type.value,
            "status": ds.status.value,
            "host": ds.host,
            "port": ds.port,
            "database": ds.database,
            "username": ds.username,
            "connection_string": ds.connection_string,
            "description": ds.description,
            "tables_count": ds.tables_count,
            "size": ds.size,
            "last_connected": ds.last_connected,
            "created_at": ds.created_at,
            "updated_at": ds.updated_at,
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid source ID format",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update data source: {str(e)}",
        )


@router.delete("/sources/{source_id}")
async def delete_data_source(
    source_id: str,
    db: Session = Depends(get_sync_db),
) -> Any:
    """
    Delete a data source
    """
    service = DataSourceService(db)
    
    try:
        source_id_int = int(source_id)
        success = service.delete_data_source(source_id_int)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data source not found",
            )
        
        return {"message": f"Data source {source_id} deleted successfully"}
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid source ID format",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete data source: {str(e)}",
        )