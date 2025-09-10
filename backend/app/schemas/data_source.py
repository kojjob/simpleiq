from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.data_source import DataSourceType, ConnectionStatus


class DataSourceBase(BaseModel):
    name: str = Field(..., description="Name of the data source")
    type: DataSourceType = Field(..., description="Type of data source")
    host: Optional[str] = Field(None, description="Database host")
    port: Optional[int] = Field(None, description="Database port")
    database: Optional[str] = Field(None, description="Database name")
    username: Optional[str] = Field(None, description="Username for authentication")
    connection_string: Optional[str] = Field(None, description="Connection string or URL")
    description: Optional[str] = Field(None, description="Description of the data source")


class DataSourceCreate(DataSourceBase):
    password: Optional[str] = Field(None, description="Password for authentication")


class DataSourceUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[DataSourceType] = None
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    connection_string: Optional[str] = None
    description: Optional[str] = None


class TableInfo(BaseModel):
    name: str
    rows: int
    size: str


class DataSourceResponse(DataSourceBase):
    id: int
    status: ConnectionStatus
    tables_count: int = 0
    size: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_connected: Optional[datetime] = None
    user_id: Optional[int] = None

    class Config:
        from_attributes = True


class DataSourceWithTables(DataSourceResponse):
    tables: List[TableInfo] = []


class ConnectionTestRequest(BaseModel):
    data_source_id: int


class ConnectionTestResponse(BaseModel):
    success: bool
    message: str
    tables_count: Optional[int] = None
    size: Optional[str] = None
    tables: List[TableInfo] = []


class DataSourceStats(BaseModel):
    total: int
    connected: int
    errors: int
    total_tables: int