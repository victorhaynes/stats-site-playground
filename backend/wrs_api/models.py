from django.db import models

class Car(models.Model):
    make = models.CharField(max_length=200)
    model = models.CharField(max_length=200)
    year = models.IntegerField()

class Summoner(models.Model):
    gameName = models.CharField(max_length=20)
    tagLine = models.CharField(max_length=10)
    puuid = models.CharField(max_length=100)
    summonerName = models.CharField(max_length=100, blank=True)
    tier = models.CharField(max_length=50, blank=True)

class SummonerOverview(models.Model):
    leagueId = models.CharField(max_length=200, blank=True) 
    queueType = models.CharField(max_length=50, blank=True) 
    tier = models.CharField(max_length=50) 
    rank = models.CharField(max_length=50) 
    summonerId = models.CharField(max_length=200) 
    summonerName = models.CharField(max_length=50, blank=True) 
    leaguePoints = models.IntegerField()
    wins = models.IntegerField()
    losses = models.IntegerField()
    veteran = models.BooleanField()
    inactive = models.BooleanField()
    freshBlood = models.BooleanField()
    hotStreak = models.BooleanField()
    puuid = models.CharField(max_length=200, blank=True)
    profileIcon = models.CharField(max_length=200, blank=True)
    gameName = models.CharField(max_length=50)
    tagLine = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)