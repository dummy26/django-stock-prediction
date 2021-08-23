import datetime as dt
from abc import ABC, abstractmethod
from functools import lru_cache

import pandas as pd
import yfinance as yf
from model_backend.model.keras_model.constants import MARKET_CLOSING_TIME


class RawDataSource(ABC):
    def __init__(self, ticker: str) -> None:
        self.ticker = ticker

    @abstractmethod
    def get_raw_df(self, period: str):
        pass


class YfinanceNSERawData(RawDataSource):
    ALLOWED_PERIOD_VALUES = {'1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'}
    OPEN_COLUMN = 'Open'
    HIGH_COLUMN = 'High'
    LOW_COLUMN = 'Low'
    CLOSE_COLUMN = 'Close'
    VOL_COLUMN = 'Volume'
    FEATURE_KEYS = [OPEN_COLUMN, HIGH_COLUMN, LOW_COLUMN, CLOSE_COLUMN, VOL_COLUMN]
    # STOCK_CSV_BASE_PATH = 'stocks_csv'

    def get_raw_df(self, period: str = 'max') -> pd.DataFrame:
        date = dt.datetime.now().date()
        market_closed = True if dt.datetime.now().time() > MARKET_CLOSING_TIME else False
        return self._get_raw_df(date, market_closed, period)

    """
    When current date changes or market closes, new data is supposed to be fetched.
    So, the date and market_closed args exist only to figure out when to call this func again rather than returning cached data 
    """
    @lru_cache(maxsize=128)
    def _get_raw_df(self, date: dt.date, market_closed: bool, period: str = 'max') -> pd.DataFrame:
        print(f'\nget_raw {self.ticker}\n')
        if period not in self.ALLOWED_PERIOD_VALUES:
            raise ValueError(f"'{period}' is not a valid value for period. It must be one of {self.ALLOWED_PERIOD_VALUES}")

        # validate_ticker(self.ticker)
        ticker = self.ticker + '.NS'
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        self.validate_raw_df(df)
        return df

    def validate_raw_df(self, df):
        for column in self.FEATURE_KEYS:
            if column not in df.columns:
                raise FeatureColNotPresentInDfError(column)


class FeatureColNotPresentInDfError(Exception):
    def __init__(self, column: str) -> None:
        msg = f"'{column}' column not present in df received from yfinance"
        super().__init__(msg)
