from rest_framework import serializers
from .models import Car, SummonerOverview, MatchHistory, RankedLpHistory

class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = ['id','make','model','year']
    

class SummonerOverviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = SummonerOverview
        # fields = '__all__'
        fields = ['overview']


class MatchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchHistory
        fields = ['history']


class RankedLpHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RankedLpHistory
        fields = ['lp_history']


