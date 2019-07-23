# Django settings for Lagerregal project.
import os

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Berlin'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    '{0}/static'.format(os.getcwd()),
)

LOCALE_PATHS = (
    '{0}/locale'.format(os.getcwd()),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
    'npm.finders.NpmFinder',
)

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'reversion.middleware.RevisionMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'users.middleware.TimezoneMiddleware',
    'users.middleware.LanguageMiddleware',
)

ROOT_URLCONF = 'Lagerregal.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'Lagerregal.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            '{0}/templates'.format(os.getcwd()),
        ],
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'devices.context_processors.get_settings'
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
        },
    },
]

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    'main',
    'devices',
    'network',
    'devicetypes',
    'devicegroups',
    'devicetags',
    'locations',
    'users',
    'api',
    'mail',
    'history',
    'reversion',
    'rest_framework',
    'debug_toolbar',
    'oauth2_provider',
    'django_select2',
)

LANGUAGES = (
    ('de', 'German'),
    ('en', 'English'),
)

AUTH_USER_MODEL = 'users.Lageruser'

SITE_NAME = "Lagerregal"

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
        'rest_framework.authentication.SessionAuthentication',
    )
}

AUTHENTICATION_BACKENDS = (
    # 'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
    'main.backends.LagerregalBackend',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# get more themes from https://bootswatch.com/ and download them to:
#   static/css/themes/<name>.min.css
THEMES = [
    'flatly',
    'darkly',
    'simplex',
    'superhero',
    'united',
]

NPM_ROOT_PATH = os.getcwd()

NPM_FILE_PATTERNS = {
    'bootstrap': [
        'dist/js/bootstrap.min.js',
    ],
    'bootswatch': ['dist/{}/bootstrap.min.css'.format(t) for t in THEMES],
    'font-awesome': [
        'css/font-awesome.min.css',
        'fonts/*',
    ],
    'jquery': ['dist/jquery.min.js'],
    'jquery-ui-dist': [
        'jquery-ui.min.js',
        'jquery-ui.min.css',
        'images/*.png',
    ],
    'datatables.net': [
        'js/jquery.dataTables.min.js',
    ],
    'datatables.net-bs4': [
        'css/dataTables.bootstrap4.min.css',
        'js/dataTables.bootstrap4.min.js',
    ],
    'mustache': ['mustache.min.js'],
    'noty': [
        'js/noty/jquery.noty.js',
        'js/noty/layouts/*.js',
        'js/noty/themes/*.js',
    ],
    'popper.js': [
        'dist/umd/popper.min.js',
    ],
    'select2': [
        'dist/js/select2.min.js',
        'dist/css/select2.min.css',
    ],
    'timeago': [
        'jquery.timeago.js',
        'locales/jquery.timeago.de.js',
    ],
}

PUBLIC_DEVICES_FILTER = {"tags__id__in": ["3", "17"]}

FAVICON_PATH = STATIC_URL + 'images/favicon.ico'

SELECT2_JS = ''
SELECT2_CSS = ''

TEST_RUNNER = 'Lagerregal.utils.DetectableTestRunner'
TEST_MODE = False
PRODUCTION = False
