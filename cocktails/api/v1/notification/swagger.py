from .serializers import NotificationSerializer

tags = ['notification']

notification_list = {
    'operation_description': '## Список уведомлений',
    'operation_summary': 'Список уведомлений',
    'responses': {'200': NotificationSerializer(many=True)},
    'tags': tags,
}

notification_retrieve = {
    'operation_description': '## Страница уведомления',
    'operation_summary': 'Получение уведомления',
    'responses': {'200': NotificationSerializer()},
    'tags': tags,
}

notification_read = {
    'operation_description': '## Прочтение уведомления',
    'operation_summary': 'Прочтение уведомления',
    'responses': {'201': NotificationSerializer()},
    'tags': tags,
}
