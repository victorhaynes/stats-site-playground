from django.contrib import admin
from .models import Season, Summoner, SummonerOverview, MatchHistory



admin.site.register([Season, Summoner, MatchHistory, SummonerOverview])

# @admin.register(SummonerOverview)
# class SummonerOverviewAdmin(admin.ModelAdmin):
#     readonly_fields = ('created_at','updated_at')