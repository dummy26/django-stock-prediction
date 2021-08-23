import datetime as dt
from functools import lru_cache

from model_backend.data.constants import NAME_OF_COMP_COLUMN, SYMBOL_COLUMN
from model_backend.data.utils import get_all_nse_company_names_and_ticker
from model_backend.model.keras_model.constants import MARKET_CLOSING_TIME
from model_backend.model.keras_model.utils import (DATE_FORMAT,
                                                   get_df_first_and_last_date)

from api.lstm_registry import lstm_registry
from api.models import Model, Ticker


def get_ticker_from_symbol(symbol):
    ticker = Ticker.objects.filter(symbol__iexact=symbol.lower()).first()
    return ticker


def populate_ticker_and_model_db():
    df = get_all_nse_company_names_and_ticker()
    all_symbols = {symbol for symbol in df[SYMBOL_COLUMN]}

    db_symbols = {ticker.symbol for ticker in Ticker.objects.all()}
    missing_symbols = all_symbols-db_symbols

    new_tickers = []
    new_models = []
    for symbol in missing_symbols:
        company_name = df[df[SYMBOL_COLUMN] == symbol][NAME_OF_COMP_COLUMN].item()
        ticker = Ticker(symbol=symbol, company_name=company_name)
        new_tickers.append(ticker)
        new_models.append(Model(ticker=ticker))

    Ticker.objects.bulk_create(new_tickers)
    Model.objects.bulk_create(new_models)


@lru_cache(maxsize=64)
def get_str_from_date(date: dt.date) -> str:
    return dt.datetime.strftime(date, DATE_FORMAT)


def get_latest_pred_date():
    ticker = Ticker.objects.all().first().symbol
    df = lstm_registry.get_service_by_symbol(ticker).preprocessed_data.data_processor.raw_data_source.get_raw_df()
    _, df_last_date = get_df_first_and_last_date(df)

    if dt.datetime.now().time() < MARKET_CLOSING_TIME:
        return get_str_from_date(df_last_date)

    if df_last_date.weekday() == 4:
        pred_date = df_last_date + dt.timedelta(days=3)
    else:
        pred_date = df_last_date + dt.timedelta(days=1)
    return get_str_from_date(pred_date)
