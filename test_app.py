"""
Unit tests for FastAPI S3 proxy service

Fixtures:
    - test_client: Provides a test client for the FastAPI app
    - mock_s3_client: Mocks the S3 client

Test Cases:
    - test_upload_file_*: Tests for file upload scenarios
    - test_download_file_*: Tests for file download scenarios
"""

from io import BytesIO
import pytest
from fastapi.testclient import TestClient
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from app import app

@pytest.fixture
def test_client():
    """Fixture to provide a test client for FastAPI app"""
    return TestClient(app)

@pytest.fixture
def mock_s3_client(mocker):
    """Fixture to mock boto3 client used in the app"""
    mock_s3 = mocker.patch("app.client")
    return mock_s3



def test_upload_file_success(test_client, mock_s3_client):
    """Test successful file upload to S3 via endpoint"""
    mock_s3_client.upload_fileobj.return_value = None

    response = test_client.post(
        "/upload/",
        files={"file": ("test.txt", b"test content")},
        data={"bucket_name": "test-bucket", "object_name": "test.txt"}
    )

    assert response.status_code == 200
    assert response.json() == {"message": "File 'test.txt' uploaded to bucket 'test-bucket' successfully."}
    mock_s3_client.upload_fileobj.assert_called_once()

def test_upload_file_bucket_not_found(test_client, mock_s3_client):
    """Test file upload failure because of bucket not existing"""
    error_response = {"Error": {
        "Code": "NoSuchBucket", 
        "Message": "The specified bucket does not exist."
        }}
    mock_s3_client.upload_fileobj.side_effect = ClientError(error_response, "PutObject")

    response = test_client.post(
        "/upload/",
        files={"file": ("test.txt", b"test content")},
        data={"bucket_name": "nonexistent-bucket", "object_name": "test.txt"}
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Bucket not found"}

def test_upload_file_no_credentials(test_client, mock_s3_client):
    """Test file upload failure because of missing credentials"""
    mock_s3_client.upload_fileobj.side_effect = NoCredentialsError

    response = test_client.post(
        "/upload/",
        files={"file": ("test.txt", b"test content")},
        data={"bucket_name": "test-bucket", "object_name": "test.txt"}
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Credentials not found"}

def test_upload_file_incomplete_credentials(test_client, mock_s3_client):
    """Test file upload failure because of incomplete credentials"""
    mock_s3_client.upload_fileobj.side_effect = PartialCredentialsError(provider="aws", cred_var="SUPER_SECRET_KEY")

    response = test_client.post(
        "/upload/",
        files={"file": ("test.txt", b"test content")},
        data={"bucket_name": "test-bucket", "object_name": "test.txt"}
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Incomplete credentials"}



def test_download_file_success(test_client, mock_s3_client):
    """Test successful file download from S3 via endpoint"""
    mock_s3_client.get_object.return_value = {"Body": BytesIO(b"test content")}

    response = test_client.get("/download/", params={"bucket_name": "test-bucket",
                                                     "object_name": "test.txt"})

    assert response.status_code == 200
    assert response.content == b"test content"
    mock_s3_client.get_object.assert_called_once_with(Bucket="test-bucket", Key="test.txt")

def test_download_file_bucket_not_found(test_client, mock_s3_client):
    """Test file download failure because of bucket not existing"""
    error_response = {"Error": {
        "Code": "NoSuchBucket", 
        "Message": "The specified bucket does not exist."
        }}
    mock_s3_client.get_object.side_effect = ClientError(error_response, "GetObject")

    response = test_client.get("/download/", params={"bucket_name": "nonexistent-bucket",
                                                     "object_name": "test.txt"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Bucket not found"}

def test_download_file_incomplete_credentials(test_client, mock_s3_client):
    """Test file download failure because of incomplete credentials"""
    mock_s3_client.get_object.side_effect = PartialCredentialsError(provider="aws", cred_var="146%_SECRET_KEY")

    response = test_client.get("/download/", params={"bucket_name": "test-bucket",
                                                     "object_name": "test.txt"})

    assert response.status_code == 401
    assert response.json() == {"detail": "Incomplete credentials"}

def test_download_file_no_credentials(test_client, mock_s3_client):
    """Test file download failure because of missing credentials"""
    mock_s3_client.get_object.side_effect = NoCredentialsError

    response = test_client.get("/download/", params={"bucket_name": "test-bucket",
                                                     "object_name": "test.txt"})

    assert response.status_code == 401
    assert response.json() == {"detail": "Credentials not found"}

def test_download_file_not_found(test_client, mock_s3_client):
    """Test file download failure because of the file not existing in S3"""
    error_response = {"Error": {
        "Code": "NoSuchKey", 
        "Message": "The specified key does not exist."
        }}
    mock_s3_client.get_object.side_effect = ClientError(error_response, "GetObject")

    response = test_client.get("/download/", params={"bucket_name": "test-bucket",
                                                     "object_name": "nonexistent.txt"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Object not found in the bucket"}
