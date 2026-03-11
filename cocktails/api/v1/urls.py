from django.conf import settings
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny

urlpatterns = [
    path('auth/', include('api.v1.auth.urls')),
    path('auth/social/', include('api.v1.social_auth.urls')),
    path('common/', include('api.v1.common.urls')),
    path('recipe/', include('api.v1.recipe.urls')),
    path('goods/', include('api.v1.goods.urls')),
    path('promo/', include('api.v1.promo.urls')),
    path('profile/', include('api.v1.profile.urls')),
    path('admin/', include('api.v1.admin.urls')),
    path('notification/', include('api.v1.notification.urls')),
]

if settings.ENVIRONMENT != 'production':
    api_v1_schema_view = get_schema_view(
        openapi.Info(
            title='Cocktails API v1',
            default_version='v1',
            description='Cocktails API v1',
        ),

        public=True,
        permission_classes=[AllowAny],
    )

    urlpatterns = [
        path('swagger/', api_v1_schema_view.with_ui("swagger", cache_timeout=0)),
    ] + urlpatterns
