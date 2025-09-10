"""
Data source schemas
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class DataSourceType(str, Enum):
    """Supported data source types"""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    MONGODB = "mongodb"
    BIGQUERY = "bigquery"
    SNOWFLAKE = "snowflake"
    REST_API = "rest_api"
    CSV = "csv"
    GOOGLE_SHEETS = "google_sheets"


class DataSourceStatus(str, Enum):
    """Data source connection status"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    TESTING = "testing"
    ERROR = "error"


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


class TableInfo(BaseModel):
    """Table information"""
    name: str
    rows: int
    size: str


class ConnectionTestResponse(BaseModel):
    """Connection test response"""
    success: bool
    message: str
    tables_count: Optional[int] = None
    size: Optional[str] = None
    tables: Optional[list[TableInfo]] = None


class DataSourceCreate(BaseModel):
    """Create data source request"""
    name: str = Field(..., min_length=1, max_length=100)
    type: DataSourceType
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    connection_string: Optional[str] = None
    description: Optional[str] = Field(None, max_length=500)


class DataSourceUpdate(BaseModel):
    """Update data source request"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    connection_string: Optional[str] = None
    description: Optional[str] = Field(None, max_length=500)


class DataSourceResponse(BaseModel):
    """Data source response"""
    id: str
    name: str
    type: DataSourceType
    status: DataSourceStatus
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    connection_string: Optional[str] = None
    description: Optional[str] = None
    tables_count: Optional[int] = None
    size: Optional[str] = None
    last_connected: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    tables: Optional[list[TableInfo]] = None
    
    class Config:
        from_attributes = True