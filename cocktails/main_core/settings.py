import os
from datetime import timedelta

import openai
import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.environ.get('SECRET_KEY')
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
SOCIAL_PASSWORD = os.environ.get('SOCIAL_PASSWORD')

DEBUG = os.environ.get('DEBUG', 'false').lower() in ('true', '1', 't')

ALLOWED_HOSTS = ['*', 'mrbarmister.pro', 'www.mrbarmister.pro']
BASE_URL = os.environ.get('BASE_URL')

CORE_APPS = [
    'rest_framework',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

PLUGIN_APPS = [
    'corsheaders',
    'django_filters',
    'rest_framework.authtoken',
    'django_celery_beat',
    'django_celery_results',
    'django_extensions',
    'drf_yasg',
    'django_admin_listfilter_dropdown',
    'rangefilter',
    'import_export',
    'nested_inline',
    'channels',
    'djangochannelsrestframework'
]

LOCAL_APPS = [
    'apps.common.apps.CommonConfig',
    'apps.reaction.apps.ReactionConfig',
    'apps.user.apps.UserConfig',
    'apps.payment.apps.PaymentConfig',
    'apps.recipe.apps.RecipesConfig',
    'apps.goods.apps.GoodsConfig',
    'apps.channel.apps.ChannelConfig',
    'apps.signal.apps.SignalConfig',
]

INSTALLED_APPS = CORE_APPS + PLUGIN_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'main_core.common.DisableCSRFMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",
]

ROOT_URLCONF = 'main_core.urls'

#Каналы
ASGI_APPLICATION = 'main_core.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    }
}
#

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'main_core.wsgi.application'

DATABASES = {
    "default": {
        "ENGINE": 'django.db.backends.postgresql_psycopg2',
        "NAME": os.environ.get("POSTGRES_DB"),
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
        "HOST": os.environ.get("POSTGRES_HOST"),
        "PORT": os.environ.get("POSTGRES_PORT"),
        "CONN_MAX_AGE": 0,
    }
}

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = False

USE_TZ = True

DATETIME_FORMAT = 'Y-m-d H:i'
DATE_FORMAT = 'Y-m-d'

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
AUTH_USER_MODEL = 'user.User'
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login'

EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 25))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL")
EMAIL_TIMEOUT = 15
EMAIL_USE_SSL = int(os.environ.get("EMAIL_USE_SSL", 0))
EMAIL_USE_TLS = int(os.environ.get("EMAIL_USE_TLS", 1))
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'api.base.permissions.IsActiveUser',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
}

CORS_ORIGIN_WHITELIST = (
    'http://localhost:3000',
    'http://localhost:8080',
    'http://127.0.0.1:3000',
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'https://corp.cocktails.ru',
    'https://main.cocktails.ru',
    'https://staff.cocktails.ru',
    'https://staff.cocktails.pro',
    'https://corp.cocktails.pro',
    'http://staff.cocktails.pro',
    'http://corp.cocktails.pro',
    'https://notify.cocktails.ru',
    'https://back-corp.cocktails.ru',
    'https://ms-corp.cocktails.ru'
)

CORS_ALLOW_HEADERS = (
    'content-disposition',
    'accept-encoding',
    'content-type',
    'accept',
    'origin',
    'authorization',
    'Access-Control-Allow-Origin',
    'access-control-allow-origin',
    'X-CSRFToken',
)
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = True

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'django-db')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_BROKER_CONNECTION_RETRY = True
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

CELERY_BEAT_SCHEDULE = {
    'get_ozon_products': {
        'task': 'goods.get_ozon_products',
        'schedule': timedelta(hours=1)
    },
}

SWAGGER_SETTINGS = {
    'DEFAULT_AUTO_SCHEMA_CLASS': 'main_core.swagger.CompoundTagsSchema',
    'DEFAULT_MODEL_RENDERING': 'example',
    'DOC_EXPANSION': 'none',
    'TAGS_SORTER': 'alpha',
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'description': 'Value example: Token ******************',
            'in': 'header',
        }
    }
}

ENVIRONMENT = os.environ.get('ENVIRONMENT') or 'production'

S3_ACCESS_KEY = os.environ.get('S3_ACCESS_KEY')
S3_SECRET_KEY = os.environ.get('S3_SECRET_KEY')
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
S3_REGION = 'ru-central1'
S3_DUMPS_DIR_NAME = 'dumps'

AUTH_BY_USER_PERMISSION_CODE = 'auth_by_user'
AUTH_BY_USER_PERMISSION_NAME = 'Авторизация за пользователя'

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

FRONT_URL = os.environ.get('FRONT_URL')

PHONENUMBER_DEFAULT_REGION = 'RU'

TINKOFF_PAYMENT_URL = os.environ.get('TINKOFF_PAYMENT_URL')
TINKOFF_TERMINAL_ID = os.environ.get('TINKOFF_TERMINAL_ID')
TINKOFF_TERMINAL_PASSWORD = os.environ.get('TINKOFF_TERMINAL_PASSWORD')
TINKOFF_PAYMENT_TOKEN = os.environ.get('TINKOFF_PAYMENT_TOKEN')
TINKOFF_DEFAULT_SHOP_ID = os.environ.get('TINKOFF_DEFAULT_SHOP_ID')
TINKOFF_DEFAULT_EMAIL = os.environ.get('TINKOFF_DEFAULT_EMAIL')

OZON_BASE_URL = os.environ.get('OZON_BASE_URL')
OZON_CLIENT_ID = os.environ.get('OZON_CLIENT_ID')
OZON_API_KEY = os.environ.get('OZON_API_KEY')

AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
AWS_BUCKET_NAME = os.environ.get('AWS_BUCKET_NAME')


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
        },
    },
}

if not DEBUG:
    sentry_sdk.init(
        dsn=os.environ.get('SENTRY_URL'),
        integrations=[DjangoIntegration(), CeleryIntegration()],
        traces_sample_rate=1.0,
        send_default_pii=True,
        environment=ENVIRONMENT,
    )

