from django.apps import AppConfig


class OrdersConfig(AppConfig):
    name = 'healthid.apps.orders'

    def ready(self):
        from . import signals  # noqa
