from apscheduler.schedulers.background import BackgroundScheduler

from api.lstm_registry import lstm_registry
from api.models import Ticker


# If get_raw_df takes more time to complete than the interval of this func then - Execution of job "fetch_new_raw_data (trigger: interval[0:00:05], next run at: 2021-08-22 12:57:04 IST)" skipped: maximum number of running instances reached (1)
def fetch_new_raw_data():
    symbols = Ticker.objects.values_list('symbol', flat=True)
    for symbol in symbols:
        lstm_registry.get_service_by_symbol(symbol).preprocessed_data.data_processor.raw_data_source.get_raw_df()


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_new_raw_data, 'interval', minutes=1)
    scheduler.start()
    fetch_new_raw_data()
