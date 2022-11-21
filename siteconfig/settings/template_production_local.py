"""
Django local.py PRODUCTION MODE Settings Example Template

Copy this to local.py and edit setting as required.
DO NOT COMMIT THE local.py FILE TO THE REPOSITORY

See: https://docs.djangoproject.com/en/2.2/ref/settings/
See: https://docs.wagtail.io/en/v2.7/getting_started/integrating_into_django.html#settings
"""
# wads-wagtail Optional Features
# ------------------------------------------------------------------------
ENABLE_LDAP = False # True|False
ENABLE_DEBUG_TOOLBAR = False # True|False

# Wagtail Site Settings
# ------------------------------------------------------------------------
# Base URL to use when referring to full URLs within the Wagtail admin
# backend - e.g. in notification emails.
# Don't include '/admin' or a trailing slash

WAGTAIL_SITE_NAME = "<INSERT SITE NAME HERE>"
BASE_URL = '<INSERT BASE URL HERE>'

# Security
# ------------------------------------------------------------------------

SECRET_KEY = '<INSERT KEY_HERE>'

# Database(s)
# ------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '<INSERT DATABASE NAME HERE>',
        'USER': '<INSERT DATABASE USER HERE>',
        'PASSWORD': '<INSERT DATABASE PASSWORD HERE>',
        'HOST': 'localhost',
        'PORT': '',
    }
}

# Hosts
# ------------------------------------------------------------------------
# Hosts/domain names that are valid for this site
#
# REQUIRED if DEBUG is False
# 
# See: https://docs.djangoproject.com/en/2.2/ref/settings/#allowed-hosts

ALLOWED_HOSTS = [
    '<INSERT FQDN HERE>',
    'localhost',
    '127.0.0.1',
]

INTERNAL_IPS = [
    '127.0.0.1',
]

# Language
# ------------------------------------------------------------------------

LANGUAGE_CODE = 'en-gb'

# Caches
# ------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/2.2/ref/settings/#caches

# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': 'redis://localhost:6379',
#         'OPTIONS': {
#             'CLIENT_CLASS': 'django_redis.client.DefaultClient',
# 	    "SERIALIZER": "django_redis.serializers.json.JSONSerializer",
#         },
#         'KEY_PREFIX': '<INSERT CACHE PREFIX HERE>'
#     },
# }

# Search Backends
# ------------------------------------------------------------------------
# See: https://docs.wagtail.io/en/v2.7/topics/search/backends.html#backends

WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail.search.backends.database',
        'INDEX': '<insert index name here>',
    },
}

# REST Framework
# ------------------------------------------------------------------------
# See: https://www.django-rest-framework.org/

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'PAGE_SIZE': 10,
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
}

DATE_FORMAT = 'dS F Y'
TIME_FORMAT = 'H:i:s'
DATETIME_FORMAT = 'dS F Y H:i:s'
SHORT_DATE_FORMAT = 'd/m/y'
SHORT_TIME_FORMAT = 'H:i'
SHORT_DATETIME_FORMAT = 'd/m/y H:i'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False

GOOGLE_RECAPTCHA_SECRET_KEY = '<INSERT RECAPTCHA SECRET KEY HERE>'
