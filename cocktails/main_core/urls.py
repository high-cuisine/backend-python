from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from rest_framework.authentication import TokenAuthentication

admin.site.site_header = 'Cocktails Corp'
admin.site.site_title = 'Cocktails Corp'

urlpatterns = [
    path('api/', include('api.urls'), name='api'),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/celery-progress/', include('celery_progress.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.ENVIRONMENT != 'production':
    schema_view = get_schema_view(
        openapi.Info(
            title='Cocktails',
            default_version='v1',
            description='API',
        ),
        url='',
        public=True,
        permission_classes=[permissions.AllowAny],
        authentication_classes=[TokenAuthentication],
    )

    urlpatterns = [
        path('swagger/', schema_view.with_ui("swagger", cache_timeout=0)),
    ] + urlpatterns
