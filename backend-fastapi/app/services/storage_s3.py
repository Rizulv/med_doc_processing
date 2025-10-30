import os
import uuid
import boto3
from botocore.exceptions import ClientError
from typing import BinaryIO
from pathlib import Path


class S3Storage:
    """S3 storage for uploaded documents"""
    
    def __init__(self, bucket_name: str = None, region: str = "ap-south-1"):
        """
        Initialize S3 storage
        
        Args:
            bucket_name: S3 bucket name (defaults to env var S3_BUCKET_NAME)
            region: AWS region
        """
        self.bucket_name = bucket_name or os.getenv("S3_BUCKET_NAME", "med-docs-dev")
        self.region = region
        self.s3_client = boto3.client('s3', region_name=region)
    
    def save_file(self, file_data: BinaryIO, filename: str) -> str:
        """
        Save file to S3
        
        Args:
            file_data: File content
            filename: Original filename
            
        Returns:
            str: S3 key (path) to saved file
        """
        # Create unique key for this file
        file_id = str(uuid.uuid4())
        s3_key = f"{file_id}/{filename}"
        
        try:
            # Upload file to S3
            self.s3_client.upload_fileobj(
                file_data,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': self._get_content_type(filename),
                    'ServerSideEncryption': 'AES256'  # Encrypt at rest
                }
            )
            return s3_key
        except ClientError as e:
            raise Exception(f"Failed to upload to S3: {str(e)}")
    
    def get_file_url(self, s3_key: str, expiration: int = 3600) -> str:
        """
        Generate presigned URL for file access
        
        Args:
            s3_key: S3 object key
            expiration: URL expiration time in seconds (default 1 hour)
            
        Returns:
            str: Presigned URL
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            raise Exception(f"Failed to generate presigned URL: {str(e)}")
    
    def file_exists(self, s3_key: str) -> bool:
        """Check if file exists in S3"""
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except ClientError:
            return False
    
    def download_file(self, s3_key: str) -> bytes:
        """
        Download file content from S3
        
        Args:
            s3_key: S3 object key
            
        Returns:
            bytes: File content
        """
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=s3_key)
            return response['Body'].read()
        except ClientError as e:
            raise Exception(f"Failed to download from S3: {str(e)}")
    
    def _get_content_type(self, filename: str) -> str:
        """Determine content type from filename"""
        ext = Path(filename).suffix.lower()
        content_types = {
            '.pdf': 'application/pdf',
            '.txt': 'text/plain',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        }
        return content_types.get(ext, 'application/octet-stream')


# Initialize storage instance
storage = S3Storage()
