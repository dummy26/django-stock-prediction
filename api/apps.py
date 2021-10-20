# can't import any model (or a module that imports a model) here at module level, only inside ready(). Read -
# (https://docs.djangoproject.com/en/3.2/ref/applications/#how-applications-are-loaded   and
# https://docs.djangoproject.com/en/3.2/ref/applications/#django.apps.AppConfig.ready)

from django.apps import AppConfig
from django.db.utils import OperationalError


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        from api.lstm_registry import lstm_registry
        from api.models import Ticker
        from api.utils import populate_ticker_and_model_db

        try:
            populate_ticker_and_model_db()
        except OperationalError:
            pass

        symbols = Ticker.objects.values_list('symbol', flat=True)
        for symbol in symbols:
            lstm_registry.register(symbol)

        # Two schedulers are set up when using py manage.py runserver - one by main process and one by reloader
        import api.scheduler as scheduler
        scheduler.start()
