from model_backend.data.data_processor import PandasDataProcessor
from model_backend.data.keras_data.keras_preprocessed_data import \
    KerasPreprocessedData
from model_backend.data.raw_data import YfinanceNSERawData
from model_backend.model.keras_model.keras_model import LstmModel


class LstmModelRegistry:
    def __init__(self):
        self._registry = {}

    def register(self, symbol):
        self._registry[symbol.lower()] = LstmModel(symbol, KerasPreprocessedData, PandasDataProcessor, YfinanceNSERawData)

    def get_service_by_symbol(self, symbol):
        service = self._registry.get(symbol.lower())
        if not service:
            raise Exception(f'Not found service for ticker: {symbol}')
        return service


lstm_registry = LstmModelRegistry()
