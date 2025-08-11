from .base import BASE_DIR, DEFAULT_JWT_CONFIG
from datetime import timedelta
import os
# ----------------------------------------------------------------


# --DATABASES-----------------------------------------------------
DATABASES = {
    "default": {
        'ENGINE': 'django.db.backends.postgresql',
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
    }
}
# ----------------------------------------------------------------


# ---JWT---------------------------------------------------------
SIMPLE_JWT = {
    **DEFAULT_JWT_CONFIG,
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}
# ----------------------------------------------------------------
