from drf_yasg import openapi
from api.v1.auth.serializers import *

tags = ['Auth']
reg_tags = ['User Registration']
reset_tags = ['Password reset']

web_sign_in = {
    'operation_description': 'Авторизация пользователя по токену.',
    'operation_summary': 'Авторизация',
    'tags': reg_tags,
    'request_body': WebSignInRequestSerializer,
    'responses': {'201': WebSignInResponseSerializer()},
}

reset_password = {
    'operation_description': 'Запрос на сброс пароля. Отправка кода подтверждения на email.',
    'operation_summary': 'Сброс пароля',
    'tags': reset_tags,
    'request_body': ResetPasswordSerializer,
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
                'application/json': {'error': 'Пользователь с таким email не найден'},
            }
        )
    }
}

confirm_reset_code = {
    'operation_description': 'Подтверждение кода для сброса пароля.',
    'operation_summary': 'Подтверждение кода сброса пароля',
    'tags': reset_tags,
    'request_body': ConfirmResetCodeSerializer,
    'responses': {
        '200': openapi.Response(
            description='Код успешно подтвержден',
            examples={
                'application/json': {'detail': 'Code verified successfully'},
            }
        ),
        '400': openapi.Response(
            description='Ошибка при подтверждении кода',
            examples={
                'application/json': {'error': 'Неверный код или email'},
            }
        )
    }
}

confirm_password = {
    'operation_description': 'Подтверждение нового пароля после успешной верификации кода.',
    'operation_summary': 'Подтверждение нового пароля',
    'tags': reset_tags,
    'request_body': ConfirmPasswordSerializer,
    'responses': {
        '201': openapi.Response(
            description='Пароль успешно сброшен',
            examples={
                'application/json': {'detail': 'Password reset successfully'},
            }
        ),
        '400': openapi.Response(
            description='Ошибка при сбросе пароля',
            examples={
                'application/json': {
                    'errors': ['Пароли не совпадают'],
                    'code': ['Неверный код'],
                },
            }
        )
    }
}

email_verification_request = {
    'operation_description': 'Запрос кода подтверждения для email пользователя.',
    'operation_summary': 'Запрос кода подтверждения email',
    'tags': reg_tags,
    'request_body': EmailVerificationRequestSerializer,
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

code_verification = {
    'operation_description': 'Подтверждение кода верификации email.',
    'operation_summary': 'Подтверждение кода верификации',
    'tags': reg_tags,
    'request_body': CodeVerificationSerializer,
    'responses': {
        '200': openapi.Response(
            description='Email успешно подтвержден',
            examples={
                'application/json': {'detail': 'Email verified successfully'},
            }
        ),
        '400': openapi.Response(
            description='Ошибка при подтверждении кода',
            examples={
                'application/json': {'error': 'Неверный код или email'},
            }
        )
    }
}

user_registration = {
    'operation_description': 'Регистрация нового пользователя.',
    'operation_summary': 'Регистрация пользователя',
    'tags': reg_tags,
    'request_body': UserRegistrationSerializer,
    'responses': {
        '201': openapi.Response(
            description='Пользователь успешно зарегистрирован',
            examples={
                'application/json': {'detail': 'User registered successfully'},
            }
        ),
        '400': openapi.Response(
            description='Ошибка при регистрации пользователя',
            examples={
                'application/json': {'error': 'Некорректные данные для регистрации'},
            }
        )
    }
}
