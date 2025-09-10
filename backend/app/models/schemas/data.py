"""
Data source schemas
"""

from datetime import datetime
from enum import Enum

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
    sheet_name: str | None = Field(None, description="Specific sheet name")
    range: str | None = Field(None, description="Cell range (e.g., A1:Z100)")


class RestAPIConfig(BaseModel):
    """REST API specific configuration"""
    url: str = Field(..., description="API endpoint URL")
    method: str = Field(default="GET", pattern="^(GET|POST|PUT|DELETE)$")
    headers: dict[str, str] | None = None
    auth_type: str | None = Field(None, pattern="^(none|basic|bearer|api_key)$")
    auth_credentials: dict[str, str] | None = None


class DatabaseConfig(BaseModel):
    """Database connection configuration"""
    host: str
    port: int
    database: str
    username: str
    password: str
    table: str | None = None
    query: str | None = None


class TableInfo(BaseModel):
    """Table information"""
    name: str
    rows: int
    size: str


class ConnectionTestResponse(BaseModel):
    """Connection test response"""
    success: bool
    message: str
    tables_count: int | None = None
    size: str | None = None
    tables: list[TableInfo] | None = None


class DataSourceCreate(BaseModel):
    """Create data source request"""
    name: str = Field(..., min_length=1, max_length=100)
    type: DataSourceType
    host: str | None = None
    port: int | None = None
    database: str | None = None
    username: str | None = None
    password: str | None = None
    connection_string: str | None = None
    description: str | None = Field(None, max_length=500)


class DataSourceUpdate(BaseModel):
    """Update data source request"""
    name: str | None = Field(None, min_length=1, max_length=100)
    host: str | None = None
    port: int | None = None
    database: str | None = None
    username: str | None = None
    password: str | None = None
    connection_string: str | None = None
    description: str | None = Field(None, max_length=500)


class DataSourceResponse(BaseModel):
    """Data source response"""
    id: str
    name: str
    type: DataSourceType
    status: DataSourceStatus
    host: str | None = None
    port: int | None = None
    database: str | None = None
    username: str | None = None
    connection_string: str | None = None
    description: str | None = None
    tables_count: int | None = None
    size: str | None = None
    last_connected: datetime | None = None
    created_at: datetime
    updated_at: datetime | None = None
    tables: list[TableInfo] | None = None
    
    class Config:
        from_attributes = True