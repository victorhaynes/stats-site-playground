## While SummonerOverview and MatchHistory do have overlap in fields, having a parent class "Summoner"
## does not fit the use case for this API as there is no "Summoner" class equivalent that can be retrieved
## from the Riot API. And therefore there is no reason to be storing "Summoner" in the database.
## There seemingly is room for a "has-one/belongs-to" for SummonerOverview and MatchHistory 
## but Riot-side these are not actually coupled in anyway. Additionally, SummonerOverview would naturally own a MatchHistory
## but SummonerOverview will not lopgically exist for every end user.


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
    gameName = models.CharField(max_length=50)
    tagLine = models.CharField(max_length=20)
    region = models.CharField(max_length=50)
    puuid = models.CharField(max_length=200, unique=True)
    overview = models.JSONField(default=dict)

    def __str__(self):
        try:
            return f"{self.gameName} #{self.tagLine} {self.overview['tier']}"
        except KeyError:
            return f"{self.gameName} #{self.tagLine} UNRANKED"

    class Meta:
        unique_together = ('gameName', 'tagLine', 'region')


class MatchHistory(models.Model):
    gameName = models.CharField(max_length=50)
    tagLine = models.CharField(max_length=20)
    region = models.CharField(max_length=50)
    puuid = models.CharField(max_length=200, unique=True)
    history = models.JSONField(default=list)

    def __str__(self):
        return f"{self.gameName} #{self.tagLine}"

    class Meta:
        unique_together = ('gameName', 'tagLine', 'region')







# class SummonerOverview(models.Model):
#     # leagueId = models.CharField(max_length=200, blank=True) 
#     # queueType = models.CharField(max_length=50, blank=True) 
#     # tier = models.CharField(max_length=50) 
#     # rank = models.CharField(max_length=50) 
#     # summonerId = models.CharField(max_length=200) 
#     # summonerName = models.CharField(max_length=50, blank=True) 
#     # leaguePoints = models.IntegerField()
#     # wins = models.IntegerField()
#     # losses = models.IntegerField()
#     # veteran = models.BooleanField()
#     # inactive = models.BooleanField()
#     # freshBlood = models.BooleanField()
#     # hotStreak = models.BooleanField()
#     # puuid = models.CharField(max_length=200, blank=True)
#     # profileIcon = models.CharField(max_length=200, blank=True)
#     # gameName = models.CharField(max_length=50)
#     # tagLine = models.CharField(max_length=20)
#     # created_at = models.DateTimeField(auto_now_add=True)
#     # updated_at = models.DateTimeField(auto_now=True)
#     # region = models.CharField(max_length=200)

#     gameName = models.CharField(max_length=50)
#     tagLine = models.CharField(max_length=20)
#     region = models.CharField(max_length=50)
#     puuid = models.CharField(max_length=200, unique=True)
#     overview = models.JSONField(default=dict)

#     class Meta:
#         unique_together = ('gameName', 'tagLine', 'region')
#         # constraints = [
#         #     # models.UniqueConstraint(fields=['gameName','tagLine,','region'], name="summoner_name_region_uniqueness")
#         # ]

# class MatchHistory(models.Model):
#     gameName = models.CharField(max_length=50)
#     tagLine = models.CharField(max_length=20)
#     region = models.CharField(max_length=50)
#     puuid = models.CharField(max_length=200, unique=True)
#     history = models.JSONField(default=list)

#     class Meta:
#         unique_together = ('gameName', 'tagLine', 'region')
#     # class Meta:
#     #     constraints = [
#     #         models.UniqueConstraint(fields=['gameName','tagLine,','region'], name="match_history_name_region_uniqueness")
#     #     ]