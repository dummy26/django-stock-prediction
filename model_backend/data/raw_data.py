from abc import ABC, abstractmethod

import pandas as pd
import yfinance as yf


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

    # the file it fetches from fielsystem may not be the lastest one, so store date when file was stored in its name and comapare with current date
    """def get_raw_df(self, period: str = 'max') -> pd.DataFrame:
        if period not in self.ALLOWED_PERIOD_VALUES:
            raise ValueError(f"'{period}' is not a valid value for period. It must be one of {self.ALLOWED_PERIOD_VALUES}")

        dirname = os.path.dirname(os.path.realpath(__file__))
        base_path = os.path.join(dirname, STOCK_CSV_BASE_PATH)
        file_path = os.path.join(base_path, self.ticker + '.csv')

        if not os.path.exists(base_path):
            os.mkdir(base_path)

        if not os.path.exists(file_path):
            df = self.__get_raw_df()
            df.to_csv(file_path)

        df = pd.read_csv(file_path)
        return df"""

    def get_raw_df(self, period: str = 'max') -> pd.DataFrame:
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
