from django.contrib import admin
from .models import Summoner, Platform



admin.site.register([Summoner, Platform])

# @admin.register(SummonerOverview)
# class SummonerOverviewAdmin(admin.ModelAdmin):
#     readonly_fields = ('created_at','updated_at')