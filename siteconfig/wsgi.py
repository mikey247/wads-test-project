"""
WSGI config for siteroot project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

from __future__ import absolute_import, unicode_literals

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "siteconfig.settings.dev")
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "siteconfig.settings.production")

application = get_wsgi_application()
