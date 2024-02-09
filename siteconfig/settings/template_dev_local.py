"""
Django local.py DEV MODE Settings Example Template
Copy this to local.py and edit setting as required.
DO NOT COMMIT THE local.py FILE TO THE REPOSITORY

Main documentation for Django and Wagtail versions:

- Django:  https://docs.djangoproject.com/en/3.2/ref/settings/
- Wagtail: https://docs.wagtail.org/en/stable/releases/2.15.html
"""

# wads-wagtail Optional Features
# ------------------------------------------------------------------------

ENABLE_LDAP = False # True|False
ENABLE_DEBUG_TOOLBAR = False # True|False

# Wagtail Site Settings
# ------------------------------------------------------------------------
# https://docs.wagtail.org/en/stable/reference/settings.html#settings
# ------------------------------------------------------------------------
# Base URL to use when referring to full URLs within the Wagtail admin
# backend - e.g. in notification emails.
# Don't include '/admin' or a trailing slash

WAGTAIL_SITE_NAME = '<INSERT WAGTAIL_SITE_NAME_HERE>'
WAGTAILADMIN_BASE_URL = '<INSERT BASE_URL HERE>' # usually localhost for dev

# Security
# ------------------------------------------------------------------------
# https://docs.djangoproject.com/en/3.2/topics/security/
# ------------------------------------------------------------------------
# Secret key is always required

SECRET_KEY = '<INSERT KEY_HERE>'

# Database
# ------------------------------------------------------------------------
# https://docs.djangoproject.com/en/3.2/ref/databases/
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
# https://docs.wagtail.org/en/stable/topics/search/backends.html
# 
# If using postgresql (now default db) use its search features
# 
# As of Wagtail 2.15 there is a new database search backend
# https://docs.wagtail.org/en/stable/releases/2.15.html

WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail.search.backends.database',
        'INDEX': '<INSERT SITE SPECIFIC INDEX NAME HERE>',
    },
}

# REST Framework
# ------------------------------------------------------------------------
# See: https://www.django-rest-framework.org/
#
# For permissions, isAdminUser only works with users added on the command
# line with ./manage.py createsuperuser
# OR with users given is_staff = True in LDAP group configurations
#
# Use isAuthenticated when requiring admin users added via Wagtail Admin

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

LOGGING = { "version": 1, "disable_existing_loggers": False, "formatters": {"rich": {"datefmt": "[%X]"}}, "handlers": { "console": { "class": "rich.logging.RichHandler", "formatter": "rich", "level": "DEBUG", "rich_tracebacks": True, } }, "loggers": { "django": {"handlers": ["console"]} }, }

WAGTAILIMAGES_EXTENSIONS = ["gif", "jpg", "jpeg", "png", "webp", "svg"]