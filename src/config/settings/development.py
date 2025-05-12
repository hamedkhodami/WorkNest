from .base import BASE_DIR
import os
#----------------------------------------------------------------


#--DATABASES-----------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
#----------------------------------------------------------------