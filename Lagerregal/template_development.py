from .base_settings import *

DEBUG = True
PRODUCTION = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'database.db',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = '{0}/media'.format(os.getcwd())

# Make this unique, and don't share it with anybody.
SECRET_KEY = "CHANGE ME IN PRODUCTION AND DON'T COMMIT ME!"

ALLOWED_HOSTS = ['*']

#example configuration; for use cases, search for LABEL_TEMPLATES in views
LABEL_TEMPLATES = {
    "DEPARTMENT": {
        "device": (
            #"/opt/Lagerregal/staticserve/labels/device.label",
            "labels/device.label",
            ["name", "inventorynumber", "serialnumber", "id"]),
        "room": (
            #"/opt/Lagerregal/staticserve/labels/room.label",
            "labels/room.label",
            ["name", "building", "id"]),
    }
}

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
# MEDIA_ROOT =  '{0}/media'.format(os.getcwd())

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

INTERNAL_IPS = [
    "127.0.0.1",
]

# comment out next line to send emails to the console
#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
