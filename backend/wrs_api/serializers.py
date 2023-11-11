from rest_framework import serializers
from .models import Car, SummonerOverview

class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = ['id','make','model','year']
    

class SummonerOverviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = SummonerOverview
        fields = '__all__'