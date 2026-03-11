from api.v1.admin.recipe.serializers import AdminCreateRecipeSerializer, AdminUpdateRecipeSerializer

tags = ['admin']

recipe_create = {
    'operation_description': '## Создание рецепта',
    'operation_summary': 'Создание рецепта',
    'request_body': AdminCreateRecipeSerializer(many=False),
    'responses': {'201': AdminCreateRecipeSerializer(many=False)},
    'tags': tags,
}

recipe_update = {
    'operation_description': '## Редактирование рецепта',
    'operation_summary': 'Редактирование рецепта',
    'request_body': AdminUpdateRecipeSerializer(many=False),
    'responses': {'200': AdminUpdateRecipeSerializer(many=False)},
    'tags': tags,
}