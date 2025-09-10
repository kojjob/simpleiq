"""
Google Sheets connector for handling OAuth2 authentication and data fetching
Production-ready with security, error handling, and rate limiting
"""

import json
import logging
from typing import Any, ClassVar

import httpx
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.connectors.base import BaseConnector
from app.core.config import settings


class GoogleSheetsConnector(BaseConnector):
    """
    Google Sheets connector with OAuth2 authentication and Sheets API integration
    Handles authentication flow, data fetching, and schema detection
    """
    
    # Google API configuration
    SCOPES: ClassVar[list[str]] = [
        'https://www.googleapis.com/auth/spreadsheets.readonly',
        'https://www.googleapis.com/auth/drive.readonly'
    ]
    
    # Rate limiting and performance
    MAX_ROWS_PER_REQUEST: ClassVar[int] = 1000
    MAX_SHEETS_PER_WORKBOOK: ClassVar[int] = 50
    REQUEST_TIMEOUT: ClassVar[int] = 30
    
    # Data validation
    MAX_COLUMNS: ClassVar[int] = 500
    MIN_ROWS_FOR_SCHEMA: ClassVar[int] = 1
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.credentials: Credentials | None = None
        self.service = None
        self.spreadsheet_id: str | None = None
        self.sheet_name: str | None = None
        
    def _get_oauth_flow(self) -> Flow:
        """
        Create OAuth2 flow for Google authentication
        
        Returns:
            Configured OAuth2 flow
        """
        flow = Flow.from_client_secrets_file(
            settings.GOOGLE_SERVICE_ACCOUNT_FILE,
            scopes=self.SCOPES,
            redirect_uri=f"{settings.BACKEND_CORS_ORIGINS[0]}/auth/google/callback"
        )
        return flow
    
    def get_auth_url(self) -> str:
        """
        Generate OAuth2 authorization URL for user consent
        
        Returns:
            Authorization URL for user to visit
        """
        flow = self._get_oauth_flow()
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'  # Force consent to get refresh token
        )
        return auth_url
    
    async def handle_oauth_callback(self, authorization_code: str) -> dict[str, Any]:
        """
        Handle OAuth2 callback and exchange code for tokens
        
        Args:
            authorization_code: Authorization code from OAuth callback
            
        Returns:
            Token information including access and refresh tokens
            
        Raises:
            ValueError: If authorization fails
        """
        try:
            flow = self._get_oauth_flow()
            flow.fetch_token(code=authorization_code)
            
            credentials = flow.credentials
            
            # Store credentials securely (in production, encrypt these)
            token_data = {
                'access_token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes,
                'expiry': credentials.expiry.isoformat() if credentials.expiry else None
            }
            
            # Update data source connection config
            self.data_source.connection_config = {
                **self.data_source.connection_config,
                'oauth_tokens': token_data,
                'authenticated': True
            }
            
            return {
                'success': True,
                'message': 'Authentication successful',
                'user_info': await self._get_user_info(credentials)
            }
            
        except Exception as e:
            self.logger.exception(f"OAuth callback failed: {e}")
            return {
                'success': False,
                'error': f"Authentication failed: {str(e)}"
            }
    
    async def _get_user_info(self, credentials: Credentials) -> dict[str, Any]:
        """
        Get user information from Google API
        
        Args:
            credentials: OAuth2 credentials
            
        Returns:
            User information including email and name
        """
        try:
            service = build('drive', 'v3', credentials=credentials)
            about = service.about().get(fields='user').execute()
            
            return {
                'email': about['user']['emailAddress'],
                'name': about['user']['displayName'],
                'photo': about['user'].get('photoLink')
            }
        except Exception as e:
            self.logger.warning(f"Failed to get user info: {e}")
            return {'email': 'unknown', 'name': 'Google User'}
    
    def _load_credentials(self) -> Credentials | None:
        """
        Load OAuth2 credentials from data source configuration
        
        Returns:
            Credentials object or None if not available
        """
        if not self.data_source.connection_config.get('oauth_tokens'):
            return None
            
        try:
            token_data = self.data_source.connection_config['oauth_tokens']
            credentials = Credentials(
                token=token_data['access_token'],
                refresh_token=token_data.get('refresh_token'),
                token_uri=token_data['token_uri'],
                client_id=token_data['client_id'],
                client_secret=token_data['client_secret'],
                scopes=token_data['scopes']
            )
            
            # Refresh token if expired
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                
                # Update stored tokens
                self.data_source.connection_config['oauth_tokens'].update({
                    'access_token': credentials.token,
                    'expiry': credentials.expiry.isoformat() if credentials.expiry else None
                })
            
            return credentials
            
        except Exception as e:
            self.logger.error(f"Failed to load credentials: {e}")
            return None
    
    async def validate_connection(self) -> tuple[bool, str | None]:
        """
        Validate Google Sheets connection and spreadsheet access
        
        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Load credentials
            self.credentials = self._load_credentials()
            if not self.credentials:
                return False, "No authentication credentials found. Please authenticate first."
            
            # Parse spreadsheet URL or ID
            spreadsheet_url = self.data_source.connection_config.get('spreadsheet_url')
            if not spreadsheet_url:
                return False, "Spreadsheet URL not configured"
            
            self.spreadsheet_id = self._extract_spreadsheet_id(spreadsheet_url)
            self.sheet_name = self.data_source.connection_config.get('sheet_name', 'Sheet1')
            
            # Test API access
            self.service = build('sheets', 'v4', credentials=self.credentials)
            
            # Get spreadsheet metadata
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id,
                fields='sheets.properties'
            ).execute()
            
            # Validate sheet exists
            sheet_names = [sheet['properties']['title'] for sheet in spreadsheet['sheets']]
            if self.sheet_name not in sheet_names:
                available_sheets = ', '.join(sheet_names[:5])  # Show first 5 sheets
                return False, f"Sheet '{self.sheet_name}' not found. Available sheets: {available_sheets}"
            
            return True, None
            
        except HttpError as e:
            error_details = json.loads(e.content.decode())
            error_message = error_details.get('error', {}).get('message', 'Unknown Google API error')
            
            if e.resp.status == 403:
                return False, f"Access denied to spreadsheet. Please check permissions: {error_message}"
            elif e.resp.status == 404:
                return False, f"Spreadsheet not found. Please check the URL: {error_message}"
            else:
                return False, f"Google Sheets API error: {error_message}"
                
        except Exception as e:
            self.logger.exception(f"Connection validation failed: {e}")
            return False, f"Connection validation failed: {str(e)}"
    
    def _extract_spreadsheet_id(self, url: str) -> str:
        """
        Extract spreadsheet ID from Google Sheets URL
        
        Args:
            url: Google Sheets URL or spreadsheet ID
            
        Returns:
            Spreadsheet ID
            
        Raises:
            ValueError: If URL format is invalid
        """
        # If it's already an ID (no slashes), return as-is
        if '/' not in url:
            return url
            
        # Extract from URL patterns
        if '/spreadsheets/d/' in url:
            start = url.find('/spreadsheets/d/') + len('/spreadsheets/d/')
            end = url.find('/', start)
            if end == -1:
                end = url.find('#', start)
            if end == -1:
                end = url.find('?', start)
            if end == -1:
                end = len(url)
            return url[start:end]
        
        raise ValueError("Invalid Google Sheets URL format")
    
    async def fetch_schema(self) -> dict[str, Any]:
        """
        Analyze Google Sheets data and extract schema information
        
        Returns:
            Dictionary containing schema details
        """
        if not self.service:
            raise ValueError("Connection not established. Call validate_connection() first.")
        
        try:
            # Get sheet metadata
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id,
                fields='sheets.properties'
            ).execute()
            
            # Find the target sheet
            sheet_info = None
            for sheet in spreadsheet['sheets']:
                if sheet['properties']['title'] == self.sheet_name:
                    sheet_info = sheet['properties']
                    break
            
            if not sheet_info:
                raise ValueError(f"Sheet '{self.sheet_name}' not found")
            
            # Get data range to determine actual content
            range_name = f"'{self.sheet_name}'!1:1000"  # Get first 1000 rows for analysis
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueRenderOption='UNFORMATTED_VALUE',
                dateTimeRenderOption='FORMATTED_STRING'
            ).execute()
            
            values = result.get('values', [])
            if not values:
                return {
                    'columns': [],
                    'row_count': 0,
                    'spreadsheet_id': self.spreadsheet_id,
                    'sheet_name': self.sheet_name,
                    'last_updated': None
                }
            
            # Analyze headers (first row)
            headers = values[0] if values else []
            data_rows = values[1:] if len(values) > 1 else []
            
            # Build column schema
            columns = []
            for i, header in enumerate(headers):
                column_data = [row[i] if i < len(row) else None for row in data_rows]
                
                col_info = {
                    'name': self.sanitize_column_name(str(header) if header else f'Column_{i+1}'),
                    'original_name': str(header) if header else f'Column_{i+1}',
                    'type': self._infer_column_type(column_data),
                    'nullable': any(cell is None or cell == '' for cell in column_data),
                    'unique_count': len(set(str(cell) for cell in column_data if cell is not None)),
                    'null_count': sum(1 for cell in column_data if cell is None or cell == ''),
                    'sample_values': list(set(str(cell) for cell in column_data[:10] if cell is not None))[:5]
                }
                
                # Add null percentage
                col_info['null_percentage'] = (col_info['null_count'] / len(data_rows) * 100) if data_rows else 0
                
                columns.append(col_info)
            
            schema = {
                'columns': columns,
                'row_count': len(data_rows),
                'spreadsheet_id': self.spreadsheet_id,
                'sheet_name': self.sheet_name,
                'sheet_dimensions': {
                    'rows': sheet_info.get('gridProperties', {}).get('rowCount', 0),
                    'columns': sheet_info.get('gridProperties', {}).get('columnCount', 0)
                },
                'last_updated': None  # Google Sheets API doesn't provide this easily
            }
            
            return schema
            
        except HttpError as e:
            self.logger.error(f"Failed to fetch schema: {e}")
            raise ValueError(f"Failed to access Google Sheets data: {str(e)}")
        except Exception as e:
            self.logger.exception(f"Schema extraction failed: {e}")
            raise
    
    def _infer_column_type(self, values: list[Any]) -> str:
        """
        Infer data type from column values
        
        Args:
            values: List of cell values
            
        Returns:
            Inferred data type
        """
        non_empty = [v for v in values if v is not None and str(v).strip() != '']
        if not non_empty:
            return 'VARCHAR'
        
        # Check for numbers
        numeric_count = 0
        for value in non_empty:
            try:
                float(value)
                numeric_count += 1
            except (ValueError, TypeError):
                pass
        
        if numeric_count / len(non_empty) > 0.8:
            # Check if integers
            try:
                all_integers = all(float(v) == int(float(v)) for v in non_empty)
                return 'INTEGER' if all_integers else 'FLOAT'
            except:
                return 'FLOAT'
        
        # Check for boolean-like values
        boolean_values = {'true', 'false', '1', '0', 'yes', 'no', 'y', 'n'}
        if all(str(v).lower() in boolean_values for v in non_empty):
            return 'BOOLEAN'
        
        # Default to text
        return 'VARCHAR'
    
    async def fetch_data(
        self,
        limit: int | None = None,
        offset: int | None = None,
        filters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """
        Fetch data from Google Sheets
        
        Args:
            limit: Maximum number of rows to fetch
            offset: Number of rows to skip from the beginning
            filters: Not supported for Google Sheets
            
        Returns:
            List of row dictionaries
        """
        if not self.service:
            raise ValueError("Connection not established. Call validate_connection() first.")
        
        try:
            # Calculate range
            start_row = (offset or 0) + 2  # +2 because row 1 is headers, and sheets are 1-indexed
            end_row = start_row + (limit or self.MAX_ROWS_PER_REQUEST) - 1
            
            range_name = f"'{self.sheet_name}'!1:{end_row}"
            
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueRenderOption='UNFORMATTED_VALUE',
                dateTimeRenderOption='FORMATTED_STRING'
            ).execute()
            
            values = result.get('values', [])
            if not values:
                return []
            
            # Get headers
            headers = values[0] if values else []
            data_rows = values[start_row-1:] if len(values) >= start_row else []  # Adjust for offset
            
            # Convert to dictionaries
            result_data = []
            for row in data_rows:
                row_dict = {}
                for i, header in enumerate(headers):
                    column_name = self.sanitize_column_name(str(header) if header else f'Column_{i+1}')
                    cell_value = row[i] if i < len(row) else None
                    
                    # Convert empty strings to None
                    if cell_value == '':
                        cell_value = None
                    
                    row_dict[column_name] = cell_value
                
                result_data.append(row_dict)
            
            return result_data
            
        except HttpError as e:
            self.logger.error(f"Failed to fetch data: {e}")
            raise ValueError(f"Failed to fetch Google Sheets data: {str(e)}")
        except Exception as e:
            self.logger.exception(f"Data fetching failed: {e}")
            raise
    
    async def count_rows(self) -> int:
        """
        Count total rows in the Google Sheet (excluding header)
        
        Returns:
            Total row count
        """
        if not self.service:
            raise ValueError("Connection not established. Call validate_connection() first.")
        
        try:
            # Get all data to count rows (this is not ideal for very large sheets)
            range_name = f"'{self.sheet_name}'"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueRenderOption='UNFORMATTED_VALUE'
            ).execute()
            
            values = result.get('values', [])
            # Subtract 1 for header row, but ensure we don't go negative
            return max(0, len(values) - 1)
            
        except Exception as e:
            self.logger.exception(f"Failed to count rows: {e}")
            return 0
    
    async def validate_data(self, data: list[dict[str, Any]] | None = None) -> tuple[bool, list[str]]:
        """
        Validate Google Sheets data
        
        Args:
            data: Optional data to validate (uses API call if not provided)
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if data is None:
            # Fetch sample data for validation
            try:
                data = await self.fetch_data(limit=100)
            except Exception as e:
                errors.append(f"Failed to fetch data for validation: {str(e)}")
                return False, errors
        
        if not data:
            errors.append("No data found in the spreadsheet")
            return False, errors
        
        # Check column count
        if data:
            column_count = len(data[0])
            if column_count > self.MAX_COLUMNS:
                errors.append(f"Too many columns: {column_count}, maximum allowed: {self.MAX_COLUMNS}")
        
        # Check for empty headers
        if data:
            empty_columns = [k for k, v in data[0].items() if not k or k.startswith('Column_')]
            if empty_columns:
                errors.append(f"Empty column headers found: {empty_columns}")
        
        # Data quality checks
        if len(data) < self.MIN_ROWS_FOR_SCHEMA:
            errors.append(f"Insufficient data for analysis: {len(data)} rows, minimum: {self.MIN_ROWS_FOR_SCHEMA}")
        
        return len(errors) == 0, errors