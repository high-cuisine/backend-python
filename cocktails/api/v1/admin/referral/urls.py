from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReferralAdminViewSet


router = DefaultRouter()
router.register(r'', ReferralAdminViewSet, basename='admin-referrals')

urlpatterns = [
    path('', include(router.urls)),
]