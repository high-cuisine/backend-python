import logging

from django.db.models import QuerySet

from apps.goods.models import Goods
from main_core import celery_app
from services.ozon_api_client import OzonApiClient

logger = logging.getLogger(__name__)

__all__ = [
    'get_ozon_products',
]


@celery_app.task(bind=True, default_retry_delay=10, max_retries=10, name='goods.get_ozon_products')
def get_ozon_products(self, api_client: OzonApiClient = OzonApiClient):
    products: QuerySet[Goods] = Goods.objects.all()

    ids_list: list[int] = api_client.get_products_ids()
    new_products: list[Goods] = api_client.get_products(ids_list)

    products_ids: list[int] = [product.product_id for product in products]
    new_products_ids: list[int] = [new_product.product_id for new_product in new_products]

    for new_product in new_products:
        if new_product.product_id in products_ids:
            Goods.objects.filter(product_id=new_product.product_id).update(
                name=new_product.name,
                price=new_product.price,
                product_id=new_product.product_id,
                sku=new_product.sku,
                description=new_product.description,
                photo=new_product.photo,
                link=new_product.link
            )
        else:
            new_product.save()

    for product in products:
        if product.product_id not in new_products_ids:
            product.delete()
