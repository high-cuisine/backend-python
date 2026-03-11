from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.v1.admin.mailing.views import AdminMailingViewSet

router = DefaultRouter()
router.register(r'', AdminMailingViewSet, basename='admin-mailing')

urlpatterns = [
    path('', include(router.urls)),
]
