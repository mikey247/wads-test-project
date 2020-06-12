from django.apps import AppConfig


class LdapsignalConfig(AppConfig):
    name = 'ldapsignal'

    def ready(self):
        import ldapsignal.signals
