import datetime as dt
import os
from abc import ABC, abstractmethod
from typing import List, Type

import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

from .raw_data import RawDataSource


# have another dataprocessor class if you want data of multiple tickers to be used for training
class DataProcessor(ABC):
    def __init__(self, ticker: str, raw_data_source: Type[RawDataSource]) -> None:
        self.raw_data_source = raw_data_source(ticker)

    @ abstractmethod
    def get_preprocessed_dfs(self):
        """Returns train, val and test dataframes"""

    @ abstractmethod
    def get_preprocessed_prediction_df(self, pred_date: dt.date):
        """Returns a preprocessed dataframe to be used for prediction"""

    @abstractmethod
    def invTransform(self, y):
        """Returns inverse transformed predictions"""


class PandasDataProcessor(DataProcessor):
    TEST_SPLIT_FRACTION = 0.2
    VAL_SPLIT_FRACTION = 0.2

    def __init__(self, ticker: str, raw_data_source: Type[RawDataSource],
                 seq_len: int, step: int, future_predict_period: str) -> None:
        super().__init__(ticker, raw_data_source)
        self.ticker = ticker
        self.seq_len = seq_len
        self.step = step
        self.future_predict_period = future_predict_period

    def get_preprocessed_dfs(self) -> List[pd.DataFrame]:
        df = self.raw_data_source.get_raw_df()
        df = df[self.raw_data_source.FEATURE_KEYS]

        train_data, val_data, test_data = self.train_val_test_split(df)

        train_x, train_y, scaler = self.get_preprocessed_df(train_data)
        val_x, val_y, _ = self.get_preprocessed_df(val_data, scaler)
        test_x, test_y, _ = self.get_preprocessed_df(test_data, scaler)

        self.save_scaler(scaler)

        return (train_x, train_y), (val_x, val_y),  (test_x, test_y)

    def get_preprocessed_df(self, df: pd.DataFrame, scaler=None, return_y: bool = True):
        df = df.astype(np.float64)
        df.dropna(inplace=True)

        df = df[df[self.raw_data_source.VOL_COLUMN] != 0]

        df = df.pct_change()
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        df.dropna(inplace=True)
        df.reset_index(inplace=True, drop=True)

        if scaler is None:
            scaler = StandardScaler().fit(df)
        df = pd.DataFrame(scaler.transform(df), columns=self.raw_data_source.FEATURE_KEYS)

        if return_y:
            df['target'] = df[self.raw_data_source.CLOSE_COLUMN].shift(-self.future_predict_period)
            df.dropna(inplace=True)
            return df[self.raw_data_source.FEATURE_KEYS], df['target'], scaler

        return df, scaler

    def get_preprocessed_prediction_df(self, pred_date: dt.date) -> pd.DataFrame:
        # after preprocessing data, some rows will get dropped, so that's why x=x.tail(seq_len) needs to be done after preprocessing
        df = self.raw_data_source.get_raw_df()
        # in loc the end index is included so subtracting 1
        end_date = pred_date - dt.timedelta(days=1)
        df = df.loc[:end_date]

        df = df[self.raw_data_source.FEATURE_KEYS]
        scaler = self.get_scaler()
        x, _ = self.get_preprocessed_df(df, scaler=scaler, return_y=False)

        len_x = len(x)
        if len_x < self.seq_len:
            raise NotEnoughSequencesError(self.seq_len, len_x)

        x = x.tail(self.seq_len)
        return x

    def train_val_test_split(self, df: pd.DataFrame) -> List[pd.DataFrame]:
        test_split = int((1-self.TEST_SPLIT_FRACTION) * len(df))
        x = df[: test_split]
        test_data = df[test_split:]

        val_split = int((1-self.VAL_SPLIT_FRACTION) * len(x))
        train_data = x[:val_split]
        val_data = x[val_split:]
        return train_data, val_data, test_data

    def save_scaler(self, scaler: StandardScaler) -> None:
        file_path = self.get_scaler_file_path()
        joblib.dump(scaler, file_path)

    def get_scaler(self) -> StandardScaler:
        file_path = self.get_scaler_file_path()
        if not os.path.exists(file_path):
            raise ScalerNotFoundError(file_path, self.ticker, self.seq_len, self.step)
        return joblib.load(file_path)

    def get_scaler_file_path(self):
        base_dir = os.path.dirname(os.path.realpath(__file__))
        scaler_path = os.path.join(base_dir, 'scalers')
        ticker_path = os.path.join(scaler_path, self.ticker)

        if not os.path.exists(ticker_path):
            os.makedirs(ticker_path)

        file_path = os.path.join(ticker_path, 'scaler.gz')
        return file_path

    def invTransform(self, y):
        colNames = self.raw_data_source.FEATURE_KEYS
        closeCol = self.raw_data_source.CLOSE_COLUMN
        scaler = self.get_scaler()

        dummy = pd.DataFrame(np.zeros((len(y), len(colNames))), columns=colNames)
        dummy[closeCol] = y
        dummy = pd.DataFrame(scaler.inverse_transform(dummy), columns=colNames)
        return dummy[closeCol].values[0]


class NotEnoughSequencesError(Exception):
    def __init__(self, seq_len: int, len_x: int) -> None:
        msg = f"We need {seq_len} number of sequences to be able to predict but for the passed date only {len_x} number of sequences are there. Please try a higher date."
        super().__init__(msg)


class ScalerNotFoundError(Exception):
    def __init__(self, file_path: str, ticker: str, seq_len: int, step: int) -> None:
        msg = f"Scaler for model with seq_len={seq_len} and step={step} trained for ticker: {ticker} not found. Expected to find it at this location: {file_path}. Please train such a model first."
        super().__init__(msg)
