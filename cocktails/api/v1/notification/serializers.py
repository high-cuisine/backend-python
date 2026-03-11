from rest_framework import serializers
from apps.user.models import Notification

__all__ = [
    'NotificationSerializer',
]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'topik', 'message', 'is_read', 'created_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')

        if request:
            user_language = request.headers.get('User-Language', 'rus')

            if user_language == 'eng':
                representation['topik'] = instance.topik_eng
                representation['message'] = instance.message_eng
            else:
                representation['topik'] = instance.topik
                representation['message'] = instance.message

        return representation
