from django.apps import AppConfig


class SitecoreConfig(AppConfig):
    name = 'sitecore'

    def ready(self):
        import sitecore.signals
