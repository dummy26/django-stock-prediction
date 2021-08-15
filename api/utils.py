import datetime as dt

from apscheduler.schedulers.background import BackgroundScheduler
from model_backend.data.constants import NAME_OF_COMP_COLUMN, SYMBOL_COLUMN
from model_backend.data.utils import get_all_nse_company_names_and_ticker
from model_backend.model.keras_model.utils import DATE_FORMAT

from .models import Ticker


def get_ticker_from_symbol(symbol):
    ticker = Ticker.objects.filter(symbol__iexact=symbol.lower()).first()
    return ticker


def get_todays_date_as_str():
    return dt.datetime.now().date().strftime(DATE_FORMAT)


def populate_ticker_db():
    df = get_all_nse_company_names_and_ticker()
    all_symbols = {symbol for symbol in df[SYMBOL_COLUMN]}

    db_symbols = {ticker.symbol for ticker in Ticker.objects.all()}
    missing_symbols = all_symbols-db_symbols

    print(len(missing_symbols))

    new_tickers = []
    for missing_symbol in missing_symbols:
        company_name = df[df[SYMBOL_COLUMN] == missing_symbol][NAME_OF_COMP_COLUMN].item()
        new_tickers.append(Ticker(symbol=missing_symbol, company_name=company_name))

    Ticker.objects.bulk_create(new_tickers)


scheduler = BackgroundScheduler()

scheduler.add_job(populate_ticker_db, 'interval', days=1)
scheduler.start()
