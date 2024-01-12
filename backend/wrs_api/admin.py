from django.contrib import admin
from .models import Summoner, SummonerOverview, MatchHistory



admin.site.register([Summoner, MatchHistory, SummonerOverview])

# @admin.register(SummonerOverview)
# class SummonerOverviewAdmin(admin.ModelAdmin):
#     readonly_fields = ('created_at','updated_at')