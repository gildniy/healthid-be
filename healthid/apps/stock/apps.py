from django.apps import AppConfig


class StockConfig(AppConfig):
    name = 'healthid.apps.stock'

    def ready(self):
        from healthid.jobs.main_job import alert_counting
        alert_counting()
