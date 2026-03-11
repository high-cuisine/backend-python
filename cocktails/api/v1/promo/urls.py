from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PromoViewSet

router = DefaultRouter()
router.register('', PromoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]