from model_backend.data.data_processor import ScalerNotFoundError
from model_backend.model.keras_model.utils import InvalidPredictionDateError
from model_backend.model.model import ModelNotFoundError
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.models import Model, Prediction, Ticker
from api.serializers import (ModelSerializer, PredictionSerializer,
                             TickerSerializer)
from api.utils import get_ticker_from_symbol


@ api_view(['GET'])
def prediction(request, symbol):
    ticker = get_ticker_from_symbol(symbol)
    if ticker is None:
        return Response(f'Invalid symbol given: {symbol}', status=status.HTTP_404_NOT_FOUND)

    model = Model.objects.filter(ticker=ticker).first()
    if model is None:
        return Response(f'No model for ticker: {ticker} found', status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    pred_date = request.GET.get('pred_date')
    if pred_date is None:
        return Response('pred_date not found in query parameters', status=status.HTTP_404_NOT_FOUND)

    prediction_obj = Prediction.objects.filter(model=model, pred_date=pred_date).first()
    if prediction_obj is None:
        try:
            y, actual_pred_date = model.predict(pred_date)
        except InvalidPredictionDateError:
            return Response(f'Invalid prediction date given: {pred_date}', status=status.HTTP_404_NOT_FOUND)
        except (ModelNotFoundError, ScalerNotFoundError):
            return Response(f'Could not find model files.', status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        prediction_obj = Prediction.objects.create(model=model, pred_date=actual_pred_date, prediction=y)

    serializer = PredictionSerializer(prediction_obj)
    return Response(serializer.data, status=status.HTTP_200_OK)


@ api_view(['GET'])
def all_models(request):
    models = Model.objects.all()
    serializer = ModelSerializer(models, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)


@ api_view(['GET'])
def all_tickers(request):
    tickers = Ticker.objects.all().order_by('symbol')
    serializer = TickerSerializer(tickers, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)
