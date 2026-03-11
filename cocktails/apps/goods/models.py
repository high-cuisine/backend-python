import logging
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from base.fields import *
from base.models import BaseModel, CreatedUpdatedModel
from django.contrib.postgres.fields import ArrayField
from apps.user.models import User

__all__ = [
    'Goods',
    'Promo',
    'PurchasedPromo'
]

logger = logging.getLogger(__name__)


class Goods(CreatedUpdatedModel):
    name = models.TextField(db_index=True, null=True, blank=True, verbose_name='Название')
    product_id = models.PositiveBigIntegerField(db_index=True, null=True, blank=True, verbose_name='Айди товара')
    sku = models.PositiveBigIntegerField(null=True, blank=True, verbose_name='Поисковый индекс')
    description = models.TextField(null=True, blank=True, verbose_name='Описание')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Цена')
    photo = models.URLField(null=True, blank=True, verbose_name='Фото')
    link = models.URLField(null=True, blank=True, verbose_name='Ссылка')

    class Meta:
        ordering = ['id']
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return '{}'.format(self.name)


class Promo(CreatedUpdatedModel):
    name = models.CharField(max_length=255, db_index=True, verbose_name='Название')
    code = models.CharField(max_length=255, db_index=True, verbose_name='Код')
    description = models.TextField(null=True, blank=True, verbose_name='Описание')
    links = models.URLField(null=True, blank=True, verbose_name='Ссылка')
    cost = models.PositiveIntegerField(null=True, blank=True, verbose_name='Стоимость')

    class Meta:
        ordering = ['id']
        verbose_name = 'Промо'
        verbose_name_plural = 'Промо'

    def __str__(self):
        return '{}'.format(self.name)


class PurchasedPromo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    promo = models.ForeignKey(Promo, on_delete=models.CASCADE, verbose_name='Промо')
    purchased_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата покупки')

    class Meta:
        ordering = ['-purchased_at']
        verbose_name = 'Купленное промо'
        verbose_name_plural = 'Купленные промо'
        unique_together = ('user', 'promo')

    def __str__(self):
        return f'{self.user} - {self.promo}'
