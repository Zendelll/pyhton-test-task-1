"""
Script to create S3 bucket on MinIO
"""


import os
import boto3
from dotenv import load_dotenv
from botocore.exceptions import ClientError

load_dotenv()

if __name__ == "__main__" and os.getenv("MINIO") == "true":
    BUCKET_NAME = os.getenv("BUCKET_NAME")

    client = boto3.client(
        "s3",
        endpoint_url=os.getenv("MINIO_ENDPOINT"),
        aws_access_key_id=os.getenv("ACCESS_KEY"),
        aws_secret_access_key=os.getenv("SECRET_KEY")
    )

    try:
        client.create_bucket(Bucket=BUCKET_NAME)
        print(f"Bucket '{BUCKET_NAME}' created successfully.")
    except ClientError as e:
        if e.response["Error"]["Code"] == "BucketAlreadyOwnedByYou":
            print(f"Bucket '{BUCKET_NAME}' already exists.")
        else:
            raise e
