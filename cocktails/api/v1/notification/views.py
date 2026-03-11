from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from .serializers import NotificationSerializer
from .swagger import notification_list, notification_retrieve, notification_read
from apps.user.models import Notification
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from api.base.permissions import IsActiveUser


class NotificationViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsActiveUser]

    def get_queryset(self):
        if self.request.user.is_anonymous:
            return self.queryset.none()
        else:
            return self.queryset.filter(user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @swagger_auto_schema(**notification_list)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(**notification_retrieve)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(**notification_read)
    @action(detail=False, methods=['post'])
    def read(self, request):
        notifications = self.get_queryset().filter(is_read=False)
        if notifications.exists():
            notifications.update(is_read=True)
            return Response({'status': 'All unread notifications marked as read'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'No unread notifications found'}, status=status.HTTP_404_NOT_FOUND)
