from django.utils.datastructures import MultiValueDictKeyError
from model_backend.model.keras_model.utils import InvalidPredictionDateError
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.models import Model, Prediction, Ticker
from api.serializers import (ModelSerializer, PredictionSerializer,
                             TickerSerializer)

from .utils import get_ticker_from_symbol


@api_view(['POST'])
def train_new(request):
    try:
        name = request.data['name'].lower()
        symbol = request.data['ticker']
        seq_len = int(request.data['seq_len'])
        step = int(request.data['step'])
        epochs = int(request.data.get('epochs', 1))
    except (MultiValueDictKeyError, ValueError):
        return Response(f'Invalid params', status=status.HTTP_404_NOT_FOUND)

    if epochs < 1:
        return Response(f"Epochs can't be less than 1", status=status.HTTP_404_NOT_FOUND)

    ticker = get_ticker_from_symbol(symbol)
    if ticker is None:
        return Response(f'Invalid symbol: {symbol}', status=status.HTTP_404_NOT_FOUND)

    # check if model already exists
    model = Model.objects.filter(ticker=ticker, seq_len=seq_len, step=step, name=name).first()
    if model is not None:
        return Response(f'Model with name={name} seq_len={seq_len} step={step} for symbol {ticker.symbol} already exists. Please use /api/train/{model.id}/ to POST a train request.', status=status.HTTP_404_NOT_FOUND)

    # ticker coming from request.data might be in different case so changing it to coreect value
    data = request.data.copy()
    data['ticker'] = ticker.pk
    serializer = ModelSerializer(data=data)
    if not serializer.is_valid():
        return Response(f'Invalid params', status=status.HTTP_404_NOT_FOUND)

    model = serializer.save()
    # model.train(epochs)
    print('training new model......\n')
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def train(request):
    try:
        pk = int(request.data['id'])
        epochs = int(request.data.get('epochs', 1))
    except (MultiValueDictKeyError, ValueError):
        return Response(f'Invalid params', status=status.HTTP_404_NOT_FOUND)

    if epochs < 1:
        return Response(f"Epochs can't be less than 1", status=status.HTTP_404_NOT_FOUND)

    model = Model.objects.filter(pk=pk).first()
    if model is None:
        return Response(f'No model with id={pk} found', status=status.HTTP_404_NOT_FOUND)

    # model.train(epochs)
    print('training......\n')
    serializer = ModelSerializer(model)
    return Response(serializer.data, status=status.HTTP_200_OK)


@ api_view(['GET'])
def predict(request, pk):
    pred_date = request.GET.get('pred_date')
    if pred_date is None:
        return Response('pred_date not found in query parameters', status=status.HTTP_404_NOT_FOUND)
    model = Model.objects.filter(pk=pk).first()

    if model is None:
        return Response(f'No model with id={pk} found', status=status.HTTP_404_NOT_FOUND)

    prediction_obj = Prediction.objects.filter(model=model, pred_date=pred_date).first()
    if prediction_obj is None:
        try:
            y, actual_pred_date = model.predict(pred_date)
        except InvalidPredictionDateError:
            return Response(f'Invalid prediction date given: {pred_date}', status=status.HTTP_404_NOT_FOUND)

        prediction_obj = Prediction.objects.create(model=model, pred_date=actual_pred_date, prediction=y)

    serializer = PredictionSerializer(prediction_obj)
    return Response(serializer.data, status=status.HTTP_200_OK)


@ api_view(['GET'])
def all_models(request, symbol):
    ticker = get_ticker_from_symbol(symbol)
    if ticker is None:
        return Response(f'Invalid symbol given: {symbol}', status=status.HTTP_404_NOT_FOUND)

    models = Model.objects.filter(ticker=ticker)
    serializer = ModelSerializer(models, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)


@ api_view(['GET'])
def all_tickers(request):
    tickers = Ticker.objects.all().order_by('symbol')
    serializer = TickerSerializer(tickers, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)
