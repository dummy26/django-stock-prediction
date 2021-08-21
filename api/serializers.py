from rest_framework import serializers

from api.models import Model, Prediction, Ticker


class PredictionSerializer(serializers.ModelSerializer):
    symbol = serializers.ReadOnlyField(source='model.ticker.symbol')

    class Meta:
        model = Prediction
        # fields = ['model', 'prediction', 'pred_date']
        fields = ['prediction', 'pred_date', 'symbol']


class ModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Model
        fields = ['ticker']


class TickerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticker
        fields = ['symbol', 'company_name']
