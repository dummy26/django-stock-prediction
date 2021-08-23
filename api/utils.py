import datetime as dt

from model_backend.data.constants import NAME_OF_COMP_COLUMN, SYMBOL_COLUMN
from model_backend.data.utils import get_all_nse_company_names_and_ticker
from model_backend.model.keras_model.utils import DATE_FORMAT

from api.models import Model, Ticker


def get_ticker_from_symbol(symbol):
    ticker = Ticker.objects.filter(symbol__iexact=symbol.lower()).first()
    return ticker


def get_todays_date_as_str():
    return dt.datetime.now().date().strftime(DATE_FORMAT)


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
