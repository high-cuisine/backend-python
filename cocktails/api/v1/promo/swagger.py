from .serializers import *


tags = ['Promo']

promo_list = {
    'operation_description': '## Список промо',
    'operation_summary': 'Список промо',
    'responses': {'200': PromoListSerializer(many=True)},
    'tags': tags,
}

promo_retrieve = {
    'operation_description': '## Страница промо',
    'operation_summary': 'Получение промо',
    'responses': {'200': PromoSerializer()},
    'tags': tags,
}

promo_buy = {
    'operation_description': '## Покупка промо',
    'operation_summary': 'Покупка промо',
    'request_body': BuyPromoSerializer(),
    'responses': {'201': PromoCodeResponseSerializer()},
    'tags': tags,
}