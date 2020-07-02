from django.apps import AppConfig


class OutletsConfig(AppConfig):

    name = 'healthid.apps.outlets'

    def ready(self):
        from . import signals  # noqa
