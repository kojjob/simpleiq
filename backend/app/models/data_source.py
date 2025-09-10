from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum


class DataSourceType(enum.Enum):
    postgresql = "postgresql"
    mysql = "mysql"
    sqlite = "sqlite"
    mongodb = "mongodb"
    bigquery = "bigquery"
    snowflake = "snowflake"
    rest_api = "rest_api"
    csv = "csv"
    google_sheets = "google_sheets"


class ConnectionStatus(enum.Enum):
    connected = "connected"
    disconnected = "disconnected"
    testing = "testing"
    error = "error"


class DataSource(Base):
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(Enum(DataSourceType), nullable=False)
    
    # Connection details
    host = Column(String(255), nullable=True)
    port = Column(Integer, nullable=True)
    database = Column(String(255), nullable=True)
    username = Column(String(255), nullable=True)
    password = Column(String(255), nullable=True)  # Should be encrypted in production
    connection_string = Column(Text, nullable=True)
    
    # Metadata
    status = Column(Enum(ConnectionStatus), default=ConnectionStatus.disconnected)
    description = Column(Text, nullable=True)
    tables_count = Column(Integer, default=0)
    size = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_connected = Column(DateTime(timezone=True), nullable=True)
    
    # User association (if needed for multi-tenancy)
    user_id = Column(Integer, nullable=True)  # Foreign key to users table
    
    def __repr__(self):
        return f"<DataSource(name='{self.name}', type='{self.type}', status='{self.status}')>"