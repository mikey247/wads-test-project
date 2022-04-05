"""
Django local.py PRODUCTION MODE Settings Example Template

Copy this to local.py and edit setting as required.
DO NOT COMMIT THE local.py FILE TO THE REPOSITORY

See: https://docs.djangoproject.com/en/2.2/ref/settings/
See: https://docs.wagtail.io/en/v2.7/getting_started/integrating_into_django.html#settings
"""

import ldap
import logging

from django_auth_ldap.config import LDAPSearch
from django.core.exceptions import ImproperlyConfigured

from sitecore.auth import GroupMembershipDNGroupType

logger = logging.getLogger('django_auth_ldap')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

# wads-wagtail Optional Features
# ------------------------------------------------------------------------
ENABLE_LDAP = True # True|False
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
# See: https://docs.djangoproject.com/en/2.2/topics/security/#ssl-https
# SECURE_HSTS_SECONDS
# - 3600 = 1 hour
# - 31536000 = 1 year

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
        'BACKEND': 'wagtail.contrib.postgres_search.backend',
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

# Authentication Backend(s)
# ------------------------------------------------------------------------
# Add LDAP Authentication and custom settings
# Remove/comment "ModelBackend" if no default username/password access is required
# See: https://docs.djangoproject.com/en/2.2/ref/settings/#databases

AUTHENTICATION_BACKENDS = (
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
)

AUTH_LDAP_GLOBAL_OPTIONS = {
    ldap.OPT_X_TLS_REQUIRE_CERT: False,
    ldap.OPT_REFERRALS: False,
}

AUTH_LDAP_SERVER_URI = 'ldaps://ldap.manchester.ac.uk'
AUTH_LDAP_BIND_DN = ''
AUTH_LDAP_BIND_PASSWORD = ''
AUTH_LDAP_ALWAYS_UPDATE_USER = True
AUTH_LDAP_FIND_GROUP_PERMS = True
AUTH_LDAP_GROUP_TYPE = GroupMembershipDNGroupType()

# Specific queries for user and group search

AUTH_LDAP_USER_SEARCH = LDAPSearch('<insert LDAP user search query>', ldap.SCOPE_SUBTREE, "(uid=%(user)s)")
AUTH_LDAP_GROUP_SEARCH = LDAPSearch('<insert LDAP group search query>', ldap.SCOPE_SUBTREE, "(uid=%(user)s)")

# (examples for UoM)
# AUTH_LDAP_USER_SEARCH = LDAPSearch('ou=mc,ou=admin,ou=uman,o=ac,c=uk', ldap.SCOPE_SUBTREE, "(uid=%(user)s)")
# AUTH_LDAP_GROUP_SEARCH = LDAPSearch('ou=mc,ou=admin,ou=uman,o=ac,c=uk', ldap.SCOPE_SUBTREE, "(uid=%(user)s)")

# Specify minimum group requirement to allow user authentication = MUST BE MEMBER OF THIS GROUP

AUTH_LDAP_REQUIRE_GROUP = '<insert required LDAP group for user authentication>'

# (examples for UoM)
# AUTH_LDAP_REQUIRE_GROUP = 'cn=admin-mc-ResearchIT-all,ou=mc,ou=admin,ou=uman,o=ac,c=uk'

# Map LDAP attribute fields to user model fields

AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail",
}

# Assign status flags based on group membership

AUTH_LDAP_USER_FLAGS_BY_GROUP = {
    "is_staff": '<insert LDAP group DN required for access>',
    "is_superuser": '<insert LDAP group DN required for superuser access>',
}

# (examples for UoM)
# AUTH_LDAP_USER_FLAGS_BY_GROUP = {
#     "is_staff": 'cn=admin-mc-ResearchIT-all,ou=mc,ou=admin,ou=uman,o=ac,c=uk',
#     "is_superuser": 'cn=admin-mc-ResearchIT-webadmin,ou=mc,ou=admin,ou=uman,o=ac,c=uk',
# }

# LDAP to Django Group Mapping - additional settings (not supported directly by django_auth_ldap)

# Assign to Django group (dict key) if user has LDAP groupMembership to any group in the value list

XAUTH_LDAP_GROUPS_FROM_MEMBERSHIP = {
    '<insert name of Django/Wagtail Group>': [
        '<insert LDAP group DN>',
        '<insert LDAP group DN>',
    ],
}

# (example for UoM)
# XAUTH_LDAP_GROUPS_FROM_MEMBERSHIP = {
#     'Moderators': [
#         'cn=admin-mc-ResearchIT-webadmin,ou=mc,ou=admin,ou=uman,o=ac,c=uk',
#     ],
# }

# Assign to Django group (dict key) if user DOES NOT HAVE LDAP groupMembership to any group in the value list

XAUTH_LDAP_GROUPS_FROM_NON_MEMBERSHIP = {
    '<insert name of Django/Wagtail Group>': [
        '<insert LDAP group DN>',
        '<insert LDAP group DN>',
    ]
}

# XAUTH_LDAP_GROUPS_FROM_NON_MEMBERSHIP = {
#     'Editors': [
#         'cn=admin-mc-ResearchIT-webadmin,ou=mc,ou=admin,ou=uman,o=ac,c=uk',
#     ]
# }

# For LDAP we do not allow users to reset their passwords (nor can we change them)
# Also disables password fields in "new user" forms (if enabled)

#WAGTAIL_PASSWORD_MANAGEMENT_ENABLED = False
#WAGTAIL_PASSWORD_RESET_ENABLED = False
#WAGTAILUSERS_PASSWORD_ENABLED = False

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
