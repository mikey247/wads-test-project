"""
Django settings for ldaptest project.

Generated by 'django-admin startproject' using Django 3.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import ldap
import logging

from django_auth_ldap.config import LDAPSearch, LDAPGroupQuery, PosixGroupType, GroupOfNamesType, MemberDNGroupType, ActiveDirectoryGroupType

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {"dhango_auth_ldap": {"level": "DEBUG", "handlers": ["console"]}},
}

logger = logging.getLogger('django_auth_ldap')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ''

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'hammerlock.itservices.manchester.ac.uk',
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "django_auth_ldap.backend.LDAPBackend",
]

# Django Auth LDAP
# With custom group settings

# Custom XAUTH settings to specify what groupMembership entries should be set per authenticated user

XAUTH_LDAP_REQUIRE_IS_STAFF_GROUP = 'cn=admin-mc-ResearchIT-all,ou=mc,ou=admin,ou=uman,o=ac,c=uk'
XAUTH_LDAP_REQUIRE_IS_SUPERUSER_GROUP = 'cn=admin-mc-ResearchIT-all,ou=mc,ou=admin,ou=uman,o=ac,c=uk'

# Standard AUTH_LDAP settings for django_auth_ldap to integrate with UoM LDAP Active Directory

AUTH_LDAP_GLOBAL_OPTIONS = {
    ldap.OPT_X_TLS_REQUIRE_CERT: False,
    ldap.OPT_REFERRALS: False,
}

AUTH_LDAP_SERVER_URI = "ldaps://ldap.manchester.ac.uk"
AUTH_LDAP_BIND_DN = ""
AUTH_LDAP_BIND_PASSWORD = ""
AUTH_LDAP_ALWAYS_UPDATE_USER = True

AUTH_LDAP_USER_SEARCH = LDAPSearch (
    "ou=mc,ou=admin,ou=uman,o=ac,c=uk",
    ldap.SCOPE_SUBTREE,
    "(uid=%(user)s)"
)

AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail",
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

