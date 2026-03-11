from api.v1.admin.ingredient.serializers import AdminUpdateIngredientCategorySectionSerializer, \
    AdminListIngredientCategorySectionSerializer

tags = ['admin']

ingredient_category_section_update = {
    'operation_description': '## Обновление блока категорий',
    'operation_summary': 'Обновление блока категорий',
    'request_body': AdminUpdateIngredientCategorySectionSerializer(many=False),
    'responses': {'200': AdminListIngredientCategorySectionSerializer(many=False)},
    'tags': tags,
}