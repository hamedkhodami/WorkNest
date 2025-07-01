from pathlib import Path
import os
from dotenv import load_dotenv
from django.utils.translation import gettext_lazy as _
from datetime import timedelta
# -----------------------------------------------------------------


# ---BASE_DIR------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent
# -----------------------------------------------------------------


# ---ENV-----------------------------------------------------------
load_dotenv(dotenv_path=BASE_DIR / '.env')
# -----------------------------------------------------------------


# ---SECURITY------------------------------------------------------
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = bool(int(os.getenv('DEBUG', 1)))
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')
# -----------------------------------------------------------------


# ---CSRF---------------------------------------------------------
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED', 'http://127.0.0.1',).split(',')
# ----------------------------------------------------------------


# ---Application definition---------------------------------------
INSTALLED_APPS = [
    'channels',
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # third party app
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'drf_yasg',
    'phonenumber_field',
    'rosetta',

    # apps
    'apps.core.apps.CoreConfig',
    'apps.account.apps.AccountConfig',
    'apps.team.apps.TeamConfig',
    'apps.board.apps.BoardConfig',
    'apps.task.apps.TaskConfig',
    'apps.notification.apps.NotificationConfig',
    'apps.logbook.apps.LogbookConfig',
    'apps.chat.apps.ChatConfig',
    'apps.public.apps.PublicConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },

    },
]
# ----------------------------------------------------------------


# ---WSGI---------------------------------------------------------
ASGI_APPLICATION = 'config.asgi.application'
# ----------------------------------------------------------------


# ---Password validation------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
# ----------------------------------------------------------------


# ---Internationalization-----------------------------------------
LANGUAGES = [
    ('fa', _("Persian")),
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

LANGUAGE_CODE = 'fa'

TIME_ZONE = 'Asia/Tehran'

USE_I18N = True

USE_TZ = False
# ----------------------------------------------------------------


# ---Static files-------------------------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = os.getenv('STATIC_ROOT')

STATICFILES_DIRS = [
   os.getenv('STATICFILES_DIRS', BASE_DIR / 'static/assets/'),
]
# ----------------------------------------------------------------


# ---Media--------------------------------------------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / os.getenv('MEDIA_ROOT', 'static/media')
# ----------------------------------------------------------------


# ---Production whitenoise----------------------------------------
if int(os.getenv('ENABLE_WHITENOISE', default=0)):
    # Insert Whitenoise Middleware and set as StaticFileStorage
    MIDDLEWARE += [
        'whitenoise.middleware.WhiteNoiseMiddleware',
    ]
    STATICFILES_STORAGE = 'whitenoise.storage.StaticFilesStorage'
# ----------------------------------------------------------------


# ---Default primary key field type------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# ---------------------------------------------------------------


# ---Auth-------------------------------------------------------
PHONENUMBER_DEFAULT_REGION = "IR"

AUTH_USER_MODEL = 'account.User'

LOGIN_URL = '/u/login'

LOGIN_OTP_CONFIG = {
    'TIMEOUT': 180,  # by sec
    'CODE_LENGTH': 6,
    'STORE_BY': 'otp_auth_phonenumber_{}'  # redis key
}

USER_OTP_CONFIG = {
    'TIMEOUT': 180,  # by sec
    'CODE_LENGTH': 4,
    'STORE_BY': 'user_otp_auth_phonenumber_{}'  # redis key
}

RESET_PASSWORD_CONFIG = {
    'TIMEOUT': 180,  # by sec
    'CODE_LENGTH': 4,
    'STORE_BY': 'reset_password_phonenumber_{}'  # redis key
}

CONFIRM_PHONENUMBER_CONFIG = {
    'TIMEOUT': 180,  # by sec
    'CODE_LENGTH': 4,
    'STORE_BY': 'confirm_phonenumber_{}'  # redis key
}
# ---------------------------------------------------------------


# ---Redis-------------------------------------------------------
REDIS_CONFIG = {
    'DB': int(os.getenv('REDIS_DB', 0)),
    'HOST': os.getenv('REDIS_HOST', 'localhost'),
    'PORT': os.getenv('REDIS_PORT', '6379'),
    'CHANNEL_NAME': os.getenv('REDIS_CHANNEL_NAME', 'market_price')
}
# ---------------------------------------------------------------


# ---CELERY config------------------------------------------------
CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND= CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE= TIME_ZONE
CELERY_TASK_DEFAULT_QUEUE = 'default'
# ----------------------------------------------------------------


# ---CHANNEL_LAYERS-----------------------------------------------
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [(REDIS_CONFIG['HOST'], REDIS_CONFIG['PORT'])],
        },
    },
}
# ---------------------------------------------------------------


# ---API---------------------------------------------------------
API_VERSION = 'v1'
API_URL_LABEL = 'api'
# ---------------------------------------------------------------


# ---SWAGGER-----------------------------------------------------
SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Bearer": {"type": "JWT", "name": "authorization", "in": "header"},
    },
}
# ---------------------------------------------------------------


# ---REST_FRAMEWORK----------------------------------------------
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'apps.core.exceptions.custom_exception_handler',
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'apps.account.auth.authentication.BaseJWTAuthentication',
    ],
}
# ---------------------------------------------------------------


# ---JWT---------------------------------------------------------
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=40),  # TODO: must change in production(just use in development)
    "REFRESH_TOKEN_LIFETIME": timedelta(days=20),
    "AUTH_HEADER_TYPES": ("Bearer",),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True
}
# ---------------------------------------------------------------


# ---CACHES------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379",
    }
}
# ---------------------------------------------------------------


# --ROSETTA------------------------------------------------------
ROSETTA_ACCESS_CONTROL_FUNCTION = lambda u: u.is_staff
# ---------------------------------------------------------------


# ---Email-------------------------------------------------------
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND')
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS') == 'True'
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')
# ----------------------------------------------------------------


# ---SMS config---------------------------------------------------
SMS_CONFIG = {
    'API_KEY': os.getenv('SMS_CONFIG_API_KEY'),
    'ORIGINATOR': os.getenv('SMS_CONFIG_ORIGINATOR')
}
# ----------------------------------------------------------------


