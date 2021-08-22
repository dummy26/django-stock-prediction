import datetime as dt

from model_backend.model.keras_model.utils import DATE_FORMAT

from api.models import Ticker


def get_ticker_from_symbol(symbol):
    ticker = Ticker.objects.filter(symbol__iexact=symbol.lower()).first()
    return ticker


def get_todays_date_as_str():
    return dt.datetime.now().date().strftime(DATE_FORMAT)
