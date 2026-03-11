from django.urls import include, path
from api.v1.auth import views

registration_patterns = [
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('verify-email/', views.EmailVerificationRequestView.as_view(), name='verify-email'),
    path('confirm-code/', views.CodeVerificationView.as_view(), name='confirm-code'),
]

web_patterns = [
    path('sign-in/', views.WebSignInView.as_view(), name='sign-in'),
]

password_patterns = [
    path('reset/', views.ResetPasswordView.as_view(), name='reset-password'),
    path('reset-code/', views.ConfirmResetCodeView.as_view(), name='code-confirm'),
    path('confirm/', views.ConfirmPasswordView.as_view(), name='confirm-password'),
]

urlpatterns = [
    path('web/', include(web_patterns), name='web'),
    path('password/', include(password_patterns), name='password'),
    path('auth/', include(registration_patterns), name='auth'),
]
