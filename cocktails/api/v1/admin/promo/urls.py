from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PromoAdminViewSet, PromoPurchasedAdminViewSet

router = DefaultRouter()
router.register(r'purchased', PromoPurchasedAdminViewSet, basename='admin-purchased-promo')
router.register(r'', PromoAdminViewSet, basename='admin-promo')

urlpatterns = [
    path('', include(router.urls)),
]
