# This API allows you to get stock price predictions for selected Indian stocks.

API is built using [Django REST framework](https://www.django-rest-framework.org/).  
For prediction, code from my other repo ([Stock-Prediction](https://github.com/dummy26/Stock-Prediction)) is used.

## API Endpoints
- Tickers - `/api/tickers/`  
- Prediction (for a particular date) - `/api/prediction/reliance/?pred_date=2022-01-27`  
- Latest Prediction - `/api/prediction/reliance/?latest=True`  
- Predictions (period in days) - `/api/predictions/reliance/?period=10`

## Overview

`model_backend` is responsible for fetching raw data and making predictions. (For more info checkout [Stock-Prediction](https://github.com/dummy26/Stock-Prediction))  

When predictions are needed, we fetch them from the database if they are already present otherwise prediction is made using backend model 

### Django Models  
- `Ticker` - Represents a stock containing its symbol and company name
- `Model` - Represents a machine learning model for stock price prediction
- `Prediction` - Stores date of prediction, predicted  andactual stock price

