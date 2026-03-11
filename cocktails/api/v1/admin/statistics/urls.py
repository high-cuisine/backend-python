from django.urls import path

from .views import AdminStatisticsView

urlpatterns = [
    path('', AdminStatisticsView.as_view(), name='admin-statistics'),
]
