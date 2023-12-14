from django.contrib import admin
from .models import Car, SummonerOverview, MatchHistory



admin.site.register([Car, MatchHistory])

@admin.register(SummonerOverview)
class SummonerOverviewAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at','updated_at')