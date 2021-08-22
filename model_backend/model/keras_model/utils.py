import datetime as dt

import pandas as pd
from model_backend.model.keras_model.constants import MARKET_CLOSING_TIME

DATE_FORMAT = '%Y-%m-%d'


def get_date_from_string(date: str) -> dt.date:
    try:
        return dt.datetime.strptime(date, DATE_FORMAT).date()
    except ValueError:
        raise InvalidDateError(date)


def get_df_first_and_last_date(df: pd.DataFrame):
    return(df.index[0].date(), df.index[-1].date())


def get_prediction_date(df: pd.DataFrame, seq_len: int, date: str = None):
    if date is None:
        pred_date = dt.datetime.now().date()
        # timezone = pytz.timezone("Asia/Kolkata")
    else:
        pred_date = get_date_from_string(date)

    df_first_date, df_last_date = get_df_first_and_last_date(df)
    check_if_pred_date_correct(pred_date, df_first_date, df_last_date, seq_len)
    return pred_date


def check_if_pred_date_correct(pred_date: dt.date, df_first_date: dt.date, df_last_date: dt.date,  seq_len: int):
    """
    If df_last_date is Fri and date is Sat or Sun then the actual pred_date is of next Mon

    If df_last_date >= date - dt.timedelta(days=1) then we surely have the data for that pred_date
    """

    # If pred_date is Sat or Sun -> error
    if pred_date.weekday() == 5 or pred_date.weekday() == 6:
        raise InvalidPredictionDateError(pred_date, df_last_date, seq_len)

    if df_first_date + dt.timedelta(days=seq_len) > pred_date:
        raise InvalidPredictionDateError(pred_date, df_first_date, seq_len, lower=True)

    # If df_last_date is Fri and pred_date is greater and not next Mon then raise error
    if df_last_date < pred_date and df_last_date.weekday() == 4:
        if pred_date != df_last_date + dt.timedelta(days=3):
            raise InvalidPredictionDateError(pred_date, df_last_date, seq_len)

    # pred_date can't be 1 day more than df_last date
    elif df_last_date + dt.timedelta(days=1) < pred_date:
        raise InvalidPredictionDateError(pred_date, df_last_date, seq_len)

    # can only pred for tomorrow if current time is greater than MARKET_CLOSING_TIME (cuz we get correct value of CLOSE_PRICE after MARKET_CLOSING_TIME)
    elif df_last_date + dt.timedelta(days=1) == pred_date and dt.datetime.now().time() < MARKET_CLOSING_TIME:
        raise InvalidPredictionDateError(pred_date, df_last_date, seq_len)


class InvalidPredictionDateError(Exception):
    def __init__(self, pred_date: dt.date, df_date: dt.date, seq_len: int, lower: bool = False) -> None:
        if lower:
            msg = f"We have data till {df_date} and model needs sequences of length {seq_len} to predict. So model can predict only for dates starting from {df_date + dt.timedelta(days=seq_len)}. But you called model's predict function with this prediction date: {pred_date}"
        else:
            msg = f"We have data till {df_date}, so model can predict only till {df_date + dt.timedelta(days=1)}. But you called model's predict function with this prediction date: {pred_date}"
        super().__init__(msg)


class InvalidDateError(Exception):
    def __init__(self, date: dt.date) -> None:
        msg = f"{date} is not in correct format. Please give date in {DATE_FORMAT} format."
        super().__init__(msg)
