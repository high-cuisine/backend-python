from django.core.management import call_command

from main_core.celery import celery_app


__all__ = [
    'get_payments_states',
]


@celery_app.task(name='recipe.get_payments_states')
def get_payments_states():
    return call_command('get_payments_states')
