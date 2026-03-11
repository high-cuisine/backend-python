from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AdminPointViewSet, AdminPointConfigViewSet

router = DefaultRouter()
router.register(r'', AdminPointViewSet, basename='admin-point')
router.register(r'config', AdminPointConfigViewSet, basename='admin-point-config')

urlpatterns = [
    path('', include(router.urls)),
]