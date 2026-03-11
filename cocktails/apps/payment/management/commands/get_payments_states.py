import logging

from django.core.management.base import BaseCommand

from apps.payment.models import TinkoffPayment
from services.tinkoff import PaymentClient


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Обновление статуса по платежам'

    def handle(self, *args, **options):
        payments = TinkoffPayment.objects.filter(status__in=TinkoffPayment.STATE_STATUSES)
        success = 0
        for payment in payments:
            assert isinstance(payment, TinkoffPayment)
            response = PaymentClient.get_state(payment)
            if not response:
                continue

            try:
                data = response.json()
            except Exception as e:
                logger.error(f'Invalid Tinkoff get state response.\n'
                             f'URL: {response.url}\n'
                             f'Status: {response.status_code}\n'
                             f'Data: {response.text}')
                logger.exception(e)
                continue

            if response.status_code not in (200, 201) or not data['Success']:
                logger.error(f'Invalid Tinkoff get state response.\n'
                             f'URL: {response.url}\n'
                             f'Status: {response.status_code}\n'
                             f'Data: {data}')
                continue
            if payment.status == data['Status']:
                success += 1
                continue

            payment.status = data['Status']
            payment.message = data.get('Message')
            payment.error_code = data['ErrorCode']
            payment.success = data['Success']
            payment.save()
            if payment.success and payment.status == TinkoffPayment.STATUS_CONFIRMED:
                if payment.tries:
                    payment.user.profile.education_plan_limit += payment.tries
                    payment.user.profile.save(update_fields=['education_plan_limit'])

            success += 1

        total = payments.count()
        return f'Success: {success}\nFail: {total - success}\nTotal: {total}'
