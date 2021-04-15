# These settings are only used for the example docker container.

from Lagerregal.base_settings import *

DEBUG = True
PRODUCTION = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'example.db',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

MEDIA_ROOT = '{0}/media'.format(os.getcwd())

SECRET_KEY = "CHANGE ME IN PRODUCTION AND DON'T COMMIT ME!"

ALLOWED_HOSTS = ['*']
LABEL_TEMPLATES = {}

STATIC_ROOT = ''

INTERNAL_IPS = [
    "127.0.0.1",
]
