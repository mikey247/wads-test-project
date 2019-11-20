"""
Django local.py PRODUCTION MODE Settings Example Template

Copy this to local.py and edit setting as required.
DO NOT COMMIT THE local.py FILE TO THE REPOSITORY

See: https://docs.djangoproject.com/en/2.2/ref/settings/
See: https://docs.wagtail.io/en/v2.7/getting_started/integrating_into_django.html#settings
"""

# Security
# ------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/2.2/topics/security/#ssl-https
# SECURE_HSTS_SECONDS
# - 3600 = 1 hour
# - 31536000 = 1 year

SECRET_KEY = '<INSERT KEY_HERE>'

# UNCOMMENT THESE WHEN SSL IS WORKING

# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SECURE_HSTS_SECONDS = 31536000

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

# Wagtail Settings
# ------------------------------------------------------------------------
# Base URL to use when referring to full URLs within the Wagtail admin
# backend - e.g. in notification emails.
# Don't include '/admin' or a trailing slash

WAGTAIL_SITE_NAME = "<INSERT SITE NAME HERE>"
BASE_URL = '<INSERT BASE URL HERE>'

# Caches
# ------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/2.2/ref/settings/#caches

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://localhost:6379',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
	    "SERIALIZER": "django_redis.serializers.json.JSONSerializer",
        },
        'KEY_PREFIX': '<INSERT CACHE PREFIX HERE>'
    },
}

# Search Backends
# ------------------------------------------------------------------------
# See: https://docs.wagtail.io/en/v2.7/topics/search/backends.html#backends

WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail.search.backends.<POSTGRES OR ELASTICSEARCHn>',
        'INDEX': 'wagtail',
    },
}

# REST Framework
# ------------------------------------------------------------------------
# See: https://www.django-rest-framework.org/

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAdminUser',
    ],
    'PAGE_SIZE': 10,
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
}

