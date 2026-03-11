import logging

import requests
from django.conf import settings
from requests import Response

from apps.goods.models import Goods

logger = logging.getLogger(__name__)


class OzonApiClient:
    BASE_URL: str = settings.OZON_BASE_URL
    headers: dict = {
        'Client-Id': settings.OZON_CLIENT_ID,
        'Api-Key': settings.OZON_API_KEY
    }

    @classmethod
    def get_products_ids(cls) -> list[int]:
        body: dict = {
            "filter": {"visibility": "ALL"},
            "limit": 1000
        }
        list_ids: list[int] = []

        response: Response = requests.post(f'{cls.BASE_URL}/v3/product/list', json=body, headers=cls.headers)
        data: dict = response.json()

        items: list[dict] = data['result']['items']
        for item in items:
            if item['has_fbo_stocks'] is True:
                list_ids.append(item['product_id'])

        return list_ids

    @classmethod
    def get_products(cls, list_ids: list[int]) -> list[Goods]:
        body: dict = {"product_id": list_ids}
        result_products: list[Goods] = []

        response: Response = requests.post(f'{cls.BASE_URL}/v3/product/info/list', json=body, headers=cls.headers)
        data: dict = response.json()

        items: list[dict] = data['items']
        for item in items:
            try:
                if item['statuses']['status_name'] == 'Продается' and item['description_category_id'] != 17028761:
                    sku: int = item['sources'][0]['sku']
                    result_products.append(
                        Goods(
                            name=item['name'],
                            product_id=item['id'],
                            sku=sku,
                            description=item['name'],
                            price=item['marketing_price'],
                            photo=item['primary_image'][-1],
                            link=f'https://www.ozon.ru/product/{sku}'
                        )
                    )
            except Exception as e:
                logger.exception(e)
                continue

        return result_products
