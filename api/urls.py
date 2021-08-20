from django.urls import path

from . import views

urlpatterns = [
    path('predict/<int:pk>/', views.predict, name='predict'),
    path('models/<str:symbol>/', views.ticker_models, name='ticker_models'),
    path('models/', views.all_models, name='all_models'),
    path('tickers/', views.all_tickers, name='tickers'),
]
