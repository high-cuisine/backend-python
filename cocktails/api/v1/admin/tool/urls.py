from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.admin.tool.views import AdminToolViewSet

router = DefaultRouter()
router.register(r'', AdminToolViewSet, basename='admin-tool')

urlpatterns = [
    path('', include(router.urls)),
]