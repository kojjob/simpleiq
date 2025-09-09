"""
Natural language query API endpoints
"""

from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.schemas.query import (
    QueryRequest,
    QueryResponse,
    QueryHistory,
    QueryResult,
)

router = APIRouter()


@router.post("/execute", response_model=QueryResponse)
async def execute_query(
    query: QueryRequest,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Execute a natural language query
    """
    # Validate query
    if not query.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty",
        )
    
    # Process natural language query (placeholder)
    # In production, this would:
    # 1. Send to LLM for NL to SQL conversion
    # 2. Execute SQL against the data source
    # 3. Format and return results
    
    return {
        "success": True,
        "query_id": "query-123",
        "original_query": query.query,
        "sql_generated": "SELECT category, SUM(sales) FROM sales_data WHERE date >= '2024-01-01' GROUP BY category",
        "results": {
            "columns": ["category", "total_sales"],
            "rows": [
                ["Electronics", 125000],
                ["Clothing", 87500],
                ["Food", 63200],
            ],
            "row_count": 3,
        },
        "execution_time_ms": 245,
        "insights": [
            "Electronics is your top performing category with $125,000 in sales",
            "Total sales across all categories: $275,700",
            "Consider increasing inventory for Electronics",
        ],
    }


@router.get("/history", response_model=List[QueryHistory])
async def get_query_history(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 50,
) -> Any:
    """
    Get query history for the current user
    """
    # Return query history (placeholder)
    return [
        {
            "id": "query-123",
            "query": "Show me sales by category this year",
            "executed_at": "2024-01-15T10:30:00Z",
            "execution_time_ms": 245,
            "success": True,
            "data_source_id": "source-1",
        },
        {
            "id": "query-122",
            "query": "What are my top customers?",
            "executed_at": "2024-01-15T09:15:00Z",
            "execution_time_ms": 189,
            "success": True,
            "data_source_id": "source-1",
        },
    ]


@router.get("/suggestions")
async def get_query_suggestions(
    context: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get suggested queries based on context
    """
    # Return contextual suggestions (placeholder)
    suggestions = [
        "Show me total sales this month",
        "What are my top selling products?",
        "Compare sales between this year and last year",
        "Show me customer growth over time",
        "What's my average order value?",
        "Which products have the highest profit margin?",
        "Show me sales by region",
        "What are the busiest days of the week?",
    ]
    
    return {"suggestions": suggestions}


@router.post("/explain")
async def explain_query(
    query: QueryRequest,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Explain what a query will do without executing it
    """
    # Explain query intent (placeholder)
    return {
        "query": query.query,
        "explanation": "This query will analyze your sales data by category for the current year, "
                      "grouping all transactions by their category and calculating the total sales amount for each.",
        "data_sources": ["Sales Data (Google Sheets)"],
        "estimated_execution_time_ms": 200,
        "potential_insights": [
            "Category performance comparison",
            "Revenue distribution analysis",
            "Top performing categories identification",
        ],
    }