from io import BytesIO

import boto3
from botocore.client import BaseClient
from botocore.config import Config


class S3Client:
    def __init__(self, access_key: str, secret_key: str, region: str = 'us-east-2'):
        self.s3: BaseClient = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
            config=Config(signature_version='s3v4')
        )

    def get_video_file(self, bucket_name, s3_key):
        try:
            response = self.s3.get_object(
                Bucket=bucket_name,
                Key=s3_key
            )
            return BytesIO(response['Body'].read())
        except Exception as e:
            print(f"Ошибка при получении видео из S3: {e}")
            return None

    def delete_object(self, bucket_name, s3_key):
        self.s3.delete_object(Bucket=bucket_name, Key=s3_key)

    def get_presigned_url(self, bucket_name, s3_key):
        presigned_url = self.s3.generate_presigned_url(
            ClientMethod='put_object',
            Params={
                'Bucket': bucket_name,
                'Key': s3_key,
                'ACL': 'public-read',
                'ContentType': 'video/mp4'
            },
            ExpiresIn=3600
        )

        return presigned_url
