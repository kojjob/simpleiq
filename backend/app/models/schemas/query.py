"""
Query-related schemas
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Natural language query request"""
    query: str = Field(..., min_length=1, max_length=500, description="Natural language query")
    data_source_id: Optional[str] = Field(None, description="Specific data source to query")
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum rows to return")
    timeout_seconds: int = Field(default=30, ge=1, le=300, description="Query timeout")
    include_insights: bool = Field(default=True, description="Include AI-generated insights")


class QueryResult(BaseModel):
    """Query execution result"""
    columns: List[str]
    rows: List[List[Any]]
    row_count: int
    truncated: bool = False


class QueryResponse(BaseModel):
    """Query execution response"""
    success: bool
    query_id: str
    original_query: str
    sql_generated: Optional[str] = None
    results: Optional[QueryResult] = None
    execution_time_ms: int
    insights: Optional[List[str]] = None
    error: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "query_id": "q_123abc",
                "original_query": "Show me sales by category",
                "sql_generated": "SELECT category, SUM(sales) FROM data GROUP BY category",
                "results": {
                    "columns": ["category", "total_sales"],
                    "rows": [["Electronics", 50000], ["Clothing", 30000]],
                    "row_count": 2,
                    "truncated": False
                },
                "execution_time_ms": 245,
                "insights": ["Electronics is your top category with 62.5% of total sales"]
            }
        }


class QueryHistory(BaseModel):
    """Query history item"""
    id: str
    query: str
    executed_at: datetime
    execution_time_ms: int
    success: bool
    data_source_id: Optional[str] = None
    error: Optional[str] = None
    
    class Config:
        from_attributes = True


class QueryExplanation(BaseModel):
    """Query explanation response"""
    query: str
    explanation: str
    data_sources: List[str]
    estimated_execution_time_ms: int
    potential_insights: List[str]
    sql_preview: Optional[str] = None