import datetime as dt
from abc import ABC, abstractmethod
from typing import Type

from .data_processor import DataProcessor
from .raw_data import RawDataSource


class PreprocessedData(ABC):
    @abstractmethod
    def __init__(self, ticker: str, data_processor: Type[DataProcessor],
                 raw_data_source: Type[RawDataSource]) -> None:
        """Init method"""

    @abstractmethod
    def get_preprocessed_datasets(self):
        """Returns train, val and test dataset"""

    @abstractmethod
    def get_preprocessed_prediction_dataset(self, pred_date: dt.date):
        """Returns dataset to be used for prediction"""

    @abstractmethod
    def invTransform(self, y):
        """Returns inverse transformed predictions"""
