from api.v1.profile.serializers import ReferralSerializer, ConfirmEmailSerializer, EmailSendCodeSerializer, ConfirmNewEmailSerializer
from api.v1.recipe.serializers import RecipeDetailSerializer
from drf_yasg import openapi

tags = ['profile']

recipe_pending= {
    'operation_description': '## Отправить рецепт на рассмотрение',
    'operation_summary': 'Отправить рецепт на рассмотрение',
    'responses': {'200': RecipeDetailSerializer()},
    'tags': tags,
}

user_id = dict(
    operation_description='## Получения ID юзера по токену.\nИспользуется другими сервисами для авторизации.',
    operation_summary='Получения ID юзера по токену',
    tags=tags,
)

profile_destroy = {
    'operation_description': '## Удаление аккаунта пользователя',
    'operation_summary': 'Удаление аккаунта пользователя',
    'tags': tags,
}

get_referral = {
    'operation_description': '## Получить реферальный код',
    'operation_summary': 'Получить реферальный код',
    'responses': {'201': ReferralSerializer()},
    'tags': tags,
}


email_verification = {
    'operation_description': 'Запрос кода подтверждения для email.',
    'operation_summary': 'Запрос кода подтверждения email',
    'tags': tags,
    'request_body': EmailSendCodeSerializer,
    'responses': {
        '200': openapi.Response(
            description='Код подтверждения успешно отправлен на email',
            examples={
                'application/json': {'detail': 'Verification code sent to email'},
            }
        ),
        '400': openapi.Response(
            description='Ошибка при отправке кода подтверждения',
            examples={
                'application/json': {'error': 'Этот email уже используется'},
            }
        )
    }
}


confirm_email = {
    'operation_description': 'Подтверждение почты.',
    'operation_summary': 'Подтверждение почты',
    'tags': tags,
    'request_body': ConfirmEmailSerializer,
    'responses': {
        '201': openapi.Response(
            description='Почта успешно изменена',
            examples={
                'application/json': {'detail': 'Verification code sent to new email'},
            }
        ),
        '400': openapi.Response(
            description='Ошибка при смене почты',
            examples={
                'application/json': {
                    'code': ['Неверный код'],
                },
            }
        )
    }
}


confirm_new_email = {
    'operation_description': 'Подтверждение новой почты.',
    'operation_summary': 'Подтверждение новой почты',
    'tags': tags,
    'request_body': ConfirmNewEmailSerializer,
    'responses': {
        '201': openapi.Response(
            description='Почта успешно изменена',
            examples={
                'application/json': {'detail': 'Email successfully change'},
            }
        ),
        '400': openapi.Response(
            description='Ошибка при смене почты',
            examples={
                'application/json': {
                    'code': ['Неверный код'],
                },
            }
        )
    }
}