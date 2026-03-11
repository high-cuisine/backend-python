import asyncio
import os

from PIL import Image
from PIL.Image import LANCZOS
from django.conf import settings
from s3 import S3Client


class StorageClient:
    BASE_URL = f'https://storage.yandexcloud.net/{settings.S3_BUCKET_NAME}/'

    def __init__(self):
        self.s3_client = S3Client(
            access_key=settings.S3_ACCESS_KEY,
            secret_key=settings.S3_SECRET_KEY,
            region=settings.S3_REGION,
            s3_bucket=settings.S3_BUCKET_NAME,
        )

    def upload_file(self, path: str, file: bytes = None) -> str:
        event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(event_loop)
        if path and not file:
            event_loop.run_until_complete(self.s3_client.upload(path, open(path, 'rb').read()))
            os.system(f'rm {path}')
        elif file:
            event_loop.run_until_complete(self.s3_client.upload(path, file))
        else:
            raise ValueError('No path and no file')
        return f'{self.BASE_URL}{path}'

    def upload_quest_file(self, path: str) -> str:
        file_name = path.split('/')[-1]
        relative_path = f'quest/{file_name}'
        return self.upload_file(relative_path)

    @staticmethod
    def resize_image(path: str, width: int, height: int):
        im = Image.open(path)
        im.thumbnail((width, height), LANCZOS)
        im.save(path)

    def upload_image(self, path: str, width: int, height: int):
        self.resize_image(path, width, height)
        return self.upload_file(path)
