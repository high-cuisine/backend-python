from .serializers import *


tags = ['Goods']


goods_list = {
    'operation_description': '## Список товаров',
    'operation_summary': 'Получение списока товаров',
    'responses': {'200': GoodsSerializer(many=True)},
    'tags': tags,
}

goods_retrieve = {
    'operation_description': '## Страница товара',
    'operation_summary': 'Получение страницы товара',
    'responses': {'200': GoodsSerializer()},
    'tags': tags,
}