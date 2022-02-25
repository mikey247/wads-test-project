"""
Django local.py DEV MODE Settings Example Template
Copy this to local.py and edit setting as required.
DO NOT COMMIT THE local.py FILE TO THE REPOSITORY
See https://docs.djangoproject.com/en/2.2/ref/settings/
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

WAGTAIL_SITE_NAME = '<INSERT WAGTAIL_SITE_NAME_HERE>'
BASE_URL = '<INSERT BASE_URL HERE>' # usually localhost for dev

# Security
# ------------------------------------------------------------------------

SECRET_KEY = '<INSERT KEY_HERE>'

# Database
# ------------------------------------------------------------------------
# Use Postgresql by default rather than sqlite3

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '<INSERT DATABASE NAME HERE>',
        'USER': '<INSERT USER NAME HERE>',
        'PASSWORD': '<INSERT PASSWORD NAME HERE>',
        'HOST': 'localhost',
        'PORT': '',
    }
}

# Hosts
# ------------------------------------------------------------------------
# Hosts/domain names that are valid for this site
# REQUIRED if DEBUG is False
# WSL2: if not serving on localhost:8000 add IP from running `ifconfig`

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
]

INTERNAL_IPS = [
    '127.0.0.1',
]

# Language
# ------------------------------------------------------------------------

LANGUAGE_CODE = 'en-gb'

# Search Backends
# ------------------------------------------------------------------------
# See: https://docs.wagtail.io/en/v2.7/topics/search/backends.html#backends
# If using postgresql (now default db) use its search features

WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail.contrib.postgres_search.backend',
        'INDEX': '<INSERT SITE SPECIFIC INDEX NAME HERE>',
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
