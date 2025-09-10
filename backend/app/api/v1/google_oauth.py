"""
Google OAuth2 API endpoints for Google Sheets integration
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.connectors.google_sheets_connector import GoogleSheetsConnector
from app.core.auth import get_current_user
from app.core.database import get_async_db
from app.models.data_source import DataSource, DataSourceType
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/google", tags=["google-oauth"])


class GoogleAuthUrlResponse(BaseModel):
    """Response model for Google OAuth authorization URL"""
    auth_url: str
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "auth_url": "https://accounts.google.com/o/oauth2/auth?client_id=...",
                "message": "Visit this URL to authorize SimpleIQ to access your Google Sheets"
            }
        }


class OAuthCallbackRequest(BaseModel):
    """Request model for OAuth callback"""
    authorization_code: str
    data_source_id: str

    class Config:
        json_schema_extra = {
            "example": {
                "authorization_code": "4/0AdQt8qh...",
                "data_source_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }


class OAuthCallbackResponse(BaseModel):
    """Response model for OAuth callback"""
    success: bool
    message: str
    user_info: dict[str, Any] | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Google Sheets authentication successful",
                "user_info": {
                    "email": "user@example.com",
                    "name": "John Doe",
                    "photo": "https://lh3.googleusercontent.com/..."
                }
            }
        }


class SheetsConnectionRequest(BaseModel):
    """Request model for creating Google Sheets connection"""
    name: str
    description: str | None = None
    spreadsheet_url: str
    sheet_name: str = "Sheet1"

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Sales Data Q4",
                "description": "Q4 sales metrics from Google Sheets",
                "spreadsheet_url": "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit#gid=0",
                "sheet_name": "Sheet1"
            }
        }


class SheetsConnectionResponse(BaseModel):
    """Response model for Google Sheets connection"""
    data_source_id: str
    auth_url: str
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "data_source_id": "550e8400-e29b-41d4-a716-446655440000",
                "auth_url": "https://accounts.google.com/o/oauth2/auth?client_id=...",
                "message": "Data source created. Please visit the auth_url to complete authorization."
            }
        }


@router.post("/sheets/connect", response_model=SheetsConnectionResponse, status_code=status.HTTP_201_CREATED)
async def create_sheets_connection(
    request: SheetsConnectionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Create a new Google Sheets data source and initiate OAuth flow
    
    This endpoint creates a data source record and returns the OAuth URL
    for user authentication. The actual connection is completed when the
    user visits the auth URL and the callback is processed.
    """
    try:
        # Create data source record
        data_source = DataSource(
            user_id=str(current_user.id),
            name=request.name,
            description=request.description,
            type=DataSourceType.google_sheets,
            connection_config={
                "spreadsheet_url": request.spreadsheet_url,
                "sheet_name": request.sheet_name,
                "authenticated": False
            }
        )
        
        db.add(data_source)
        await db.commit()
        await db.refresh(data_source)
        
        # Create connector to get auth URL
        connector = GoogleSheetsConnector(data_source, db)
        auth_url = connector.get_auth_url()
        
        logger.info(f"Created Google Sheets data source {data_source.id} for user {current_user.id}")
        
        return SheetsConnectionResponse(
            data_source_id=str(data_source.id),
            auth_url=auth_url,
            message="Data source created. Please visit the auth_url to complete authorization."
        )
        
    except Exception as e:
        logger.exception(f"Failed to create Google Sheets connection for user {current_user.id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create Google Sheets connection"
        )


@router.post("/oauth/callback", response_model=OAuthCallbackResponse)
async def handle_oauth_callback(
    request: OAuthCallbackRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Handle OAuth2 callback from Google
    
    This endpoint processes the authorization code from Google's OAuth flow,
    exchanges it for tokens, and stores the credentials for the data source.
    """
    try:
        # Get the data source
        data_source = await db.get(DataSource, request.data_source_id)
        if not data_source:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data source not found"
            )
        
        # Verify ownership
        if data_source.user_id != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to data source"
            )
        
        # Verify it's a Google Sheets source
        if data_source.type != DataSourceType.google_sheets:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data source is not a Google Sheets connection"
            )
        
        # Handle OAuth callback
        connector = GoogleSheetsConnector(data_source, db)
        result = await connector.handle_oauth_callback(request.authorization_code)
        
        if result["success"]:
            # Update data source in database
            await db.commit()
            await db.refresh(data_source)
            
            logger.info(f"OAuth callback successful for data source {data_source.id}")
            
            return OAuthCallbackResponse(
                success=True,
                message="Google Sheets authentication successful",
                user_info=result.get("user_info")
            )
        else:
            logger.error(f"OAuth callback failed for data source {data_source.id}: {result.get('error')}")
            return OAuthCallbackResponse(
                success=False,
                message=result.get("error", "Authentication failed"),
                user_info=None
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"OAuth callback processing failed for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process OAuth callback"
        )


@router.get("/auth-url/{data_source_id}", response_model=GoogleAuthUrlResponse)
async def get_auth_url(
    data_source_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get OAuth authorization URL for existing Google Sheets data source
    
    Use this endpoint to regenerate the auth URL if the user needs to
    re-authenticate or complete the initial authentication flow.
    """
    try:
        # Get the data source
        data_source = await db.get(DataSource, data_source_id)
        if not data_source:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data source not found"
            )
        
        # Verify ownership
        if data_source.user_id != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to data source"
            )
        
        # Verify it's a Google Sheets source
        if data_source.type != DataSourceType.google_sheets:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data source is not a Google Sheets connection"
            )
        
        # Generate auth URL
        connector = GoogleSheetsConnector(data_source, db)
        auth_url = connector.get_auth_url()
        
        return GoogleAuthUrlResponse(
            auth_url=auth_url,
            message="Visit this URL to authorize SimpleIQ to access your Google Sheets"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to generate auth URL for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate authorization URL"
        )


@router.post("/sheets/{data_source_id}/test-connection")
async def test_sheets_connection(
    data_source_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Test Google Sheets connection and return basic information
    
    This endpoint validates the OAuth credentials and spreadsheet access,
    returning basic information about the sheet structure.
    """
    try:
        # Get the data source
        data_source = await db.get(DataSource, data_source_id)
        if not data_source:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data source not found"
            )
        
        # Verify ownership
        if data_source.user_id != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to data source"
            )
        
        # Verify it's a Google Sheets source
        if data_source.type != DataSourceType.google_sheets:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data source is not a Google Sheets connection"
            )
        
        # Test connection
        connector = GoogleSheetsConnector(data_source, db)
        is_valid, error_message = await connector.validate_connection()
        
        if is_valid:
            # Get basic schema information
            try:
                schema = await connector.fetch_schema()
                row_count = await connector.count_rows()
                
                return {
                    "success": True,
                    "message": "Connection successful",
                    "sheet_info": {
                        "spreadsheet_id": schema.get("spreadsheet_id"),
                        "sheet_name": schema.get("sheet_name"),
                        "columns": len(schema.get("columns", [])),
                        "rows": row_count,
                        "sample_columns": [col["name"] for col in schema.get("columns", [])[:5]]
                    }
                }
            except Exception as e:
                logger.warning(f"Connection valid but failed to get schema: {e}")
                return {
                    "success": True,
                    "message": "Connection successful but failed to analyze sheet structure",
                    "sheet_info": None
                }
        else:
            return {
                "success": False,
                "message": error_message or "Connection failed",
                "sheet_info": None
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Connection test failed for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to test connection"
        )


@router.get("/sheets/{data_source_id}/preview")
async def preview_sheets_data(
    data_source_id: str,
    limit: int = Query(default=10, ge=1, le=100, description="Number of rows to preview"),
    offset: int = Query(default=0, ge=0, description="Number of rows to skip"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Preview data from Google Sheets data source
    
    Returns a sample of data from the connected Google Sheets for preview purposes.
    Includes both schema information and actual data rows.
    """
    try:
        # Get the data source
        data_source = await db.get(DataSource, data_source_id)
        if not data_source:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data source not found"
            )
        
        # Verify ownership
        if data_source.user_id != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to data source"
            )
        
        # Verify it's a Google Sheets source
        if data_source.type != DataSourceType.google_sheets:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data source is not a Google Sheets connection"
            )
        
        # Create connector and validate connection
        connector = GoogleSheetsConnector(data_source, db)
        is_valid, error_message = await connector.validate_connection()
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unable to connect to data source: {error_message}"
            )
        
        # Get schema and data
        schema = await connector.fetch_schema()
        data_rows = await connector.fetch_data(limit=limit, offset=offset)
        
        return {
            "data_source_id": data_source_id,
            "schema": {
                "columns": schema.get("columns", []),
                "total_rows": schema.get("row_count", 0),
                "spreadsheet_id": schema.get("spreadsheet_id"),
                "sheet_name": schema.get("sheet_name")
            },
            "data": {
                "rows": data_rows,
                "count": len(data_rows),
                "limit": limit,
                "offset": offset,
                "has_more": len(data_rows) == limit
            },
            "message": f"Preview showing {len(data_rows)} rows (limit: {limit}, offset: {offset})"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Data preview failed for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to preview data"
        )


@router.get("/sheets/{data_source_id}/schema")
async def get_sheets_schema(
    data_source_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get detailed schema information for Google Sheets data source
    
    Returns comprehensive schema information including column types, 
    sample values, and data quality metrics.
    """
    try:
        # Get the data source
        data_source = await db.get(DataSource, data_source_id)
        if not data_source:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data source not found"
            )
        
        # Verify ownership
        if data_source.user_id != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to data source"
            )
        
        # Verify it's a Google Sheets source
        if data_source.type != DataSourceType.google_sheets:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data source is not a Google Sheets connection"
            )
        
        # Create connector and validate connection
        connector = GoogleSheetsConnector(data_source, db)
        is_valid, error_message = await connector.validate_connection()
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unable to connect to data source: {error_message}"
            )
        
        # Get detailed schema information
        schema = await connector.fetch_schema()
        
        return {
            "data_source_id": data_source_id,
            "schema": schema,
            "message": "Schema information retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Schema retrieval failed for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve schema"
        )


@router.get("/callback")
async def oauth_callback_redirect(
    code: str = Query(..., description="Authorization code from Google"),
    state: str = Query(None, description="State parameter for CSRF protection")
):
    """
    OAuth callback endpoint for browser redirects from Google
    
    This is the endpoint that Google redirects to after user authorization.
    In a real application, this would typically redirect to a frontend page
    that handles the authorization code.
    """
    # In production, this would redirect to a frontend page with the code
    # For now, return instructions for the user
    return {
        "message": "Authorization successful! Please copy the authorization code below and use it with the /google/oauth/callback endpoint.",
        "authorization_code": code,
        "instructions": [
            "1. Copy the authorization code above",
            "2. Use the POST /api/v1/google/oauth/callback endpoint",
            "3. Include the authorization code and your data source ID",
            "4. Your Google Sheets connection will be activated"
        ]
    }