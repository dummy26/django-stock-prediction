from django.urls import path

from . import views

urlpatterns = [
    path('train/', views.train, name='train'),
    path('train/new/', views.train_new, name='train_new'),
    path('predict/<int:pk>/', views.predict, name='predict'),
    path('models/<str:symbol>/', views.all_models, name='models'),
    path('tickers/', views.all_tickers, name='tickers'),
]
