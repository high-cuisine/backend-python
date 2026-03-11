from django.urls import include, path
from api.v1.admin.auth import views


web_patterns = [
    path('', views.AdminWebSignInView.as_view(), name='sign-in'),
]

urlpatterns = [
    path('sign-in/', include(web_patterns), name='web'),
]
