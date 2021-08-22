# can't import any model (or a module that imports a model) here at module level, only inside ready(). Read -
# (https://docs.djangoproject.com/en/3.2/ref/applications/#how-applications-are-loaded   and
# https://docs.djangoproject.com/en/3.2/ref/applications/#django.apps.AppConfig.ready)

from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        from api.lstm_registry import lstm_registry
        from api.models import Ticker

        symbols = Ticker.objects.values_list('symbol', flat=True)
        for symbol in symbols:
            lstm_registry.register(symbol)

        # Two schedulers are set up when using py manage.py runserver - one by main process and one by reloader
        import api.scheduler as scheduler
        scheduler.start()
