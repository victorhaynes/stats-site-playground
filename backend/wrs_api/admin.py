from django.contrib import admin
from .models import Car, SummonerOverview



admin.site.register([Car])

@admin.register(SummonerOverview)
class SummonerOverviewAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at','updated_at')