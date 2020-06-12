"""
Django local.py PRODUCTION MODE Settings Example Template

Copy this to local.py and edit setting as required.
DO NOT COMMIT THE local.py FILE TO THE REPOSITORY

See: https://docs.djangoproject.com/en/2.2/ref/settings/
See: https://docs.wagtail.io/en/v2.7/getting_started/integrating_into_django.html#settings
"""

# LDAP IMPORTS

# import os
# import ldap
# import logging

# from django_auth_ldap.config import LDAPSearch, LDAPGroupQuery, PosixGroupType, GroupOfNamesType, MemberDNGroupType, ActiveDirectoryGroupType

# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "handlers": {"console": {"class": "logging.StreamHandler"}},
#     "loggers": {"dhango_auth_ldap": {"level": "DEBUG", "handlers": ["console"]}},
# }

# logger = logging.getLogger('django_auth_ldap')
# logger.addHandler(logging.StreamHandler())
# logger.setLevel(logging.DEBUG)


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

# LDAP VARIABLES AND FUNCTIONS
# COMMENTED OUT BY DEFAULT

# AUTHENTICATION_BACKENDS = [
#     "django.contrib.auth.backends.ModelBackend",
#     "django_auth_ldap.backend.LDAPBackend",
# ]

# # Django Auth LDAP
# # With custom group settings

# # Custom XAUTH settings to specify what groupMembership entries should be set per authenticated user

# XAUTH_LDAP_REQUIRE_IS_STAFF_GROUP = 'cn=admin-mc-ResearchIT-all,ou=mc,ou=admin,ou=uman,o=ac,c=uk'
# XAUTH_LDAP_REQUIRE_IS_SUPERUSER_GROUP = 'cn=admin-mc-ResearchIT-all,ou=mc,ou=admin,ou=uman,o=ac,c=uk'

# # Standard AUTH_LDAP settings for django_auth_ldap to integrate with UoM LDAP Active Directory

# AUTH_LDAP_GLOBAL_OPTIONS = {
#     ldap.OPT_X_TLS_REQUIRE_CERT: False,
#     ldap.OPT_REFERRALS: False,
# }

# AUTH_LDAP_SERVER_URI = "ldaps://ldap.manchester.ac.uk"
# AUTH_LDAP_BIND_DN = ""
# AUTH_LDAP_BIND_PASSWORD = ""
# AUTH_LDAP_ALWAYS_UPDATE_USER = True

# AUTH_LDAP_USER_SEARCH = LDAPSearch (
#     "ou=mc,ou=admin,ou=uman,o=ac,c=uk",
#     ldap.SCOPE_SUBTREE,
#     "(uid=%(user)s)"
# )

# AUTH_LDAP_USER_ATTR_MAP = {
#     "first_name": "givenName",
#     "last_name": "sn",
#     "email": "mail",
# }

# # Password validation
# # https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

# AUTH_PASSWORD_VALIDATORS = [
#     {
#         'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
#     },
# ]