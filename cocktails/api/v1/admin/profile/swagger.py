
from api.v1.admin.profile.serializers import AdminUserCreateSerializer, AdminUserUpdateSerializer, AdminUserSerializer

tags = ['admin']


profile_create = {
    'operation_description': '## Создание пользователя',
    'operation_summary': 'Создание пользователя',
    'request_body': AdminUserCreateSerializer(),
    'responses': {'201': AdminUserSerializer(many=False)},
    'tags': tags,
}

profile_update = {
    'operation_description': '## Редактирование пользователя',
    'operation_summary': 'Редактирование пользователя',
    'request_body': AdminUserUpdateSerializer(),
    'responses': {'201': AdminUserSerializer(many=False)},
    'tags': tags,
}
