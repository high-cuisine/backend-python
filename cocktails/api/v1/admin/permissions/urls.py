from django.urls import path

from api.v1.admin.permissions.views import AdminPermissionsView

urlpatterns = [
    path('', AdminPermissionsView.as_view(), name='admin-permissions'),
]