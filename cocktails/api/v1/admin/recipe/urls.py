from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.v1.admin.recipe.views import (
    AdminPendingRecipeViewSet,
    AdminApprovedRecipeViewSet,
    AdminRejectedRecipeViewSet,
    AdminUploadUrlView, AdminDeleteObjectView
)

router = DefaultRouter()
router.register(r'pending', AdminPendingRecipeViewSet, basename='admin-pending-recipe')
router.register(r'approved', AdminApprovedRecipeViewSet, basename='admin-approved-recipe')
router.register(r'rejected', AdminRejectedRecipeViewSet, basename='admin-rejected-recipe')

urlpatterns = [
    path('', include(router.urls)),
    path('video-upload-url/', AdminUploadUrlView.as_view(), name='admin-upload-url'),
    path('video-delete/<str:s3_key>/', AdminDeleteObjectView.as_view(), name='admin-delete-video')
]
