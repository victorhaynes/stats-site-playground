from django.contrib import admin
from .models import Car, SummonerOverview

admin.site.register([Car, SummonerOverview])