import asyncio
import os
from datetime import date, timedelta

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone
from s3 import S3Client


class Command(BaseCommand):
    help = 'Создание дампа базы данных, отправка на storage и удаление старых дампов'

    def handle(self, *args, **options):
        def sync_file_list():
            async def consume_file_list():
                return [f async for f in s3.list(f'{settings.S3_DUMPS_DIR_NAME}/')]

            yield from event_loop.run_until_complete(consume_file_list())

        now = timezone.localtime()
        file_name = f'dump_{now.year}-{now.month}-{now.day}_{now.hour}:{now.minute}'
        file_path = f'{settings.S3_DUMPS_DIR_NAME}/{file_name}.json'
        call_command('dumpdata', output=file_path)
        archive_path = f'{settings.S3_DUMPS_DIR_NAME}/{file_name}.tar.gz'
        os.system(f'tar -zcvf {archive_path} {file_path}')
        os.system(f'rm {file_path}')

        s3 = S3Client(
            access_key=settings.S3_ACCESS_KEY,
            secret_key=settings.S3_SECRET_KEY,
            region=settings.S3_REGION,
            s3_bucket=settings.S3_BUCKET_NAME,
        )
        event_loop = asyncio.get_event_loop()
        event_loop.run_until_complete(s3.upload(archive_path, open(archive_path, 'rb').read()))
        os.system(f'rm {archive_path}')

        keys_to_delete = []
        week_ago_date = (now - timedelta(days=7)).date()
        for s3_file in sync_file_list():
            try:
                splitted_key = s3_file.key.split('_')
                year, month, day = [int(i) for i in splitted_key[1].split('-')]
                hour, minute = [int(i) for i in splitted_key[2].split('.')[0].split(':')]
            except ValueError:
                keys_to_delete.append(s3_file.key)
                continue
            file_date = date(year=year, month=month, day=day)

            # Храним только дампы за неделю и за первый день каждого месяца
            if file_date < week_ago_date and (day != 1 or hour < 12):
                keys_to_delete.append(s3_file.key)

        result = 'New dump successfully created and uploaded to storage.'
        if keys_to_delete:
            event_loop.run_until_complete(s3.delete(*keys_to_delete))
            result += '\nDeleted dumps:\n' + '\n'.join(keys_to_delete)

        return result
