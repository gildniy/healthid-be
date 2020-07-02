from django.apps import AppConfig


class ProductsConfig(AppConfig):
    name = 'healthid.apps.products'

    def ready(self):
        from . import signals  # noqa F401
        from healthid.jobs import main_job # noqa F401
