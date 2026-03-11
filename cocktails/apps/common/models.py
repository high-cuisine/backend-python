from email.policy import default

from django.db import models
from django.db.models import Manager
from django.contrib.postgres.fields import ArrayField
from base.models import BaseModel, CreatedUpdatedModel
from base.utils import Memoized


__all__ = [
    'Config',
    'Ads',
    'FAQ',
    'Document',
    'Mailing',
]


class Config(BaseModel):
    code = models.CharField(max_length=128, verbose_name='Код')
    name = models.CharField(max_length=255, verbose_name='Название')
    value = models.TextField(verbose_name='Значение')
    description = models.TextField(default='', blank=True, verbose_name='Описание')

    objects = Manager()

    class Meta:
        verbose_name = 'Конфигурация'
        verbose_name_plural = 'Конфигурации'

    @classmethod
    @Memoized()
    def get_all(cls):
        return dict((item.code, item.value) for item in cls.objects.all())

    @classmethod
    def get(cls, code):
        return cls.get_all()[code]


class Ads(CreatedUpdatedModel):
    TARGET_AUDIENCE_CHOICES = [
        ('ALL', 'All'),
        ('MEN', 'Men'),
        ('WOMEN', 'Women')
    ]

    title = models.CharField(max_length=255, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    images = models.FileField(upload_to='ads/', verbose_name='Изображение')
    target_audience = models.CharField(
        max_length=10,
        choices=TARGET_AUDIENCE_CHOICES,
        default='ALL',
        verbose_name='Таргет'
    )
    url = models.URLField(null=True, blank=True, verbose_name='Ссылка')

    class Meta:
        verbose_name = 'Реклама'
        verbose_name_plural = 'Рекламы'

    def __str__(self):
        return self.title


class FAQ(CreatedUpdatedModel):
    question = models.CharField(max_length=255, verbose_name='Вопрос')
    answer = models.TextField(verbose_name='Ответ')

    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'

    def __str__(self):
        return self.question


class Document(CreatedUpdatedModel):
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    document_type = models.CharField(max_length=50, verbose_name='Тип')
    file = models.FileField(upload_to='documents/', verbose_name='Файл')

    class Meta:
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'

    def __str__(self):
        return self.title


class Mailing(CreatedUpdatedModel):
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    title_eng = models.CharField(max_length=255, verbose_name='Заголовок на ENG', default='')
    description_eng = models.TextField(verbose_name='Описание на ENG', default='')
    url = models.URLField(null=True, blank=True, verbose_name='Ссылка')

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'

    def __str__(self):
        return self.title
