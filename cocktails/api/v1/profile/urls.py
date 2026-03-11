from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *


user_list = UserViewSet.as_view({
    'get': 'retrieve'
})

router = DefaultRouter()
router.register(r'recipe', UserRecipeViewSet, basename='user-recipe')
router.register(r'favorite', FavoriteUserRecipeViewSet, basename='favorite-user-recipe')
router.register(r'referral', ReferralViewSet, basename='referral-user')


email_change_patterns = [
    path('verify/', EmailVerificationCodeView.as_view(), name='verify-new-email'),
    path('confirm/', ConfirmEmailView.as_view(), name='confirm-email'),
    path('confirm-new/', ConfirmNewEmailView.as_view(), name='confirm-new-email'),
]

# router.register(r'notifications', UserNotificationViewSet, basename='user-notifications')

urlpatterns = [
    path('', user_list, name='user-profile'),
    path('', include(router.urls)),
    path('change-email/', include(email_change_patterns), name='change-email'),
]