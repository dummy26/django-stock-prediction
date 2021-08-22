from apscheduler.schedulers.background import BackgroundScheduler
from model_backend.data.constants import NAME_OF_COMP_COLUMN, SYMBOL_COLUMN
from model_backend.data.utils import get_all_nse_company_names_and_ticker

from api.lstm_registry import lstm_registry
from api.models import Ticker


def populate_ticker_db():
    df = get_all_nse_company_names_and_ticker()
    # all_symbols = {symbol for symbol in df[SYMBOL_COLUMN]}
    # TODO get it from df
    all_symbols = ['RELIANCE', 'TCS']

    db_symbols = {ticker.symbol for ticker in Ticker.objects.all()}
    missing_symbols = all_symbols-db_symbols

    print(len(missing_symbols))

    new_tickers = []
    for missing_symbol in missing_symbols:
        company_name = df[df[SYMBOL_COLUMN] == missing_symbol][NAME_OF_COMP_COLUMN].item()
        new_tickers.append(Ticker(symbol=missing_symbol, company_name=company_name))

    Ticker.objects.bulk_create(new_tickers)


# If get_raw_df takes more time to complete than the interval of this func then - Execution of job "fetch_new_raw_data (trigger: interval[0:00:05], next run at: 2021-08-22 12:57:04 IST)" skipped: maximum number of running instances reached (1)
def fetch_new_raw_data():
    symbols = Ticker.objects.values_list('symbol', flat=True)
    for symbol in symbols:
        lstm_registry.get_service_by_symbol(symbol).preprocessed_data.data_processor.raw_data_source.get_raw_df()


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(populate_ticker_db, 'interval', days=1)
    scheduler.add_job(fetch_new_raw_data, 'interval', minutes=1)
    scheduler.start()
    fetch_new_raw_data()
