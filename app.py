"""
FastAPI application for proxying file operations to S3 storage

Endpoints:
- /upload/ (POST): Upload a file to S3 bucket and object name
- /download/ (GET): Download a file from S3 bucket and object name
"""

import os
import boto3
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError

app = FastAPI()

#setting up client for minio or aws
load_dotenv()
if os.getenv("MINIO") == "true":
    print("minio")
    client = boto3.client(
        "s3",
        endpoint_url=os.getenv("MINIO_ENDPOINT"),
        aws_access_key_id=os.getenv("ACCESS_KEY"),
        aws_secret_access_key=os.getenv("SECRET_KEY")
    )
else:
    client = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("ACCESS_KEY"),
        aws_secret_access_key=os.getenv("SECRET_KEY"),
        region_name=os.getenv("AWS_REGION")
    )



@app.post("/upload/")
async def upload_file(bucket_name: str = Form(...),
                      object_name: str = Form(...),
                      file: UploadFile = File(...)):
    """
    Uploads a file to the specified S3 bucket and object name
    """
    try:
        client.upload_fileobj(file.file, bucket_name, object_name)
        return {"message": f"File '{object_name}' uploaded to bucket '{bucket_name}' successfully."}
    except NoCredentialsError as e:
        raise HTTPException(status_code=401, detail="Credentials not found") from e
    except PartialCredentialsError as e:
        raise HTTPException(status_code=401, detail="Incomplete credentials") from e
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchBucket":
            raise HTTPException(status_code=404, detail="Bucket not found") from e
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {e}") from e

@app.get("/download/")
async def download_file(bucket_name: str,
                        object_name: str):
    """
    Downloads a file from the specified S3 bucket and object name.
    """
    try:
        file_obj = client.get_object(Bucket=bucket_name, Key=object_name)
        return StreamingResponse(file_obj["Body"], media_type="application/octet-stream")
    except NoCredentialsError as e:
        raise HTTPException(status_code=401, detail="Credentials not found") from e
    except PartialCredentialsError as e:
        raise HTTPException(status_code=401, detail="Incomplete credentials") from e
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "NoSuchBucket":
            raise HTTPException(status_code=404, detail="Bucket not found") from e
        if error_code == "NoSuchKey":
            raise HTTPException(status_code=404, detail="Object not found in the bucket") from e
        raise HTTPException(status_code=500, detail=f"Failed to download file: {e}") from e
