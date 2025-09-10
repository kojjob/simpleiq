"""
Tests for data processing API endpoints
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.data_processing_job import DataProcessingJob, ProcessingStatus
from app.models.data_source import DataSource, DataSourceType
from app.models.user import User


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def mock_user():
    """Mock user fixture"""
    user = MagicMock(spec=User)
    user.id = "550e8400-e29b-41d4-a716-446655440000"
    user.email = "test@example.com"
    return user


@pytest.fixture
def mock_data_source():
    """Mock data source fixture"""
    data_source = MagicMock(spec=DataSource)
    data_source.id = "550e8400-e29b-41d4-a716-446655440001"
    data_source.user_id = "550e8400-e29b-41d4-a716-446655440000"
    data_source.name = "Test CSV"
    data_source.type = DataSourceType.csv
    return data_source


@pytest.fixture
def mock_job():
    """Mock processing job fixture"""
    job = MagicMock(spec=DataProcessingJob)
    job.id = "550e8400-e29b-41d4-a716-446655440002"
    job.data_source_id = "550e8400-e29b-41d4-a716-446655440001"
    job.user_id = "550e8400-e29b-41d4-a716-446655440000"
    job.job_type = "upload"
    job.status = ProcessingStatus.QUEUED.value
    job.progress_percentage = 0.0
    job.current_step = None
    job.error_message = None
    job.can_retry = False
    job.retry_count = 0
    job.result_summary = None
    job.started_at = None
    job.completed_at = None
    job.processing_time_seconds = None
    return job


class TestDataProcessingAPI:
    """Test data processing API endpoints"""

    @patch("app.api.v1.data_processing.get_current_user")
    @patch("app.api.v1.data_processing.get_async_db")
    @patch("app.services.data_processor.DataProcessingService")
    def test_create_job_success(self, mock_service_class, mock_db, mock_auth, client, mock_user, mock_data_source, mock_job):
        """Test successful job creation"""
        # Setup mocks
        mock_auth.return_value = mock_user
        mock_db_session = AsyncMock(spec=AsyncSession)
        mock_db.return_value = mock_db_session
        mock_db_session.get = AsyncMock(return_value=mock_data_source)
        
        mock_service = AsyncMock()
        mock_service_class.return_value = mock_service
        mock_service.create_processing_job = AsyncMock(return_value=mock_job)
        
        # Test data
        request_data = {
            "data_source_id": "550e8400-e29b-41d4-a716-446655440001",
            "job_type": "upload",
            "config": {"chunk_size": 10000}
        }
        
        # Make request
        response = client.post("/api/v1/data-processing/jobs", json=request_data)
        
        # Assertions
        assert response.status_code == 201
        data = response.json()
        assert data["job_id"] == str(mock_job.id)
        assert data["status"] == "created"
        assert "message" in data

    @patch("app.api.v1.data_processing.get_current_user")
    @patch("app.api.v1.data_processing.get_async_db")
    def test_create_job_data_source_not_found(self, mock_db, mock_auth, client, mock_user):
        """Test job creation with non-existent data source"""
        # Setup mocks
        mock_auth.return_value = mock_user
        mock_db_session = AsyncMock(spec=AsyncSession)
        mock_db.return_value = mock_db_session
        mock_db_session.get = AsyncMock(return_value=None)  # Data source not found
        
        # Test data
        request_data = {
            "data_source_id": "non-existent-id",
            "job_type": "upload"
        }
        
        # Make request
        response = client.post("/api/v1/data-processing/jobs", json=request_data)
        
        # Assertions
        assert response.status_code == 404
        assert "Data source not found" in response.json()["detail"]

    @patch("app.api.v1.data_processing.get_current_user")
    @patch("app.api.v1.data_processing.get_async_db")
    def test_create_job_access_denied(self, mock_db, mock_auth, client, mock_user, mock_data_source):
        """Test job creation with access denied"""
        # Setup mocks
        mock_auth.return_value = mock_user
        mock_db_session = AsyncMock(spec=AsyncSession)
        mock_db.return_value = mock_db_session
        
        # Data source belongs to different user
        mock_data_source.user_id = "different-user-id"
        mock_db_session.get = AsyncMock(return_value=mock_data_source)
        
        # Test data
        request_data = {
            "data_source_id": "550e8400-e29b-41d4-a716-446655440001",
            "job_type": "upload"
        }
        
        # Make request
        response = client.post("/api/v1/data-processing/jobs", json=request_data)
        
        # Assertions
        assert response.status_code == 403
        assert "Access denied to data source" in response.json()["detail"]

    @patch("app.api.v1.data_processing.get_current_user")
    @patch("app.api.v1.data_processing.get_async_db")
    def test_create_job_invalid_job_type(self, mock_db, mock_auth, client, mock_user, mock_data_source):
        """Test job creation with invalid job type"""
        # Setup mocks
        mock_auth.return_value = mock_user
        mock_db_session = AsyncMock(spec=AsyncSession)
        mock_db.return_value = mock_db_session
        mock_db_session.get = AsyncMock(return_value=mock_data_source)
        
        # Test data
        request_data = {
            "data_source_id": "550e8400-e29b-41d4-a716-446655440001",
            "job_type": "invalid_type"
        }
        
        # Make request
        response = client.post("/api/v1/data-processing/jobs", json=request_data)
        
        # Assertions
        assert response.status_code == 400
        assert "Invalid job type" in response.json()["detail"]

    @patch("app.api.v1.data_processing.get_current_user")
    @patch("app.api.v1.data_processing.get_async_db")
    @patch("app.services.data_processor.DataProcessingService")
    def test_get_job_status_success(self, mock_service_class, mock_db, mock_auth, client, mock_user, mock_job):
        """Test successful job status retrieval"""
        # Setup mocks
        mock_auth.return_value = mock_user
        mock_db_session = AsyncMock(spec=AsyncSession)
        mock_db.return_value = mock_db_session
        mock_db_session.get = AsyncMock(return_value=mock_job)
        
        mock_service = AsyncMock()
        mock_service_class.return_value = mock_service
        mock_service.get_job_status = AsyncMock(return_value={
            "job_id": str(mock_job.id),
            "status": "processing",
            "progress_percentage": 45.0,
            "current_step": "Processing data",
            "error_message": None,
            "can_retry": False
        })
        
        # Make request
        response = client.get(f"/api/v1/data-processing/jobs/{mock_job.id}")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == str(mock_job.id)
        assert data["status"] == "processing"
        assert data["progress_percentage"] == 45.0
        assert data["current_step"] == "Processing data"

    @patch("app.api.v1.data_processing.get_current_user")
    @patch("app.api.v1.data_processing.get_async_db")
    def test_get_job_status_not_found(self, mock_db, mock_auth, client, mock_user):
        """Test job status retrieval for non-existent job"""
        # Setup mocks
        mock_auth.return_value = mock_user
        mock_db_session = AsyncMock(spec=AsyncSession)
        mock_db.return_value = mock_db_session
        mock_db_session.get = AsyncMock(return_value=None)  # Job not found
        
        # Make request
        response = client.get("/api/v1/data-processing/jobs/non-existent-id")
        
        # Assertions
        assert response.status_code == 404
        assert "Job not found" in response.json()["detail"]

    @patch("app.api.v1.data_processing.get_current_user")
    @patch("app.api.v1.data_processing.get_async_db")
    def test_get_job_status_access_denied(self, mock_db, mock_auth, client, mock_user, mock_job):
        """Test job status retrieval with access denied"""
        # Setup mocks
        mock_auth.return_value = mock_user
        mock_db_session = AsyncMock(spec=AsyncSession)
        mock_db.return_value = mock_db_session
        
        # Job belongs to different user
        mock_job.user_id = "different-user-id"
        mock_db_session.get = AsyncMock(return_value=mock_job)
        
        # Make request
        response = client.get(f"/api/v1/data-processing/jobs/{mock_job.id}")
        
        # Assertions
        assert response.status_code == 403
        assert "Access denied to job" in response.json()["detail"]

    @patch("app.api.v1.data_processing.get_current_user")
    @patch("app.api.v1.data_processing.get_async_db")
    @patch("app.services.data_processor.DataProcessingService")
    def test_retry_job_success(self, mock_service_class, mock_db, mock_auth, client, mock_user, mock_job):
        """Test successful job retry"""
        # Setup mocks
        mock_auth.return_value = mock_user
        mock_db_session = AsyncMock(spec=AsyncSession)
        mock_db.return_value = mock_db_session
        
        # Job is failed and can be retried
        mock_job.status = "failed"
        mock_job.can_retry = True
        mock_db_session.get = AsyncMock(return_value=mock_job)
        
        # Make request
        response = client.post(f"/api/v1/data-processing/jobs/{mock_job.id}/retry")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == str(mock_job.id)
        assert data["status"] == "retry_initiated"

    @patch("app.api.v1.data_processing.get_current_user")
    @patch("app.api.v1.data_processing.get_async_db")
    def test_retry_job_not_failed(self, mock_db, mock_auth, client, mock_user, mock_job):
        """Test retry for job that is not failed"""
        # Setup mocks
        mock_auth.return_value = mock_user
        mock_db_session = AsyncMock(spec=AsyncSession)
        mock_db.return_value = mock_db_session
        
        # Job is not failed
        mock_job.status = "completed"
        mock_db_session.get = AsyncMock(return_value=mock_job)
        
        # Make request
        response = client.post(f"/api/v1/data-processing/jobs/{mock_job.id}/retry")
        
        # Assertions
        assert response.status_code == 400
        assert "Only failed jobs can be retried" in response.json()["detail"]

    @patch("app.api.v1.data_processing.get_current_user")
    @patch("app.api.v1.data_processing.get_async_db")
    def test_retry_job_cannot_retry(self, mock_db, mock_auth, client, mock_user, mock_job):
        """Test retry for job that cannot be retried"""
        # Setup mocks
        mock_auth.return_value = mock_user
        mock_db_session = AsyncMock(spec=AsyncSession)
        mock_db.return_value = mock_db_session
        
        # Job is failed but cannot be retried
        mock_job.status = "failed"
        mock_job.can_retry = False
        mock_db_session.get = AsyncMock(return_value=mock_job)
        
        # Make request
        response = client.post(f"/api/v1/data-processing/jobs/{mock_job.id}/retry")
        
        # Assertions
        assert response.status_code == 400
        assert "exceeded maximum retry attempts" in response.json()["detail"]

    @patch("app.api.v1.data_processing.get_current_user")
    @patch("app.api.v1.data_processing.get_async_db")
    def test_list_jobs_success(self, mock_db, mock_auth, client, mock_user, mock_job):
        """Test successful job listing"""
        # Setup mocks
        mock_auth.return_value = mock_user
        mock_db_session = AsyncMock(spec=AsyncSession)
        mock_db.return_value = mock_db_session
        
        # Mock query result
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_job]
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        # Make request
        response = client.get("/api/v1/data-processing/jobs")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["job_id"] == str(mock_job.id)

    def test_job_create_request_validation(self, client):
        """Test request validation for job creation"""
        # Missing required fields
        response = client.post("/api/v1/data-processing/jobs", json={})
        assert response.status_code == 422
        
        # Invalid data types
        response = client.post("/api/v1/data-processing/jobs", json={
            "data_source_id": 123,  # Should be string
            "job_type": "upload"
        })
        assert response.status_code == 422