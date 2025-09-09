"""
Dashboard management API endpoints
"""

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.schemas.dashboard import (
    DashboardCreate,
    DashboardResponse,
    DashboardUpdate,
    WidgetCreate,
    ChartType,
)

router = APIRouter()


@router.get("/", response_model=List[DashboardResponse])
async def list_dashboards(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    List all dashboards for the current user
    """
    # Return dashboards (placeholder)
    return [
        {
            "id": "dashboard-1",
            "name": "Sales Overview",
            "description": "Main sales performance dashboard",
            "widgets": [
                {
                    "id": "widget-1",
                    "title": "Monthly Sales",
                    "type": ChartType.LINE,
                    "query": "Show me sales by month",
                    "position": {"x": 0, "y": 0, "w": 6, "h": 4},
                },
                {
                    "id": "widget-2",
                    "title": "Top Products",
                    "type": ChartType.BAR,
                    "query": "What are my top 10 products?",
                    "position": {"x": 6, "y": 0, "w": 6, "h": 4},
                },
            ],
            "is_public": False,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-15T10:30:00Z",
        }
    ]


@router.post("/", response_model=DashboardResponse)
async def create_dashboard(
    dashboard: DashboardCreate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create a new dashboard
    """
    # Create dashboard (placeholder)
    return {
        "id": "new-dashboard-id",
        "name": dashboard.name,
        "description": dashboard.description,
        "widgets": [],
        "is_public": dashboard.is_public,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z",
    }


@router.get("/{dashboard_id}", response_model=DashboardResponse)
async def get_dashboard(
    dashboard_id: str,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get a specific dashboard
    """
    # Get dashboard (placeholder)
    if dashboard_id == "not-found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found",
        )
    
    return {
        "id": dashboard_id,
        "name": "Sales Overview",
        "description": "Main sales performance dashboard",
        "widgets": [],
        "is_public": False,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-15T10:30:00Z",
    }


@router.put("/{dashboard_id}", response_model=DashboardResponse)
async def update_dashboard(
    dashboard_id: str,
    dashboard: DashboardUpdate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Update a dashboard
    """
    # Update dashboard (placeholder)
    return {
        "id": dashboard_id,
        "name": dashboard.name or "Sales Overview",
        "description": dashboard.description,
        "widgets": [],
        "is_public": dashboard.is_public or False,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-15T11:00:00Z",
    }


@router.delete("/{dashboard_id}")
async def delete_dashboard(
    dashboard_id: str,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Delete a dashboard
    """
    # Delete dashboard (placeholder)
    return {"message": f"Dashboard {dashboard_id} deleted successfully"}


@router.post("/{dashboard_id}/widgets", response_model=Any)
async def add_widget(
    dashboard_id: str,
    widget: WidgetCreate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Add a widget to a dashboard
    """
    # Add widget (placeholder)
    return {
        "id": "new-widget-id",
        "dashboard_id": dashboard_id,
        "title": widget.title,
        "type": widget.type,
        "query": widget.query,
        "position": widget.position,
        "created_at": "2024-01-15T10:30:00Z",
    }


@router.delete("/{dashboard_id}/widgets/{widget_id}")
async def remove_widget(
    dashboard_id: str,
    widget_id: str,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Remove a widget from a dashboard
    """
    # Remove widget (placeholder)
    return {"message": f"Widget {widget_id} removed from dashboard {dashboard_id}"}