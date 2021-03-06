from django.apps import AppConfig
from django.conf import settings

class SitecoreConfig(AppConfig):
    name = 'sitecore'

    def ready(self):
        if settings.ENABLE_LDAP:
            import sitecore.signals
