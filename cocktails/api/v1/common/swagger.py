from django.conf import settings
from drf_yasg import openapi
from api.v1.common.serializers import *

base_tags = ['Common']

image_upload = {
    'operation_description': '## Загрузка изображения в storage с изменением размера',
    'operation_summary': 'Загрузка изображения в storage с изменением размера',
    'request_body': ImageUploadSerializer,
    'responses': {
        '200': openapi.Response(
            description='Success Response',
            examples={
                'application/json': {
                    'url': f'https://storage.yandexcloud.net/{settings.S3_BUCKET_NAME}/quest/banner_413.jpg',
                }
            }
        )
    },
    'tags': base_tags,
}

file_upload = {
    'operation_description': '## Загрузка файла в storage',
    'operation_summary': 'Загрузка файла в storage',
    'request_body': FileUploadSerializer,
    'responses': {
        '200': openapi.Response(
            description='Success Response',
            examples={
                'application/json': {
                    'url': f'https://storage.yandexcloud.net/{settings.S3_BUCKET_NAME}/quest/banner_413.jpg',
                }
            }
        )
    },
    'tags': base_tags,
}

config_list = dict(
    operation_description='## Список конфигураций',
    operation_summary='Список конфигураций',
    responses={
        '200': openapi.Response(
            description='Success Response',
            examples={
                'application/json': {
                    "QUEST_ACTUAL_DAYS_BEFORE": "3",
                    "QUEST_ACTUAL_DAYS_AFTER": "3",
                    "PLAN_GENERATION_FREE_LIMIT": "1",
                    "PLAN_GENERATION_UPDATE_LIMIT": "5",
                },
            },
        ),
    },
    tags=base_tags,
)


docs_list = {
    'operation_description': '## Список документов',
    'operation_summary': 'Получение Списока документов',
    'responses': {'200': DocumentSerializer(many=True)},
    'tags': base_tags,
}

ads_list = {
    'operation_description': '## Список рекламы',
    'operation_summary': 'Получение Списока рекламы',
    'responses': {'200': AdvertisementSerializer(many=True)},
    'tags': base_tags,
}

faq_list = {
    'operation_description': '## Список FAQ',
    'operation_summary': 'Получение Списока FAQ',
    'responses': {'200': FAQSerializer(many=True)},
    'tags': base_tags,
}