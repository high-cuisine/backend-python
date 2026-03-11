from django.contrib import admin

from apps.payment.models import *
from base.admin import BaseAdmin


@admin.register(TinkoffPayment)
class TinkoffPaymentAdmin(BaseAdmin):
    list_display = ('id', 'type', 'amount', 'fee', 'created_at', 'status')
    list_filter = (
        'type',
        'success',
        'status',
    )
    readonly = True

    def get_fields(self, request, obj=None):
        return ['created_at'] + list(super().get_fields(request, obj))
