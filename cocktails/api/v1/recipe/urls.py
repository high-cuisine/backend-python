from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'section', IngredientCategorySectionViewSet)
router.register(r'category', IngredientCategoryViewSet)
router.register(r'ingredient', IngredientViewSet)
router.register(r'tool', ToolViewSet)
router.register(r'claim', ClaimViewSet, basename='claim_recipe')
router.register(r'', RecipeViewSet, basename='recipe')

urlpatterns = [
    path('', include(router.urls)),
]