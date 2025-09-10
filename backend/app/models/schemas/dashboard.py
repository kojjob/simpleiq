"""
Dashboard and widget schemas
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ChartType(str, Enum):
    """Supported chart types"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    TABLE = "table"
    KPI = "kpi"
    SCATTER = "scatter"
    HEATMAP = "heatmap"
    AREA = "area"


class WidgetPosition(BaseModel):
    """Widget position on dashboard grid"""
    x: int = Field(..., ge=0, le=12, description="X position (0-12)")
    y: int = Field(..., ge=0, description="Y position")
    w: int = Field(..., ge=1, le=12, description="Width (1-12)")
    h: int = Field(..., ge=1, le=12, description="Height (1-12)")


class WidgetCreate(BaseModel):
    """Create widget request"""
    title: str = Field(..., min_length=1, max_length=100)
    type: ChartType
    query: str = Field(..., min_length=1, max_length=500)
    position: WidgetPosition
    config: dict[str, Any] | None = Field(None, description="Chart configuration")
    refresh_interval: int | None = Field(None, ge=0, description="Auto-refresh in seconds")


class WidgetUpdate(BaseModel):
    """Update widget request"""
    title: str | None = Field(None, min_length=1, max_length=100)
    type: ChartType | None = None
    query: str | None = Field(None, min_length=1, max_length=500)
    position: WidgetPosition | None = None
    config: dict[str, Any] | None = None
    refresh_interval: int | None = Field(None, ge=0)


class WidgetResponse(BaseModel):
    """Widget response"""
    id: str
    title: str
    type: ChartType
    query: str
    position: WidgetPosition
    config: dict[str, Any] | None = None
    refresh_interval: int | None = None
    last_updated: datetime | None = None
    
    class Config:
        from_attributes = True


class DashboardCreate(BaseModel):
    """Create dashboard request"""
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    is_public: bool = Field(default=False, description="Make dashboard publicly accessible")
    tags: list[str] | None = Field(None, max_items=10)


class DashboardUpdate(BaseModel):
    """Update dashboard request"""
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    is_public: bool | None = None
    tags: list[str] | None = Field(None, max_items=10)


class DashboardResponse(BaseModel):
    """Dashboard response"""
    id: str
    name: str
    description: str | None = None
    widgets: list[WidgetResponse] = []
    is_public: bool = False
    tags: list[str] = []
    created_at: datetime
    updated_at: datetime
    share_url: str | None = None
    
    class Config:
        from_attributes = True