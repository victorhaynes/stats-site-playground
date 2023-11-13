from django.db import models

class Car(models.Model):
    make = models.CharField(max_length=200)
    model = models.CharField(max_length=200)
    year = models.IntegerField()


class SummonerOverview(models.Model):
        leagueId = models.CharField(max_length=200) 
        queueType = models.CharField(max_length=200) 
        tier = models.CharField(max_length=200) 
        rank = models.CharField(max_length=200) 
        summonerId = models.CharField(max_length=200) 
        summonerName = models.CharField(max_length=200) 
        leaguePoints = models.IntegerField()
        wins = models.IntegerField()
        losses = models.IntegerField()
        veteran = models.BooleanField()
        inactive = models.BooleanField()
        freshBlood = models.BooleanField()
        hotStreak = models.BooleanField()
        puuid = models.CharField(max_length=200, blank=True)