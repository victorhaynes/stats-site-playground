from django.contrib import admin
from .models import Car, SummonerOverview, MatchHistory, RankedLpHistory



admin.site.register([Car, MatchHistory, SummonerOverview, RankedLpHistory])

# @admin.register(SummonerOverview)
# class SummonerOverviewAdmin(admin.ModelAdmin):
#     readonly_fields = ('created_at','updated_at')