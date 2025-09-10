from datetime import datetime

from pydantic import BaseModel, Field

from app.models.data_source import ConnectionStatus, DataSourceType


class DataSourceBase(BaseModel):
    name: str = Field(..., description="Name of the data source")
    type: DataSourceType = Field(..., description="Type of data source")
    host: str | None = Field(None, description="Database host")
    port: int | None = Field(None, description="Database port")
    database: str | None = Field(None, description="Database name")
    username: str | None = Field(None, description="Username for authentication")
    connection_string: str | None = Field(None, description="Connection string or URL")
    description: str | None = Field(None, description="Description of the data source")


class DataSourceCreate(DataSourceBase):
    password: str | None = Field(None, description="Password for authentication")


class DataSourceUpdate(BaseModel):
    name: str | None = None
    type: DataSourceType | None = None
    host: str | None = None
    port: int | None = None
    database: str | None = None
    username: str | None = None
    password: str | None = None
    connection_string: str | None = None
    description: str | None = None


class TableInfo(BaseModel):
    name: str
    rows: int
    size: str


class DataSourceResponse(DataSourceBase):
    id: int
    status: ConnectionStatus
    tables_count: int = 0
    size: str | None = None
    created_at: datetime
    updated_at: datetime
    last_connected: datetime | None = None
    user_id: int | None = None

    class Config:
        from_attributes = True


class DataSourceWithTables(DataSourceResponse):
    tables: list[TableInfo] = []


class ConnectionTestRequest(BaseModel):
    data_source_id: int


class ConnectionTestResponse(BaseModel):
    success: bool
    message: str
    tables_count: int | None = None
    size: str | None = None
    tables: list[TableInfo] = []


class DataSourceStats(BaseModel):
    total: int
    connected: int
    errors: int
    total_tables: int