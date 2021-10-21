import concurrent.futures

from apscheduler.schedulers.background import BackgroundScheduler

from api.lstm_registry import lstm_registry
from api.models import MAX_NUM_OF_PREDICTIONS, Prediction, Ticker


# If get_raw_df takes more time to complete than the interval of this func then - Execution of job "fetch_new_raw_data (trigger: interval[0:00:05], next run at: 2021-08-22 12:57:04 IST)" skipped: maximum number of running instances reached (1)
def fetch_new_raw_data():
    symbols = Ticker.objects.values_list('symbol', flat=True)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(fetch_new_raw_data_from_symbol, symbols)


def fetch_new_raw_data_from_symbol(symbol):
    lstm_registry.get_service_by_symbol(symbol).preprocessed_data.data_processor.raw_data_source.get_raw_df()


def delete_prediction_objects():
    predictions = Prediction.objects.all().order_by('pred_date')

    # using count() is faster than len() -> https://docs.djangoproject.com/en/3.2/ref/models/querysets/#django.db.models.query.QuerySet.count
    total_predictions = predictions.count()

    # It's not possible to call delete() on a sliced queryset -> https://docs.djangoproject.com/en/3.2/ref/models/querysets/#delete
    if total_predictions > MAX_NUM_OF_PREDICTIONS:
        to_be_deleted = predictions[:total_predictions-MAX_NUM_OF_PREDICTIONS].values_list('pk', flat=True)
        Prediction.objects.filter(id__in=to_be_deleted).delete()


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_new_raw_data, 'interval', minutes=1)
    scheduler.add_job(delete_prediction_objects, 'interval', days=1)
    scheduler.start()
