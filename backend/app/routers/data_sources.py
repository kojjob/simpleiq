
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.data_source import (
    ConnectionTestResponse,
    DataSourceCreate,
    DataSourceResponse,
    DataSourceStats,
    DataSourceUpdate,
    DataSourceWithTables,
)
from app.services.data_source_service import DataSourceService

router = APIRouter(prefix="/api/data-sources", tags=["data-sources"])


@router.get("/", response_model=list[DataSourceResponse])
async def get_data_sources(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all data sources"""
    service = DataSourceService(db)
    data_sources = service.get_data_sources(skip=skip, limit=limit)
    return data_sources


@router.get("/stats", response_model=DataSourceStats)
async def get_data_source_stats(db: Session = Depends(get_db)):
    """Get data source statistics"""
    service = DataSourceService(db)
    stats = service.get_stats()
    return DataSourceStats(**stats)


@router.get("/{data_source_id}", response_model=DataSourceWithTables)
async def get_data_source(
    data_source_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific data source by ID"""
    service = DataSourceService(db)
    data_source = service.get_data_source(data_source_id)
    
    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    # Convert to response model
    data_source_dict = {
        **data_source.__dict__,
        "tables": []  # Would be populated from actual database introspection
    }
    
    return DataSourceWithTables(**data_source_dict)


@router.post("/", response_model=DataSourceResponse)
async def create_data_source(
    data_source: DataSourceCreate,
    db: Session = Depends(get_db)
):
    """Create a new data source"""
    service = DataSourceService(db)
    return service.create_data_source(data_source)


@router.put("/{data_source_id}", response_model=DataSourceResponse)
async def update_data_source(
    data_source_id: int,
    data_source: DataSourceUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing data source"""
    service = DataSourceService(db)
    updated_data_source = service.update_data_source(data_source_id, data_source)
    
    if not updated_data_source:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    return updated_data_source


@router.delete("/{data_source_id}")
async def delete_data_source(
    data_source_id: int,
    db: Session = Depends(get_db)
):
    """Delete a data source"""
    service = DataSourceService(db)
    success = service.delete_data_source(data_source_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    return {"message": "Data source deleted successfully"}


@router.post("/{data_source_id}/test", response_model=ConnectionTestResponse)
async def test_data_source_connection(
    data_source_id: int,
    db: Session = Depends(get_db)
):
    """Test connection to a data source"""
    service = DataSourceService(db)
    result = service.test_connection(data_source_id)
    
    if not result.success:
        # Don't raise HTTP error, return the failure response
        pass
    
    return result


@router.get("/{data_source_id}/tables")
async def get_data_source_tables(
    data_source_id: int,
    db: Session = Depends(get_db)
):
    """Get tables from a specific data source"""
    service = DataSourceService(db)
    data_source = service.get_data_source(data_source_id)
    
    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    # Test connection to get fresh table information
    result = service.test_connection(data_source_id)
    
    if result.success:
        return {
            "data_source_id": data_source_id,
            "tables": result.tables,
            "tables_count": result.tables_count,
            "size": result.size
        }
    raise HTTPException(status_code=400, detail=f"Cannot retrieve tables: {result.message}")


@router.post("/{data_source_id}/sync")
async def sync_data_source(
    data_source_id: int,
    db: Session = Depends(get_db)
):
    """Sync/refresh data source metadata"""
    service = DataSourceService(db)
    result = service.test_connection(data_source_id)
    
    if result.success:
        return {
            "message": "Data source synced successfully",
            "tables_count": result.tables_count,
            "size": result.size,
            "status": "connected"
        }
    return {
        "message": f"Sync failed: {result.message}",
        "status": "error"
    }