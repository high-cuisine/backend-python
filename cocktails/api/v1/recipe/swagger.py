from .serializers import *
from api.base.swagger import filter_params
from drf_yasg import openapi

tags = ['recipe']

ingredient_category_block_list = {
    'operation_description': '## Список секция категорий',
    'operation_summary': 'Список секция категорий',
    'responses': {'200': IngredientCategorySectionSerializer()},
    'tags': tags,
    'manual_parameters': [
        openapi.Parameter(
            'q',
            openapi.IN_QUERY,
            description="Поиск по названию ингредиентов",
            type=openapi.TYPE_STRING
        ),
        openapi.Parameter(
            'ingredients',
            openapi.IN_QUERY,
            description="Фильтрация по ID ингредиентов (через запятую, например: 1,2,3)",
            type=openapi.TYPE_STRING
        ),
        openapi.Parameter(
            'alc',
            openapi.IN_QUERY,
            description="Фильтрация по алкогольности (1 - алкогольные, 0 - безалкогольные)",
            type=openapi.TYPE_STRING
        ),
        openapi.Parameter(
            'withRecipesOnly',
            openapi.IN_QUERY,
            description="Показать только ингредиенты и подкатегории, которые используются в коктейлях. Если не указан - показываются все ингредиенты.",
            type=openapi.TYPE_STRING
        ),
    ]
}

ingredient_retrieve = {
    'operation_description': '## Страница ингредиента',
    'operation_summary': 'Получение страницы ингредиента',
    'responses': {'200': IngredientSerializer()},
    'tags': tags,
}

ingredient_category_list = {
    'operation_description': '## Список категорий ингредиентов',
    'operation_summary': 'Получение списока категорий ингредиентов',
    'responses': {'200': IngredientCategorySerializer(many=True)},
    'tags': tags,
}

tool_list = {
    'operation_description': '## Список инструментов',
    'operation_summary': 'Получение списока инструментов',
    'responses': {'200': ViewToolSerializer(many=True)},
    'tags': tags,
}

tool_retrieve = {
    'operation_description': '## Страница инструмента',
    'operation_summary': 'Получение страницы инструмента',
    'responses': {'200': ViewToolSerializer()},
    'tags': tags,
}

recipe_selection = {
    'operation_description': '## Поиск рецепта по ингредиентам',
    'operation_summary': 'Поиск рецепта по ингредиентам',
    'request_body': SelectionRecipeSerializer,
    'responses': {'200': SelectionRecipeSerializer(many=True)},
    'tags': tags,
}

recipe_list = {
    'operation_description': '## Список рецепта',
    'operation_summary': 'Получение Списока рецепта',
    'responses': {'200': RecipeListSerializer(many=True)},
    'tags': tags,
    'manual_parameters': filter_params,
}

recipe_update = {
    'operation_description': '## Изменение рецепта',
    'operation_summary': 'Изменение рецепта',
    'request_body': UpdateRecipeSerializer(),
    'responses': {'200': RecipeDetailSerializer()},
    'tags': tags,
}

recipe_delete = {
    'operation_description': '## Удаление рецепта',
    'operation_summary': 'Удаление рецепта',
    'responses': {'200': 'Deleted'},
    'tags': tags,
}

recipe_create = {
    'operation_description': '## Создание рецепта',
    'operation_summary': 'Создание рецепта',
    'request_body': CreateRecipeSerializer(),
    'responses': {'201': RecipeDetailSerializer()},
    'tags': tags,
}

recipe_retrieve = {
    'operation_description': '## Страница рецепта',
    'operation_summary': 'Получение страницы рецепта',
    'responses': {'200': RecipeDetailSerializer()},
    'tags': tags,
}
