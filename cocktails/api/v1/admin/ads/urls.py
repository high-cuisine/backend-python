from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.v1.admin.ads.views import AdminADSViewSet

router = DefaultRouter()
router.register(r'', AdminADSViewSet, basename='admin-ads')

urlpatterns = [
    path('', include(router.urls)),
]
