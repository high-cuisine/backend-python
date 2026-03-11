from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *


router = DefaultRouter()
router.register(r'faq', FAQViewSet, basename='faq')
router.register(r'documents', DocumentViewSet, basename='documents')
router.register(r'ads', AdvertisementViewSet, basename='advertisements')


urlpatterns = [
    path('upload_image/', ImageUploadView.as_view(), name='upload_image'),
    path('upload_file/', FileUploadView.as_view(), name='upload_file'),
    path('config/', ConfigAPIView.as_view(), name='config'),
    path('', include(router.urls)),
]
