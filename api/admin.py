from django.contrib import admin

from api.models import Model, Prediction, Ticker

admin.site.register(Model)
admin.site.register(Ticker)
admin.site.register(Prediction)
