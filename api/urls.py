from django.urls import path

from . import views

urlpatterns = [
    path('prediction/<str:symbol>/', views.prediction, name='prediction'),
    path('predictions/<str:symbol>/', views.predictions, name='predictions'),
    path('models/', views.all_models, name='all_models'),
    path('tickers/', views.all_tickers, name='tickers'),
]
