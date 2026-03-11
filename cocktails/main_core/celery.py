from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main_core.settings')

#main_core или cocktails
celery_app = Celery('main_core')

celery_app.config_from_object('django.conf:settings', namespace='CELERY')

celery_app.autodiscover_tasks()

# if not settings.DEBUG:
#     schedule = {
#         'calculate_quests_progress': {
#             'task': 'recipe.calculate_quests_progress',
#             'schedule': crontab(hour='0', minute='1'),
#         },
#         'calculate_quest_members_progress': {
#             'task': 'recipe.calculate_quest_members_progress',
#             'schedule': crontab(hour='0', minute='30'),
#         },
#         'sync_hh_industries': {
#             'task': 'vacancy.sync_hh_industries',
#             'schedule': crontab(minute='0', hour='*/2'),
#         },
#         'get_payments_states': {
#             'task': 'recipe.get_payments_states',
#             'schedule': crontab(minute='*/5'),
#         },
#         'deny_expired_quest_members': {
#             'task': 'recipe.deny_expired_quest_members',
#             'schedule': crontab(hour='0', minute='5'),
#         },
#     }
#
#     if settings.ENVIRONMENT == 'production':
#         schedule['update_dumps'] = {
#             'task': 'storage.update_dumps',
#             'schedule': crontab(hour='6,18', minute='0'),
#         }
#
#     celery_app.conf.beat_schedule = schedule

celery_app.conf.timezone = 'Europe/Moscow'
