import boto3
import tempfile
import os
from botocore.exceptions import ClientError
from fastapi import UploadFile
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket_name = settings.S3_BUCKET_NAME
    
    async def upload_file(self, file: UploadFile, object_name: str) -> str:
        """Upload file to S3 and return the URL"""
        try:
            # Create a temporary file to handle the upload
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            # Upload to S3
            self.s3_client.upload_file(
                temp_file_path,
                self.bucket_name,
                object_name,
                ExtraArgs={'ContentType': file.content_type or 'audio/mpeg'}
            )
            
            # Clean up temp file
            os.unlink(temp_file_path)
            
            # Generate S3 URL
            s3_url = f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{object_name}"
            
            logger.info(f"Successfully uploaded file to S3: {s3_url}")
            return s3_url
            
        except ClientError as e:
            logger.error(f"Failed to upload file to S3: {str(e)}")
            raise Exception(f"Failed to upload file to S3: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during S3 upload: {str(e)}")
            raise Exception(f"Unexpected error during S3 upload: {str(e)}")
    
    def generate_presigned_url(self, object_name: str, expiration: int = 3600) -> str:
        """Generate a presigned URL for S3 object"""
        try:
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': object_name},
                ExpiresIn=expiration
            )
            return response
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {str(e)}")
            raise Exception(f"Failed to generate presigned URL: {str(e)}")

s3_service = S3Service()
