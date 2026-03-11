from rest_framework import serializers
from apps.channel.models import Ticket

__all__ = [
    'AdminTicketListSerializer',
    'AdminUserListSerializer'
]

from apps.user.models import User


class AdminUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'phone', 'avatar']


class AdminTicketListSerializer(serializers.ModelSerializer):
    user = AdminUserListSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'user', 'subject', 'description', 'status', 'created_at']
        read_only_fields = ['user', 'subject', 'description', 'created_at']