"""
Django settings for siteroot project.

Generated by 'django-admin startproject' using Django 2.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/


# Application definition

INSTALLED_APPS = [
    'sitecore',
    'siteuser',
    'home',
    'article',
    'event',
    'wagtailstreamforms',
    
    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail',

    'wagtail.contrib.modeladmin',
    'wagtail.contrib.settings',
    'wagtail.contrib.table_block',
    'wagtail.contrib.routable_page',
    'wagtail.contrib.styleguide',
    'wagtail.api.v2',

    'captcha',
    'crispy_forms',
    'wagtailautocomplete',
    'wagtailmenus',
    'wagtailcaptcha',
    'modelcluster',
    'taggit',
    'rest_framework',
    'shortcodes',
    'sekizai',
    'wagtailmedia',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'django_extensions',
    'django_select2',
    'django_social_share',
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',

    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
]

ROOT_URLCONF = 'siteconfig.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'wagtail.contrib.settings.context_processors.settings',
                'wagtailmenus.context_processors.wagtailmenus',
                'sekizai.context_processors.sekizai'
            ],
        },
    },
]

WSGI_APPLICATION = 'siteconfig.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = False

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

STATICFILES_DIRS = [
    os.path.join(PROJECT_DIR, 'static'),
]

# ManifestStaticFilesStorage is recommended in production, to prevent outdated
# Javascript / CSS assets being served from cache (e.g. after a Wagtail upgrade).
# See https://docs.djangoproject.com/en/2.2/ref/contrib/staticfiles/#manifeststaticfilesstorage
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# LML: Including this breaks ./manage.py collectstatic as the static files are found 'here' and via siteconfig as an INSTALLED_APPS leading to duplicates
# LML: Option is use separate app for project level templates, tags, static or leave like this.
# STATICFILES_DIRS = [
#     os.path.join(PROJECT_DIR, 'static'),
# ]

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

WAGTAIL_FRONTEND_LOGIN_TEMPLATE = 'sitecore/registration/login.html'
WAGTAIL_FRONTEND_LOGIN_URL = '/login/'

PASSWORD_REQUIRED_TEMPLATE = 'sitecore/registration/password_required.html'

AUTH_USER_MODEL = 'siteuser.User'
WAGTAIL_USER_EDIT_FORM = 'siteuser.forms.CustomUserEditForm'
WAGTAIL_USER_CREATION_FORM = 'siteuser.forms.CustomUserCreationForm'

WAGTAILIMAGES_IMAGE_MODEL = 'sitecore.SiteImage'
WAGTAIL_USER_CUSTOM_FIELDS = ['bio', 'team', 'job_title', 'country', 'twitter', 'receive_submission_notify_email']

LOGIN_REDIRECT_URL = '/'

CRISPY_ALLOWED_TEMPLATE_PACKS = "crispy_forms/bootstrap5"
CRISPY_TEMPLATE_PACK = "crispy_forms/bootstrap5"

# WAGTAILSTREAMFORMS_ADVANCED_SETTINGS_MODEL = 'sitecore.AdvancedFormSetting'
# WAGTAILSTREAMFORMS_ENABLE_BUILTIN_HOOKS=False

WAGTAILMEDIA_MEDIA_MODEL = 'sitecore.SiteMedia'
