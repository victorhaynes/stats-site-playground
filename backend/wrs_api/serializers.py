from rest_framework import serializers
from .models import Season, Summoner, SummonerOverview, MatchHistory



class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = '__all__'


class MatchHistorySerializer(serializers.ModelSerializer):
    season = SeasonSerializer()

    class Meta:
        model = MatchHistory
        fields = ['all_match_history', 'season']

class SummonerOverviewSerializer(serializers.ModelSerializer):
    season = SeasonSerializer()
    
    class Meta:
        model = SummonerOverview
        # fields = '__all__'
        fields = ['overview', 'season']

# class SummonerOverviewField(serializers.RelatedField):
#     def to_representation(self, value):
#         return value.overview
    
class SummonerSerializer(serializers.ModelSerializer):
    # overviews = serializers.SlugRelatedField(many=True, read_only=True, slug_field='overview') - slug/out
    overviews = SummonerOverviewSerializer(many=True, read_only=True) 
    histories = MatchHistorySerializer(many=True, read_only=True)

    # - directionally correct
    
    # overviews = SummonerOverviewField(many=True, read_only=True) - custom, removes "overview" label from the array of overviews

    class Meta:
        model = Summoner
        fields = ['id', 'puuid', 'gameName', 'tagLine', 'region', 'profileIconId', 'encryptedSummonerId', 'summonerName', 'overviews', 
                  'histories']

