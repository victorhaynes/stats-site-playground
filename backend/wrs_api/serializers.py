from rest_framework import serializers
from .models import Summoner, SummonerOverview, MatchHistory


class SummonerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Summoner
        fields = '__all__'


class SummonerOverviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = SummonerOverview
        # fields = '__all__'
        fields = ['overview']


class MatchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchHistory
        fields = ['all_match_history']
