"""
CSV connector for handling CSV file uploads and processing
Production-ready with security, validation, and performance optimizations
"""

import hashlib
import io
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import chardet
import magic
import pandas as pd

from app.connectors.base import BaseConnector
from app.models.data_source import ConnectionStatus, ProcessingStatus


class CSVConnector(BaseConnector):
    """
    CSV file connector with comprehensive validation and processing
    Supports large files, encoding detection, and data profiling
    """
    
    # Security constants
    MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
    ALLOWED_MIME_TYPES = ['text/csv', 'text/plain', 'application/csv']
    CHUNK_SIZE = 10000  # Rows to process at a time for large files
    
    # Validation constants
    MIN_ROWS = 1
    MAX_COLUMNS = 1000
    MAX_COLUMN_NAME_LENGTH = 255
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_path = self.data_source.file_path
        self.df: Optional[pd.DataFrame] = None
        self._file_hash: Optional[str] = None
        self._encoding: Optional[str] = None
    
    async def validate_file_security(self, file_content: bytes) -> Tuple[bool, Optional[str]]:
        """
        Validate file security: size, type, content
        
        Args:
            file_content: Raw file content
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file size
        file_size = len(file_content)
        if file_size > self.MAX_FILE_SIZE:
            return False, f"File size {file_size / 1024 / 1024:.2f}MB exceeds maximum {self.MAX_FILE_SIZE / 1024 / 1024}MB"
        
        if file_size == 0:
            return False, "File is empty"
        
        # Check MIME type using python-magic
        mime = magic.from_buffer(file_content, mime=True)
        if mime not in self.ALLOWED_MIME_TYPES:
            return False, f"File type '{mime}' is not allowed. Allowed types: {', '.join(self.ALLOWED_MIME_TYPES)}"
        
        # Calculate file hash for integrity checking
        self._file_hash = hashlib.sha256(file_content).hexdigest()
        
        # Detect encoding
        detection = chardet.detect(file_content[:10000])  # Check first 10KB
        self._encoding = detection.get('encoding', 'utf-8')
        
        if detection.get('confidence', 0) < 0.7:
            self.logger.warning(f"Low confidence in encoding detection: {detection}")
        
        return True, None
    
    async def validate_connection(self) -> Tuple[bool, Optional[str]]:
        """
        Validate CSV file can be read and parsed
        
        Returns:
            Tuple of (success, error_message)
        """
        try:
            if not self.file_path or not os.path.exists(self.file_path):
                return False, f"File not found: {self.file_path}"
            
            # Try to read first few rows
            self.df = pd.read_csv(
                self.file_path,
                nrows=5,
                encoding=self._encoding or 'utf-8',
                on_bad_lines='skip'
            )
            
            if self.df.empty:
                return False, "CSV file appears to be empty"
            
            return True, None
            
        except Exception as e:
            self.logger.error(f"Failed to validate CSV connection: {str(e)}")
            return False, f"Failed to read CSV: {str(e)}"
    
    async def fetch_schema(self) -> Dict[str, Any]:
        """
        Analyze CSV file and extract schema information
        
        Returns:
            Dictionary containing schema details
        """
        if self.df is None:
            # Read the full file if not already loaded
            self.df = pd.read_csv(
                self.file_path,
                encoding=self._encoding or 'utf-8',
                on_bad_lines='skip',
                low_memory=False
            )
        
        schema = {
            "columns": [],
            "row_count": len(self.df),
            "file_size_bytes": os.path.getsize(self.file_path) if self.file_path else 0,
            "encoding": self._encoding,
            "file_hash": self._file_hash
        }
        
        # Analyze each column
        for col in self.df.columns:
            col_info = {
                "name": self.sanitize_column_name(str(col)),
                "original_name": str(col),
                "type": self.infer_column_type(self.df[col]),
                "nullable": self.df[col].isnull().any(),
                "unique_count": self.df[col].nunique(),
                "null_count": self.df[col].isnull().sum(),
                "null_percentage": (self.df[col].isnull().sum() / len(self.df)) * 100 if len(self.df) > 0 else 0
            }
            
            # Add statistics for numeric columns
            if pd.api.types.is_numeric_dtype(self.df[col]):
                col_info.update({
                    "min": float(self.df[col].min()) if not self.df[col].isna().all() else None,
                    "max": float(self.df[col].max()) if not self.df[col].isna().all() else None,
                    "mean": float(self.df[col].mean()) if not self.df[col].isna().all() else None,
                    "median": float(self.df[col].median()) if not self.df[col].isna().all() else None,
                    "std": float(self.df[col].std()) if not self.df[col].isna().all() else None
                })
            
            # Sample values for categorical columns
            if pd.api.types.is_object_dtype(self.df[col]):
                top_values = self.df[col].value_counts().head(10).to_dict()
                col_info["top_values"] = {str(k): v for k, v in top_values.items()}
            
            schema["columns"].append(col_info)
        
        return schema
    
    async def fetch_data(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch data from CSV file
        
        Args:
            limit: Maximum number of rows
            offset: Number of rows to skip
            filters: Not implemented for CSV
            
        Returns:
            List of row dictionaries
        """
        if self.df is None:
            self.df = pd.read_csv(
                self.file_path,
                encoding=self._encoding or 'utf-8',
                on_bad_lines='skip',
                low_memory=False
            )
        
        # Apply offset and limit
        start_idx = offset or 0
        end_idx = start_idx + limit if limit else len(self.df)
        
        subset = self.df.iloc[start_idx:end_idx]
        
        # Convert to list of dictionaries, handling NaN values
        return subset.where(pd.notnull(subset), None).to_dict('records')
    
    async def count_rows(self) -> int:
        """
        Count total rows in CSV file
        
        Returns:
            Total row count
        """
        if self.df is None:
            # For large files, use chunking to count rows without loading entire file
            row_count = 0
            for chunk in pd.read_csv(
                self.file_path,
                chunksize=self.CHUNK_SIZE,
                encoding=self._encoding or 'utf-8',
                on_bad_lines='skip'
            ):
                row_count += len(chunk)
            return row_count
        
        return len(self.df)
    
    async def validate_data(self, data: List[Dict[str, Any]] = None) -> Tuple[bool, List[str]]:
        """
        Comprehensive data validation
        
        Args:
            data: Optional data to validate (uses loaded df if not provided)
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if data is None and self.df is None:
            errors.append("No data to validate")
            return False, errors
        
        df_to_validate = pd.DataFrame(data) if data else self.df
        
        # Check minimum rows
        if len(df_to_validate) < self.MIN_ROWS:
            errors.append(f"File has {len(df_to_validate)} rows, minimum is {self.MIN_ROWS}")
        
        # Check maximum columns
        if len(df_to_validate.columns) > self.MAX_COLUMNS:
            errors.append(f"File has {len(df_to_validate.columns)} columns, maximum is {self.MAX_COLUMNS}")
        
        # Check for duplicate column names
        duplicate_cols = df_to_validate.columns[df_to_validate.columns.duplicated()].tolist()
        if duplicate_cols:
            errors.append(f"Duplicate column names found: {duplicate_cols}")
        
        # Check column name lengths
        for col in df_to_validate.columns:
            if len(str(col)) > self.MAX_COLUMN_NAME_LENGTH:
                errors.append(f"Column name '{col[:50]}...' exceeds maximum length of {self.MAX_COLUMN_NAME_LENGTH}")
        
        # Check for completely empty columns
        empty_cols = [col for col in df_to_validate.columns if df_to_validate[col].isna().all()]
        if empty_cols:
            errors.append(f"Completely empty columns found: {empty_cols}")
        
        # Check data quality score
        quality_score = self.calculate_quality_score(df_to_validate)
        if quality_score < 0.3:  # Less than 30% quality
            errors.append(f"Data quality score is too low: {quality_score:.2%}")
        
        return len(errors) == 0, errors
    
    def infer_column_type(self, series: pd.Series) -> str:
        """
        Infer the data type of a pandas Series
        
        Args:
            series: Pandas Series to analyze
            
        Returns:
            Inferred data type string
        """
        # Remove null values for type inference
        non_null = series.dropna()
        
        if len(non_null) == 0:
            return "NULL"
        
        # Try to convert to numeric
        try:
            pd.to_numeric(non_null, errors='raise')
            if non_null.dtype == 'int64' or (non_null == non_null.astype(int)).all():
                return "INTEGER"
            else:
                return "FLOAT"
        except:
            pass
        
        # Try to convert to datetime
        try:
            pd.to_datetime(non_null, errors='raise')
            return "TIMESTAMP"
        except:
            pass
        
        # Try to convert to boolean
        if set(non_null.unique()).issubset({True, False, 1, 0, '1', '0', 'true', 'false', 'True', 'False'}):
            return "BOOLEAN"
        
        # Default to string
        return "VARCHAR"
    
    def calculate_quality_score(self, df: pd.DataFrame) -> float:
        """
        Calculate data quality score (0.0 to 1.0)
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Quality score between 0 and 1
        """
        if df.empty:
            return 0.0
        
        scores = []
        
        # Completeness score (percentage of non-null values)
        completeness = 1 - (df.isnull().sum().sum() / (len(df) * len(df.columns)))
        scores.append(completeness)
        
        # Uniqueness score (for columns that should be unique)
        # This is a simplified check - in production, you'd have metadata about which columns should be unique
        if len(df) > 1:
            potential_id_cols = [col for col in df.columns if 'id' in str(col).lower()]
            if potential_id_cols:
                uniqueness_scores = [df[col].nunique() / len(df) for col in potential_id_cols]
                scores.append(max(uniqueness_scores) if uniqueness_scores else 0.5)
        
        # Consistency score (check for mixed types in columns)
        consistency_scores = []
        for col in df.columns:
            try:
                # If we can convert to numeric without errors, it's consistent
                pd.to_numeric(df[col], errors='raise')
                consistency_scores.append(1.0)
            except:
                # Check if it's consistently string or mixed
                non_null = df[col].dropna()
                if len(non_null) > 0:
                    types = non_null.apply(type).unique()
                    consistency_scores.append(1.0 if len(types) == 1 else 0.5)
        
        if consistency_scores:
            scores.append(sum(consistency_scores) / len(consistency_scores))
        
        # Return average of all scores
        return sum(scores) / len(scores) if scores else 0.0
    
    async def process_file_upload(
        self,
        file_content: bytes,
        file_name: str,
        job_id: str
    ) -> Dict[str, Any]:
        """
        Process uploaded CSV file
        
        Args:
            file_content: Raw file content
            file_name: Original file name
            job_id: Processing job ID
            
        Returns:
            Processing result dictionary
        """
        result = {
            "success": False,
            "rows_processed": 0,
            "errors": [],
            "schema": None
        }
        
        try:
            # Validate file security
            is_valid, error = await self.validate_file_security(file_content)
            if not is_valid:
                result["errors"].append(error)
                return result
            
            # Parse CSV
            self.df = pd.read_csv(
                io.BytesIO(file_content),
                encoding=self._encoding or 'utf-8',
                on_bad_lines='skip',
                low_memory=False
            )
            
            # Validate data
            is_valid, errors = await self.validate_data()
            if not is_valid:
                result["errors"].extend(errors)
                return result
            
            # Get schema
            schema = await self.fetch_schema()
            
            result.update({
                "success": True,
                "rows_processed": len(self.df),
                "schema": schema,
                "quality_score": self.calculate_quality_score(self.df)
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to process CSV file: {str(e)}")
            result["errors"].append(f"Processing error: {str(e)}")
            return result