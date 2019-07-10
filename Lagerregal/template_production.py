import ldap
from django_auth_ldap.config import LDAPSearch
from django_auth_ldap.config import NestedActiveDirectoryGroupType

from .base_settings import *

DEBUG = False
PRODUCTION = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.,
    }
}

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT =  ''

# Make this unique, and don't share it with anybody.
SECRET_KEY = None

# example configuration; for use cases, search for LABEL_TEMPLATES in views
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

# A list of strings representing the host/domain names that this Django site can serve. This is a security measure to prevent
# HTTP Host header attacks, which are possible even under many seemingly-safe web server configurations.
# Values in this list can be fully qualified names (e.g. 'www.example.com'), in which case they will be matched against
# the request’s Host header exactly (case-insensitive, not including port). A value beginning with a period can be used as a
# subdomain wildcard: '.example.com' will match example.com, www.example.com, and any other subdomain of example.com.
# A value of '*' will match anything; in this case you are responsible to provide your
# own validation of the Host header (perhaps in a middleware; if so this middleware must be listed first in MIDDLEWARE).
ALLOWED_HOSTS = ""

# A list of all the people who get code error notifications. When DEBUG=False and AdminEmailHandler is configured in LOGGING (done by default),
# Django emails these people the details of exceptions raised in the request/response cycle.
ADMINS = []

# A list in the same format as ADMINS that specifies who should get broken link notifications when BrokenLinkEmailsMiddleware is enabled.
MANAGERS = []


# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = '/opt/Lagerregal/staticserve/'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_FILE_PATH = '/opt/lagerregal/mails'
EMAIL_HOST = 'localhost'
SERVER_EMAIL = ""
DEFAULT_FROM_EMAIL = ""

INTERNAL_IPS = ""
SEARCHSTRIP = {
    "text": "BILD"
}
STORAGE_ROOM = ""

USE_LDAP = True

ldap.set_option(ldap.OPT_REFERRALS, 0)

AUTHENTICATION_BACKENDS += 'django_auth_ldap.backend.LDAPBackend',
AUTH_LDAP_SERVER_URI = ""
AUTH_LDAP_BIND_DN = ""
AUTH_LDAP_BIND_PASSWORD = ""
AUTH_LDAP_USER_SEARCH = ""
AUTH_LDAP_GROUP_SEARCH = ""

LDAP_USER_SEARCH = []

AUTH_LDAP_GROUP_TYPE = NestedActiveDirectoryGroupType()
AUTH_LDAP_MIRROR_GROUPS = True

AUTH_LDAP_ATTR_NOSYNC = ["distinguishedName"]
AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail",
    "expiration_date": "accountExpires"  # FIXME
    }

AUTH_LDAP_USER_FLAGS_BY_GROUP = {}

AUTH_LDAP_DEPARTMENT_FIELD = "distinguishedName"
AUTH_LDAP_DEPARTMENT_REGEX = "OU=([^,]*?),DC"

USE_PUPPET = True

PUPPETDB_SETTINGS = {
        'host'       : 'lip-puppet.mpib-berlin.mpg.de',
        'port'       : 8081,
        'cacert'     : '/var/lib/puppet/ssl/certs/ca.pem',
        'cert'       : '/var/lib/puppet/ssl/certs/lagerregal.mpib-berlin.mpg.de.pem',
        'key'        : '/var/lib/puppet/ssl/private_keys/lagerregal.mpib-berlin.mpg.de.pem',
        'req'        : '/pdb/query/v4/facts?',
        'query_fact' : 'lagerregal_id',
        'software_fact' : 'software',
    }


# sample logger
# import logging, logging.handlers
# logger = logging.getLogger('django_auth_ldap')
# logger.addHandler(logging.StreamHandler())
# logger.setLevel(logging.DEBUG)
