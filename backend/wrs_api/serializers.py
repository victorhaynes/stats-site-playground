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
        limit = 3
        if self.context.get("limit") and int(self.context.get("limit")) > limit:
            limit = self.context.get("limit")

        # Query is not queue-specific get all matches up to a limit 
        if not self.context.get('queueId'):
            partition_name = "_" + instance.platform.code
            formatted_table_names = [partition_name] * 10

            sql =   """
                        SELECT wrs_api_summonermatch{}."matchId", wrs_api_match{}."queueId", wrs_api_match{}.metadata
                        FROM wrs_api_summonermatch{}
                        JOIN wrs_api_match{} ON wrs_api_summonermatch{}."matchId" = wrs_api_match{}."matchId"
                        WHERE wrs_api_summonermatch{}.puuid = %s 
                            AND wrs_api_summonermatch{}.platform = %s
                        ORDER BY wrs_api_summonermatch{}."matchId" DESC
                        LIMIT %s;

                    """.format(*formatted_table_names)

            params = [
                instance.puuid,
                instance.platform.code,
                limit
            ]       

            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                results = dictfetchall(cursor)
            return format_match_strings_as_json(results)
        
        # If query is queue-specific get all matches of a certain type up to a limit 
        elif self.context.get('queueId'):
            partition_name = "_" + instance.platform.code
            formatted_table_names = [partition_name] * 11

            sql =   """
                        SELECT wrs_api_summonermatch{}."matchId", wrs_api_match{}."queueId", wrs_api_match{}.metadata
                        FROM wrs_api_summonermatch{}
                        JOIN wrs_api_match{} ON wrs_api_summonermatch{}."matchId" = wrs_api_match{}."matchId"
                        WHERE wrs_api_summonermatch{}."queueId" = %s 
                            AND wrs_api_summonermatch{}.puuid = %s 
                            AND wrs_api_summonermatch{}.platform = %s
                        ORDER BY wrs_api_summonermatch{}."matchId" DESC
                        LIMIT %s;
                    """.format(*formatted_table_names)
            
            params = [
                    int(self.context.get("queueId")), 
                    instance.puuid,
                    instance.platform.code,
                    limit]   

            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                results = dictfetchall(cursor)
            return format_match_strings_as_json(results)


    class Meta:
        model = Summoner
        fields = ['id', 'puuid', 'gameName', 'tagLine', 'platform', 'profileIconId', 'encryptedSummonerId', 'most_recent_game','overviews', 'match_history', 'created_at', 'updated_at'] 

 

