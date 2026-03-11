from django.contrib import admin
from apps.goods.models import *
from base.admin import BaseAdmin


@admin.register(Goods)
class GoodsAdmin(BaseAdmin):
    list_display = ('id', 'name', 'product_id', 'price', 'sku', 'description', 'photo', 'link')
    search_fields = ('name', 'link')
    ordering = ('id', )


@admin.register(Promo)
class PromoAdmin(BaseAdmin):
    list_display = ('id', 'name', 'code', 'description', 'links', 'cost')
    search_fields = ('name', )
    ordering = ('id', )


@admin.register(PurchasedPromo)
class PurchasedPromoAdmin(BaseAdmin):
    list_display = ('id', 'user', 'promo', 'purchased_at')
    search_fields = ('user__email', 'user__phone', 'promo__name')
    ordering = ('id', )