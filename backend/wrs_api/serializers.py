from rest_framework import serializers
from .models import Summoner, SummonerOverview
from django.db import connection
from .utilities import dictfetchall


class SummonerSerializer(serializers.ModelSerializer):
    overviews = serializers.SerializerMethodField('get_related_overviews')


    def get_related_overviews(self, instance):
        sql = """
            SELECT * FROM wrs_api_summoneroverview WHERE puuid = %s AND platform = %s;
        """
        with connection.cursor() as cursor:
            cursor.execute(sql,[instance.puuid, str(instance.platform)])
            results = dictfetchall(cursor)

        return results

    class Meta:
        model = Summoner
        fields = ['id', 'puuid', 'gameName', 'tagLine', 'platform', 'profileIconId', 'encryptedSummonerId', 'most_recent_game','overviews', 'created_at', 'updated_at'] 


class SummonerOverviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = SummonerOverview
        fields = '__all__'