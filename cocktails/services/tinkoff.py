import hashlib
import logging

from django.conf import settings

from apps.payment.models import TinkoffPayment
from services.base import BaseClient

logger = logging.getLogger(__name__)


class PaymentClient(BaseClient):
    BASE_URL = settings.TINKOFF_PAYMENT_URL
    TERMINAL_ID = settings.TINKOFF_TERMINAL_ID
    TERMINAL_PASSWORD = settings.TINKOFF_TERMINAL_PASSWORD
    TIMEOUT = 10
    ACCESS_TOKEN = settings.TINKOFF_PAYMENT_TOKEN

    @classmethod
    def init_payment(cls, payment: TinkoffPayment, success_url: str, fail_url: str):
        name = 'Генерация учебного плана'
        data = {
            'Amount': payment.amount,
            'Description': name,
            'OrderId': f'{settings.ENVIRONMENT}_staff_{payment.pk}',
            'TerminalKey': cls.TERMINAL_ID,
        }
        token_string = str(data['Amount']) + data['Description'] + data['OrderId'] + cls.TERMINAL_PASSWORD + \
            data['TerminalKey']
        token_hash = hashlib.sha256()
        token_hash.update(token_string.encode('utf-8'))
        token = token_hash.hexdigest()
        payment.token = token
        payment.save(update_fields=['token'])
        data.update({
            'SuccessURL': success_url,
            'FailURL': fail_url,
            'Token': token,
        })

        if payment.tries:
            shop_code = settings.TINKOFF_DEFAULT_SHOP_ID
            email = settings.TINKOFF_DEFAULT_EMAIL
        else:
            raise ValueError('Invalid payment type')

        data.update({
            'Shops': [{
                'ShopCode': shop_code,
                'Amount': payment.amount,
                'Name': name,
                'Fee': payment.fee,
            }],
            'Receipts': [
                {
                    'Email': email,
                    'ShopCode': shop_code,
                    'Taxation': 'osn',
                    'Items': [
                        {
                            'Name': name,
                            'Price': payment.amount,
                            'Quantity': 1,
                            'Amount': payment.amount,
                            'Tax': 'none',
                        }
                    ],
                }
            ]
        })

        return cls.send_request(
            'POST',
            'Init',
            data=data,
            full=True,
            headers={'Authorization': f'Bearer {cls.ACCESS_TOKEN}', 'Content-Type': 'application/json'},
        )

    @classmethod
    def get_state(cls, payment: TinkoffPayment):
        token_string = cls.TERMINAL_PASSWORD + payment.tinkoff_id + payment.terminal_key
        token_hash = hashlib.sha256()
        token_hash.update(token_string.encode('utf-8'))
        data = {
            'TerminalKey': payment.terminal_key,
            'PaymentId': payment.tinkoff_id,
            'Token': token_hash.hexdigest(),
        }
        return cls.send_request(
            'POST',
            'GetState',
            data=data,
            full=True,
            headers={'Authorization': f'Bearer {cls.ACCESS_TOKEN}', 'Content-Type': 'application/json'},
        )

    @classmethod
    def get_qr(cls, payment: TinkoffPayment):
        token_string = 'IMAGE' + cls.TERMINAL_PASSWORD + payment.tinkoff_id + payment.terminal_key
        token_hash = hashlib.sha256()
        token_hash.update(token_string.encode('utf-8'))
        data = {
            'TerminalKey': payment.terminal_key,
            'PaymentId': payment.tinkoff_id,
            'DataType': 'IMAGE',
            'Token': token_hash.hexdigest(),
        }
        return cls.send_request(
            'POST',
            'GetQr',
            data=data,
            full=True,
            headers={'Authorization': f'Bearer {cls.ACCESS_TOKEN}', 'Content-Type': 'application/json'},
        )

    @classmethod
    def cancel_payment(cls, payment: TinkoffPayment):
        data = {
            'PaymentId': payment.tinkoff_id,
            'TerminalKey': cls.TERMINAL_ID,
        }
        token_string = cls.TERMINAL_PASSWORD + data['PaymentId'] + data['TerminalKey']
        token_hash = hashlib.sha256()
        token_hash.update(token_string.encode('utf-8'))
        token = token_hash.hexdigest()
        data.update({
            'Shops': [{
                'ShopCode': payment.user.shop_code,
                'Amount': payment.amount,
                'Fee': payment.fee,
            }],
            'Token': token,
        })
        return cls.send_request(
            'POST',
            'Cancel',
            data=data,
            full=True,
            headers={'Authorization': f'Bearer {cls.ACCESS_TOKEN}', 'Content-Type': 'application/json'},
        )
