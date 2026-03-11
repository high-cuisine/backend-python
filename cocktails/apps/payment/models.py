from django.db import models

from apps.user.models import User
from base.fields import ForeignKey
from base.models import DateTimeModel


__all__ = [
    'TinkoffPayment',
]


class TinkoffPayment(DateTimeModel):
    TYPE_EDUCATION_PLAN = 'plan'
    TYPES = (
        (TYPE_EDUCATION_PLAN, 'Генерация учебного плана'),
    )

    STATUS_CREATED = 'CREATED'
    STATUS_NEW = 'NEW'
    STATUS_CANCELED = 'CANCELED'
    STATUS_DEADLINE_EXPIRED = 'DEADLINE_EXPIRED'
    STATUS_FORM_SHOWED = 'FORM_SHOWED'
    STATUS_AUTHORIZING = 'AUTHORIZING'
    STATUS_REJECTED = 'REJECTED'
    STATUS_3DS_CHECKING = '3DS_CHECKING'
    STATUS_3DS_CHECKED = '3DS_CHECKED'
    STATUS_AUTH_FAIL = 'AUTH_FAIL'
    STATUS_PAY_CHECKING = 'PAY_CHECKING'
    STATUS_AUTHORIZED = 'AUTHORIZED'
    STATUS_REVERSING = 'REVERSING'
    STATUS_REVERSED = 'REVERSED'
    STATUS_CONFIRMING = 'CONFIRMING'
    STATUS_CONFIRM_CHECKING = 'CONFIRM_CHECKING'
    STATUS_CONFIRMED = 'CONFIRMED'
    STATUS_REFUNDING = 'REFUNDING'
    STATUS_ASYNC_REFUNDING = 'ASYNC_REFUNDING'
    STATUS_REFUNDED = 'REFUNDED'
    STATUS_PARTIAL_REFUNDED = 'PARTIAL_REFUNDED'
    STATUSES = (
        (STATUS_CREATED, 'Платеж зарегистрирован в шлюзе, но его обработка в процессинге не начата'),
        (STATUS_NEW, 'Инициализирован'),
        (STATUS_CANCELED, 'Отменен'),
        (STATUS_DEADLINE_EXPIRED, 'Время сессии истекло'),
        (STATUS_FORM_SHOWED, 'Покупатель переправлен на страницу оплаты'),
        (STATUS_AUTHORIZING, 'Аутентификация покупателя'),
        (STATUS_REJECTED, 'Отклонено банком'),
        (STATUS_3DS_CHECKING, 'Начало аутентификация 3-D Secure'),
        (STATUS_3DS_CHECKED, 'Завершение аутентификации 3-D Secure'),
        (STATUS_AUTH_FAIL, 'Не пройдена аутентификация 3-D Secure'),
        (STATUS_PAY_CHECKING, 'Платеж обрабатывается'),
        (STATUS_AUTHORIZED, 'Средства заблокированы, но не списаны'),
        (STATUS_REVERSING, 'Начало отмены блокировки средств'),
        (STATUS_REVERSED, 'Денежные средства разблокированы'),
        (STATUS_CONFIRMING, 'Начало списания денежных средств'),
        (STATUS_CONFIRM_CHECKING, 'Платеж обрабатывается'),
        (STATUS_CONFIRMED, 'Денежные средства списаны'),
        (STATUS_REFUNDING, 'Начало возврата денежных средств'),
        (STATUS_ASYNC_REFUNDING, 'Обработка возврата денежных средств по QR'),
        (STATUS_REFUNDED, 'Произведен возврат денежных средств'),
        (STATUS_PARTIAL_REFUNDED, 'Произведен частичный возврат денежных средств'),
    )
    STATE_STATUSES = (STATUS_NEW, STATUS_FORM_SHOWED, STATUS_AUTHORIZING, STATUS_3DS_CHECKING, STATUS_3DS_CHECKED,
                      STATUS_AUTH_FAIL, STATUS_PAY_CHECKING, STATUS_AUTHORIZED, STATUS_REVERSING, STATUS_CONFIRMING,
                      STATUS_CONFIRM_CHECKING, STATUS_REFUNDING)

    INIT_STATUSES = (STATUS_AUTHORIZING, STATUS_3DS_CHECKING, STATUS_3DS_CHECKED, STATUS_PAY_CHECKING,
                     STATUS_AUTHORIZED, STATUS_CONFIRMING, STATUS_CONFIRM_CHECKING, STATUS_CONFIRMED)

    user = ForeignKey(User, related_name='tinkoff_payments')

    # объекты оплаты
    tries = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Количество попыток')
    type = models.CharField(max_length=6, choices=TYPES, default=TYPE_EDUCATION_PLAN, verbose_name='Тип')
    status = models.CharField(max_length=17, choices=STATUSES, default=STATUS_CREATED, verbose_name='Статус')
    terminal_key = models.CharField(max_length=50, verbose_name='Идентификатор терминала')
    description = models.CharField(max_length=140, verbose_name='Краткое описание')
    tinkoff_id = models.CharField(max_length=255, verbose_name='ID транзакции в системе банка', null=True, blank=True)
    payment_url = models.URLField(blank=True, null=True, verbose_name='Ссылка на платежную форму')
    amount = models.PositiveIntegerField(verbose_name='Сумма в копейках')
    token = models.CharField(max_length=64, verbose_name='Токен')
    error_code = models.CharField(max_length=10, blank=True, null=True, verbose_name='Код ошибки')
    message = models.TextField(blank=True, null=True, verbose_name='Описание ошибки')
    success = models.BooleanField(blank=True, null=True, verbose_name='Выполнение платежа')
    fee = models.PositiveIntegerField(default=0, verbose_name='Размер комиссии в копейках')

    class Meta:
        verbose_name = 'Платеж через Tinkoff'
        verbose_name_plural = 'Платежи через Tinkoff'
