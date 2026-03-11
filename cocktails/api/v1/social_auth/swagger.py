from .serializers import FacebookSocialAuthSerializer, GoogleSocialAuthSerializer

tags = ['Social Auth']

google_in = {
    'operation_description': 'Авторизация пользователя через google.',
    'operation_summary': 'Авторизация пользователя через google',
    'tags': tags,
    'request_body': GoogleSocialAuthSerializer,
    'responses': {'201': GoogleSocialAuthSerializer()},
}

facebook_in = {
    'operation_description': 'Авторизация пользователя через facebook.',
    'operation_summary': 'Авторизация пользователя через facebook',
    'tags': tags,
    'request_body': FacebookSocialAuthSerializer,
    'responses': {'201': FacebookSocialAuthSerializer()},
}
