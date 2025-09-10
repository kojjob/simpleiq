import sqlite3
from datetime import datetime
from typing import Any

import psycopg2
import pymysql
import requests
from sqlalchemy.orm import Session

from app.models.data_source import ConnectionStatus, DataSource, DataSourceType
from app.models.schemas.data import (
    ConnectionTestResponse,
    DataSourceCreate,
    DataSourceUpdate,
    TableInfo,
)


class DataSourceService:
    def __init__(self, db: Session):
        self.db = db

    def get_data_sources(self, skip: int = 0, limit: int = 100) -> list[DataSource]:
        """Get all data sources with pagination"""
        return self.db.query(DataSource).offset(skip).limit(limit).all()

    def get_data_source(self, data_source_id: int) -> DataSource | None:
        """Get a specific data source by ID"""
        return self.db.query(DataSource).filter(DataSource.id == data_source_id).first()

    def create_data_source(self, data_source: DataSourceCreate) -> DataSource:
        """Create a new data source"""
        # Convert the Pydantic model to a dict and map fields
        data = data_source.dict()
        
        # Map the string type to enum
        if "type" in data:
            data["type"] = DataSourceType(data["type"])
        
        db_data_source = DataSource(**data)
        self.db.add(db_data_source)
        self.db.commit()
        self.db.refresh(db_data_source)
        return db_data_source

    def update_data_source(self, data_source_id: int, data_source: DataSourceUpdate) -> DataSource | None:
        """Update an existing data source"""
        db_data_source = self.get_data_source(data_source_id)
        if not db_data_source:
            return None
        
        update_data = data_source.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_data_source, field, value)
        
        self.db.commit()
        self.db.refresh(db_data_source)
        return db_data_source

    def delete_data_source(self, data_source_id: int) -> bool:
        """Delete a data source"""
        db_data_source = self.get_data_source(data_source_id)
        if not db_data_source:
            return False
        
        self.db.delete(db_data_source)
        self.db.commit()
        return True

    def test_connection(self, data_source_id: int) -> ConnectionTestResponse:
        """Test connection to a data source"""
        data_source = self.get_data_source(data_source_id)
        if not data_source:
            return ConnectionTestResponse(
                success=False,
                message="Data source not found"
            )

        try:
            result = self._test_connection_by_type(data_source)
            
            # Update data source status and metadata
            if result.success:
                data_source.status = ConnectionStatus.connected
                data_source.last_connected = datetime.utcnow()
                data_source.tables_count = result.tables_count or 0
                data_source.size = result.size
            else:
                data_source.status = ConnectionStatus.error
            
            self.db.commit()
            self.db.refresh(data_source)
            
            return result
        except Exception as e:
            data_source.status = ConnectionStatus.error
            self.db.commit()
            return ConnectionTestResponse(
                success=False,
                message=f"Connection test failed: {e!s}"
            )

    def _test_connection_by_type(self, data_source: DataSource) -> ConnectionTestResponse:
        """Test connection based on data source type"""
        if data_source.type == DataSourceType.postgresql:
            return self._test_postgresql(data_source)
        if data_source.type == DataSourceType.mysql:
            return self._test_mysql(data_source)
        if data_source.type == DataSourceType.sqlite:
            return self._test_sqlite(data_source)
        if data_source.type == DataSourceType.rest_api:
            return self._test_rest_api(data_source)
        if data_source.type in [DataSourceType.bigquery, DataSourceType.snowflake]:
            return self._test_cloud_database(data_source)
        if data_source.type == DataSourceType.google_sheets:
            return self._test_google_sheets(data_source)
        return ConnectionTestResponse(
            success=False,
            message=f"Connection testing not implemented for {data_source.type}"
        )

    def _test_postgresql(self, data_source: DataSource) -> ConnectionTestResponse:
        """Test PostgreSQL connection"""
        try:
            conn = psycopg2.connect(
                host=data_source.host,
                port=data_source.port,
                database=data_source.database,
                user=data_source.username,
                password=data_source.password,
                connect_timeout=10
            )
            
            cursor = conn.cursor()
            
            # Get table count
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            """)
            tables_count = cursor.fetchone()[0]
            
            # Get database size
            cursor.execute(f"SELECT pg_size_pretty(pg_database_size('{data_source.database}'))")
            size = cursor.fetchone()[0]
            
            # Get table information
            cursor.execute("""
                SELECT 
                    t.table_name,
                    COALESCE(s.n_tup_ins + s.n_tup_upd + s.n_tup_del, 0) as estimated_rows,
                    pg_size_pretty(pg_total_relation_size(c.oid)) as size
                FROM information_schema.tables t
                LEFT JOIN pg_class c ON c.relname = t.table_name
                LEFT JOIN pg_stat_user_tables s ON s.relname = t.table_name
                WHERE t.table_schema = 'public' 
                AND t.table_type = 'BASE TABLE'
                ORDER BY t.table_name
                LIMIT 10
            """)
            
            tables = []
            for row in cursor.fetchall():
                tables.append(TableInfo(
                    name=row[0],
                    rows=int(row[1]) if row[1] else 0,
                    size=row[2] if row[2] else "0 bytes"
                ))
            
            cursor.close()
            conn.close()
            
            return ConnectionTestResponse(
                success=True,
                message="Successfully connected to PostgreSQL",
                tables_count=tables_count,
                size=size,
                tables=tables
            )
        except Exception as e:
            return ConnectionTestResponse(
                success=False,
                message=f"PostgreSQL connection failed: {e!s}"
            )

    def _test_mysql(self, data_source: DataSource) -> ConnectionTestResponse:
        """Test MySQL connection"""
        try:
            conn = pymysql.connect(
                host=data_source.host,
                port=data_source.port,
                user=data_source.username,
                password=data_source.password,
                database=data_source.database,
                connect_timeout=10
            )
            
            cursor = conn.cursor()
            
            # Get table count
            cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = %s", 
                          (data_source.database,))
            tables_count = cursor.fetchone()[0]
            
            # Get database size
            cursor.execute("""
                SELECT ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) as size_mb
                FROM information_schema.tables 
                WHERE table_schema = %s
            """, (data_source.database,))
            size_mb = cursor.fetchone()[0] or 0
            size = f"{size_mb} MB"
            
            # Get table information
            cursor.execute("""
                SELECT 
                    table_name,
                    table_rows,
                    ROUND((data_length + index_length) / 1024 / 1024, 2) as size_mb
                FROM information_schema.tables
                WHERE table_schema = %s
                ORDER BY table_name
                LIMIT 10
            """, (data_source.database,))
            
            tables = []
            for row in cursor.fetchall():
                tables.append(TableInfo(
                    name=row[0],
                    rows=int(row[1]) if row[1] else 0,
                    size=f"{row[2]} MB" if row[2] else "0 MB"
                ))
            
            cursor.close()
            conn.close()
            
            return ConnectionTestResponse(
                success=True,
                message="Successfully connected to MySQL",
                tables_count=tables_count,
                size=size,
                tables=tables
            )
        except Exception as e:
            return ConnectionTestResponse(
                success=False,
                message=f"MySQL connection failed: {e!s}"
            )

    def _test_sqlite(self, data_source: DataSource) -> ConnectionTestResponse:
        """Test SQLite connection"""
        try:
            db_path = data_source.connection_string or data_source.database
            conn = sqlite3.connect(db_path, timeout=10)
            cursor = conn.cursor()
            
            # Get table count
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            tables_count = cursor.fetchone()[0]
            
            # Get table information
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
                LIMIT 10
            """)
            
            tables = []
            for row in cursor.fetchall():
                table_name = row[0]
                cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
                row_count = cursor.fetchone()[0]
                tables.append(TableInfo(
                    name=table_name,
                    rows=row_count,
                    size="N/A"  # SQLite doesn't easily provide table sizes
                ))
            
            cursor.close()
            conn.close()
            
            return ConnectionTestResponse(
                success=True,
                message="Successfully connected to SQLite",
                tables_count=tables_count,
                size="N/A",
                tables=tables
            )
        except Exception as e:
            return ConnectionTestResponse(
                success=False,
                message=f"SQLite connection failed: {e!s}"
            )

    def _test_rest_api(self, data_source: DataSource) -> ConnectionTestResponse:
        """Test REST API connection"""
        try:
            url = data_source.connection_string
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return ConnectionTestResponse(
                    success=True,
                    message=f"Successfully connected to REST API (Status: {response.status_code})",
                    tables_count=1,
                    size="N/A"
                )
            return ConnectionTestResponse(
                success=False,
                message=f"REST API returned status code: {response.status_code}"
            )
        except Exception as e:
            return ConnectionTestResponse(
                success=False,
                message=f"REST API connection failed: {e!s}"
            )

    def _test_cloud_database(self, data_source: DataSource) -> ConnectionTestResponse:
        """Test cloud database connection (BigQuery, Snowflake)"""
        # This would require specific SDKs and authentication
        return ConnectionTestResponse(
            success=True,  # Mock success for demo
            message=f"Successfully connected to {data_source.type.value} (Mock)",
            tables_count=10,
            size="1.5 GB"
        )

    def _test_google_sheets(self, data_source: DataSource) -> ConnectionTestResponse:
        """Test Google Sheets connection"""
        try:
            # This would require Google Sheets API authentication
            # For now, just check if the URL is valid
            url = data_source.connection_string
            if url and "docs.google.com/spreadsheets" in url:
                return ConnectionTestResponse(
                    success=True,
                    message="Successfully connected to Google Sheets (Mock)",
                    tables_count=3,
                    size="2.1 MB",
                    tables=[
                        TableInfo(name="Sheet1", rows=100, size="1.2 MB"),
                        TableInfo(name="Sheet2", rows=250, size="0.7 MB"),
                        TableInfo(name="Sheet3", rows=75, size="0.2 MB")
                    ]
                )
            return ConnectionTestResponse(
                success=False,
                message="Invalid Google Sheets URL"
            )
        except Exception as e:
            return ConnectionTestResponse(
                success=False,
                message=f"Google Sheets connection failed: {e!s}"
            )

    def get_stats(self) -> dict[str, Any]:
        """Get data source statistics"""
        total = self.db.query(DataSource).count()
        connected = self.db.query(DataSource).filter(DataSource.status == ConnectionStatus.connected).count()
        errors = self.db.query(DataSource).filter(DataSource.status == ConnectionStatus.error).count()
        
        # Get total tables count
        total_tables = self.db.query(DataSource.tables_count).filter(DataSource.tables_count.isnot(None)).all()
        total_tables_sum = sum([count[0] for count in total_tables if count[0]])
        
        return {
            "total": total,
            "connected": connected,
            "errors": errors,
            "total_tables": total_tables_sum
        }