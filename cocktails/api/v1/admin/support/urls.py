from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdminTicketViewSet


router = DefaultRouter()
router.register(r'', AdminTicketViewSet, basename='admin-sup')

urlpatterns = [
    path('', include(router.urls)),
]