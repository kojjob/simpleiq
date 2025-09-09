"""
Data source schemas
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class DataSourceType(str, Enum):
    """Supported data source types"""
    GOOGLE_SHEETS = "google_sheets"
    CSV = "csv"
    REST_API = "rest_api"
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    EXCEL = "excel"


class DataSourceStatus(str, Enum):
    """Data source connection status"""
    ACTIVE = "active"
    PENDING = "pending"
    ERROR = "error"
    SYNCING = "syncing"
    DISCONNECTED = "disconnected"


class GoogleSheetsConfig(BaseModel):
    """Google Sheets specific configuration"""
    spreadsheet_id: str = Field(..., description="Google Sheets spreadsheet ID")
    sheet_name: Optional[str] = Field(None, description="Specific sheet name")
    range: Optional[str] = Field(None, description="Cell range (e.g., A1:Z100)")


class RestAPIConfig(BaseModel):
    """REST API specific configuration"""
    url: str = Field(..., description="API endpoint URL")
    method: str = Field(default="GET", pattern="^(GET|POST|PUT|DELETE)$")
    headers: Optional[Dict[str, str]] = None
    auth_type: Optional[str] = Field(None, pattern="^(none|basic|bearer|api_key)$")
    auth_credentials: Optional[Dict[str, str]] = None


class DatabaseConfig(BaseModel):
    """Database connection configuration"""
    host: str
    port: int
    database: str
    username: str
    password: str
    table: Optional[str] = None
    query: Optional[str] = None


class DataSourceCreate(BaseModel):
    """Create data source request"""
    name: str = Field(..., min_length=1, max_length=100)
    type: DataSourceType
    config: Dict[str, Any]
    description: Optional[str] = Field(None, max_length=500)
    sync_frequency: Optional[str] = Field(
        default="manual",
        pattern="^(manual|hourly|daily|weekly|realtime)$"
    )


class DataSourceUpdate(BaseModel):
    """Update data source request"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    config: Optional[Dict[str, Any]] = None
    description: Optional[str] = Field(None, max_length=500)
    sync_frequency: Optional[str] = Field(
        None,
        pattern="^(manual|hourly|daily|weekly|realtime)$"
    )


class DataSourceResponse(BaseModel):
    """Data source response"""
    id: str
    name: str
    type: DataSourceType
    status: DataSourceStatus
    description: Optional[str] = None
    sync_frequency: str = "manual"
    last_sync: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True