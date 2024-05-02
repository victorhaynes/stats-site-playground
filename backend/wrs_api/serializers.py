from rest_framework import serializers
from .models import Summoner, SummonerOverview, Match
from django.db import connection
from .utilities import dictfetchall, format_match_strings_as_json, format_overview_strings_as_json
import json




class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = '__all__'

class SummonerOverviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = SummonerOverview
        fields = '__all__'


class SummonerSerializer(serializers.ModelSerializer):
    overviews = SummonerOverviewSerializer(many=True, read_only=True)
    # matches = MatchSerializer(many=True, read_only=True)

    class Meta:
        model = Summoner
        # fields = ['id', 'puuid', 'gameName', 'tagLine', 'platform', 'profileIconId', 'encryptedSummonerId', 'most_recent_game','overviews', 'created_at', 'updated_at'] 
        fields = ['puuid','overviews', 'created_at', 'updated_at'] 



class SummonerCustomSerializer(serializers.ModelSerializer):
    overviews = serializers.SerializerMethodField('get_related_overviews')
    match_history = serializers.SerializerMethodField('get_related_matches')

    def get_related_overviews(self, instance):
        sql =   """
                    SELECT * FROM wrs_api_summoneroverview WHERE puuid = %s AND platform = %s
                    ORDER BY id DESC;
                """
        with connection.cursor() as cursor:
            cursor.execute(sql,[instance.puuid, instance.platform.code])
            results = dictfetchall(cursor)
        return format_overview_strings_as_json(results)

    def get_related_matches(self, instance):
        sql =   """
                    SELECT wrs_api_summonermatch."matchId",  wrs_api_match.metadata, wrs_api_match."queueId"
                    FROM wrs_api_summonermatch 
                    JOIN wrs_api_match ON wrs_api_summonermatch."matchId" = wrs_api_match."matchId"
                    WHERE wrs_api_summonermatch.puuid = %s AND wrs_api_summonermatch.platform = %s
                    ORDER BY wrs_api_summonermatch."matchId" DESC
                    LIMIT %s;
                """
        with connection.cursor() as cursor:
            cursor.execute(sql,[instance.puuid, instance.platform.code, self.context.get('limit')])
            results = dictfetchall(cursor)
        return format_match_strings_as_json(results)

    class Meta:
        model = Summoner
        fields = ['id', 'puuid', 'gameName', 'tagLine', 'platform', 'profileIconId', 'encryptedSummonerId', 'most_recent_game','overviews', 'match_history', 'created_at', 'updated_at'] 

 

