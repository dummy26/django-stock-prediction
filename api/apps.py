from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        from api.lstm_registry import lstm_registry
        from api.models import Ticker

        # symbols = list(Ticker.objects.values_list('symbol', flat=True))
        symbols = ['RELIANCE', 'TCS']
        for symbol in symbols:
            lstm_registry.register(symbol)
