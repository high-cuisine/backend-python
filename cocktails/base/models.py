import re

from django.contrib.contenttypes.models import ContentType
from django.db import models, ProgrammingError, OperationalError
from django.urls import reverse
from django.utils.functional import classproperty
from django.utils.html import conditional_escape, format_html

from base.managers import ActiveManager
from base import utils
from base.utils import cached_classproperty


class BaseModel(models.Model):
    objects = models.Manager()

    class Meta:
        abstract = True

    @classproperty
    def app_label(cls):  # noqa
        return cls._meta.app_label  # noqa

    @classproperty
    def model_name(cls):  # noqa
        return cls._meta.model_name  # noqa

    @classproperty
    def verbose_name(cls):  # noqa
        return cls._meta.verbose_name  # noqa

    @classproperty
    def verbose_name_plural(cls):  # noqa
        return re.sub('^\d+\. ', '', cls._meta.verbose_name_plural)  # noqa

    @classmethod
    def get_index_url(cls, **kwargs):
        path = reverse(f'admin:{cls.app_label}_{cls.model_name}_changelist')
        return utils.site_url(path, **kwargs)

    @cached_classproperty
    def self_content_type_id(cls):  # noqa
        try:
            return ContentType.objects.get_for_model(cls).id
        except (ProgrammingError, OperationalError):
            return

    @cached_classproperty
    def content_type_id(cls):  # noqa
        return cls.self_content_type_id

    def get_url(self, **kwargs):
        path = reverse(f'admin:{self.app_label}_{self.model_name}_change', args=[self.pk])
        return utils.site_url(path, **kwargs)

    def get_link(self, title='', attr=None):
        if not self.pk:
            return '-'
        if not title and attr and hasattr(self, attr):
            title = getattr(self, attr)
        title = title or str(self)
        return format_html('<a href="{}" target="_blank">{}</a>', self.get_url(), conditional_escape(title))


class CreatedAtModel(BaseModel):
    created_at = models.DateTimeField(auto_now_add=True, blank=True, verbose_name='Создано')

    class Meta:
        abstract = True


class CreatedUpdatedModel(BaseModel):
    created_at = models.DateTimeField(auto_now_add=True, blank=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now_add=True, blank=True, verbose_name='Изменено')

    class Meta:
        abstract = True


class DateTimeModel(CreatedAtModel):
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    class Meta:
        abstract = True


class ActiveModel(BaseModel):
    active = models.BooleanField(default=True, verbose_name='Активно?')

    objects = models.Manager()
    active_objects = ActiveManager()

    class Meta:
        abstract = True
