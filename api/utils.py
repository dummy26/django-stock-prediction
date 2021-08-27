import datetime as dt
import time
from functools import lru_cache

import numpy as np
from model_backend.data.constants import NAME_OF_COMP_COLUMN, SYMBOL_COLUMN
from model_backend.data.data_processor import ScalerNotFoundError
from model_backend.data.utils import get_all_nse_company_names_and_ticker
from model_backend.model.keras_model.constants import MARKET_CLOSING_TIME
from model_backend.model.keras_model.utils import (DATE_FORMAT,
                                                   InvalidPredictionDateError,
                                                   get_df_first_and_last_date)
from model_backend.model.model import ModelNotFoundError

from api.lstm_registry import lstm_registry
from api.models import Model, Prediction, Ticker


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


def get_pred_date_from_request(request):
    latest_prediction = request.GET.get('latest')
    if latest_prediction is not None and latest_prediction.lower() == 'true':
        return get_latest_pred_date()

    pred_date = request.GET.get('pred_date')
    return pred_date


def get_latest_pred_date():
    ticker = Ticker.objects.all().first().symbol
    df = lstm_registry.get_service_by_symbol(ticker).preprocessed_data.data_processor.raw_data_source.get_raw_df()
    _, df_last_date = get_df_first_and_last_date(df)

    today = dt.datetime.now()
    if df_last_date == today.date():
        if today.time() < MARKET_CLOSING_TIME:
            pred_date = df_last_date
        else:
            if df_last_date.weekday() == 4:
                pred_date = df_last_date + dt.timedelta(days=3)
            else:
                pred_date = df_last_date + dt.timedelta(days=1)

    elif df_last_date < today.date():
        if df_last_date.weekday() == 4:
            pred_date = df_last_date + dt.timedelta(days=3)
        else:
            pred_date = df_last_date + dt.timedelta(days=1)

    return get_str_from_date(pred_date)


def get_predictions_for_period(period, symbol, model):
    latest_pred_date = dt.datetime.strptime(get_latest_pred_date(), DATE_FORMAT)
    if latest_pred_date.weekday() == 1:
        pred_date = latest_pred_date - dt.timedelta(days=3)
    else:
        pred_date = latest_pred_date - dt.timedelta(days=1)

    start = time.monotonic()

    predictions = []
    raw_data_source = lstm_registry.get_service_by_symbol(symbol).preprocessed_data.data_processor.raw_data_source
    df = get_processed_df(raw_data_source)

    i = 0
    while i < period:
        try:
            actual = df.loc[pred_date] * 100
        except KeyError:
            pred_date -= dt.timedelta(days=1)
            continue

        prediction_obj = Prediction.objects.filter(model=model, pred_date=pred_date).first()
        if prediction_obj is None:
            try:
                y, actual_pred_date = model.predict(dt.datetime.strftime(pred_date, DATE_FORMAT))
                y = round(float(y), 2)
                prediction_obj = Prediction.objects.create(model=model, pred_date=actual_pred_date, prediction=y, actual=actual)

            # except (ModelNotFoundError, ScalerNotFoundError):
            #     return Response(f'Could not find model files.', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except InvalidPredictionDateError:
                pass

        if prediction_obj is not None:
            predictions.append(prediction_obj)
            pred_date -= dt.timedelta(days=1)
            i += 1

    predictions.sort(key=lambda prediction: prediction.pred_date)
    print('views predictions', time.monotonic() - start)
    return predictions


def get_processed_df(raw_data_source):
    df = raw_data_source.get_raw_df()
    df = df[raw_data_source.FEATURE_KEYS]
    df = df.astype(np.float64)
    df.dropna(inplace=True)
    df = df[df[raw_data_source.VOL_COLUMN] != 0]
    df = df[raw_data_source.CLOSE_COLUMN]

    df = df.pct_change()
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(inplace=True)
    return df
