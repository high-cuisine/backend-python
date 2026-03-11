from django.contrib import admin
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from apps.common.models import *
from base.admin import BaseAdmin

admin.site.register(Permission)
admin.site.register(ContentType)


@admin.register(Ads)
class AdsAdmin(BaseAdmin):
    list_display = ['title', 'description', 'target_audience', 'images', 'url']
    search_fields = ['title', 'target_audience', 'url']
    list_filter = (
        'target_audience',
    )


@admin.register(FAQ)
class FAQAdmin(BaseAdmin):
    list_display = ['question', 'answer']
    search_fields = ['question', 'answer']


@admin.register(Document)
class DocumentAdmin(BaseAdmin):
    list_display = ['title', 'document_type', 'file']
    search_fields = ['title', 'document_type']
    list_filter = (
        'document_type',
    )


@admin.register(Config)
class ConfigAdmin(BaseAdmin):
    list_display = ['code', 'name', 'value']
    search_fields = ['code', 'name', 'value', 'description']


@admin.register(Mailing)
class MailingAdmin(BaseAdmin):
    list_display = ['title', 'title_eng', 'description', 'description_eng', 'url']
    search_fields = ['title', 'title_eng', 'url']
