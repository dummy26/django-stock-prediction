import datetime as dt
from abc import ABC, abstractmethod
from typing import Union

from .validate import validate_ticker


class ModelNotFoundError(Exception):
    def __init__(self, ticker: str, seq_len: int, step: int) -> None:
        msg = f"There is no saved model for '{ticker}' with seq_len={seq_len} and step={step}. Please train such a model first."
        super().__init__(msg)


class Model(ABC):
    def __init__(self, ticker: str) -> None:
        validate_ticker(ticker)
        self.ticker = ticker

    @abstractmethod
    def train(self, epochs: int = 1):
        """Method to train a model"""

    @abstractmethod
    def predict(self, date: Union[dt.date, str]):
        """Method to give prediction for a date"""
