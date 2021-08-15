from django.core.validators import MinValueValidator
from django.db import models
from model_backend.data.data_processor import PandasDataProcessor
from model_backend.data.keras_data.keras_preprocessed_data import \
    KerasPreprocessedData
from model_backend.data.raw_data import YfinanceNSERawData
from model_backend.model.keras_model.keras_model import LstmModel


class Ticker(models.Model):
    symbol = models.CharField(max_length=50, primary_key=True)
    company_name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return f'{self.symbol}-{self.company_name}'


class Model(models.Model):
    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE)
    seq_len = models.IntegerField(validators=[MinValueValidator(1)])
    step = models.IntegerField(validators=[MinValueValidator(1)])
    name = models.CharField(max_length=50)

    def _create_model(self):
        backend_model = LstmModel(self.ticker.symbol, KerasPreprocessedData, PandasDataProcessor, YfinanceNSERawData, self.name)
        return backend_model

    def train(self, epochs):
        backend_model = self._create_model()
        backend_model.train(epochs)

    def predict(self, pred_date):
        backend_model = self._create_model()
        return backend_model.predict(pred_date)

    def __str__(self) -> str:
        return f'{self.name}-{self.seq_len}-{self.step}-{self.ticker.symbol}'


class Prediction(models.Model):
    model = models.ForeignKey(Model, on_delete=models.CASCADE)
    prediction = models.FloatField()
    pred_date = models.DateField()
