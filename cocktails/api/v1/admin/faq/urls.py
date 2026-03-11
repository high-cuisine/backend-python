from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.v1.admin.faq.views import AdminFAQViewSet

router = DefaultRouter()
router.register(r'', AdminFAQViewSet, basename='admin-FAQ')

urlpatterns = [
    path('', include(router.urls)),
]
