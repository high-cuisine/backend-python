import logging
import os

from django.conf import settings

from services.base import BaseClient
from main_core import celery_app

logger = logging.getLogger(__name__)


class NotifyClient(BaseClient):
    BASE_URL = os.environ.get('NOTIFY_URL', '') + '/api/'
    AUTH_TOKEN = os.environ.get('NOTIFY_TOKEN')
    TIMEOUT = 5

    TYPE_BASE = 'base'
    TYPE_USER_QUESTION = 'user_question'

    QUEST_REQUEST_TEXT = 'Новая заявка на участие в курсе "{recipe}" от {quest_member}'

    @classmethod
    def create_notification(cls, user_id: int, notification_type: str, text: str, text_eng: str, **extra):
        data = dict(
            user_id=user_id,
            type=notification_type,
            text=text,
            text_eng=text_eng,
            extra=extra,
        )
        headers = {'Authorization': cls.AUTH_TOKEN}
        try:
            return cls.send_request('POST', 'notification/', data=data, headers=headers, verify=False)
        except ValueError as e:
            logger.exception(e)

    @classmethod
    def send_user_question(cls, user_id: int, text: str, text_eng: str, sender_name: str, email: str, quest: dict):
        return cls.create_notification(
            user_id,
            cls.TYPE_USER_QUESTION,
            text,
            text_eng,
            sender_name=sender_name,
            email=email,
            quest=quest
        )


@celery_app.task(name='notify.send_notification')
def send_notification(user_id: int, text: str, text_eng: str, **extra):
    # if settings.DEBUG:
    #     return
    NotifyClient.create_notification(user_id, NotifyClient.TYPE_BASE, text, text_eng, **extra)
