"""
Dashboard and widget schemas
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

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
    config: Optional[Dict[str, Any]] = Field(None, description="Chart configuration")
    refresh_interval: Optional[int] = Field(None, ge=0, description="Auto-refresh in seconds")


class WidgetUpdate(BaseModel):
    """Update widget request"""
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[ChartType] = None
    query: Optional[str] = Field(None, min_length=1, max_length=500)
    position: Optional[WidgetPosition] = None
    config: Optional[Dict[str, Any]] = None
    refresh_interval: Optional[int] = Field(None, ge=0)


class WidgetResponse(BaseModel):
    """Widget response"""
    id: str
    title: str
    type: ChartType
    query: str
    position: WidgetPosition
    config: Optional[Dict[str, Any]] = None
    refresh_interval: Optional[int] = None
    last_updated: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DashboardCreate(BaseModel):
    """Create dashboard request"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_public: bool = Field(default=False, description="Make dashboard publicly accessible")
    tags: Optional[List[str]] = Field(None, max_items=10)


class DashboardUpdate(BaseModel):
    """Update dashboard request"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_public: Optional[bool] = None
    tags: Optional[List[str]] = Field(None, max_items=10)


class DashboardResponse(BaseModel):
    """Dashboard response"""
    id: str
    name: str
    description: Optional[str] = None
    widgets: List[WidgetResponse] = []
    is_public: bool = False
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime
    share_url: Optional[str] = None
    
    class Config:
        from_attributes = True