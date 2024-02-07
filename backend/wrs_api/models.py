from django.db import models
    

class Summoner(models.Model):
    puuid = models.CharField(max_length=100)
    gameName = models.CharField(max_length=50)
    tagLine = models.CharField(max_length=10)
    region = models.CharField(max_length=40)
    profileIconId = models.IntegerField(blank=True)
    encryptedSummonerId = models.CharField(max_length=100)
    summonerName = models.CharField(max_length=100, blank=True)

    # class Meta:
    #     unique_together = ('gameName', 'tagLine', 'region')

    def __str__(self):
        try:
            return f"{self.gameName}#{self.tagLine}"
        except KeyError:
            return "MISSING INFO"


class Season(models.Model):
    season = models.IntegerField()
    split = models.IntegerField()
    # split_1_start_date = models.DateField()
    # split_1_start_end = models.DateField()
    # split_2_start_date = models.DateField()
    # split_2_start_end = models.DateField()
    # split_3_start_date = models.DateField()
    # split_3_start_end = models.DateField()

    def __str__(self):
        return f"season: {self.season}, split: {self.split}"


# Persistent and will match source of truth when updated
class SummonerOverview(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="summoner_overviews")
    summoner = models.ForeignKey(Summoner, on_delete=models.CASCADE, related_name="summoner_overviews")
    json = models.JSONField(default=dict)

    def __str__(self):
        try:
            return f"{self.overview['tier']}"
        except KeyError:
            return f"UNRANKED"

    class Meta:
        unique_together = ('season', 'summoner')


# Persistent but will not keep track of complete history, only recent games so client has something to display
class MatchDetails(models.Model):
    summoner = models.OneToOneField(Summoner, on_delete=models.CASCADE, related_name="match_details")
    json = models.JSONField(default=list)


# Persistent and will be complete history per season (necessary for LP +/- gains, feature unimplemented)
class MatchHistory(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="histories")
    summoner = models.ForeignKey(Summoner, on_delete=models.CASCADE, related_name="histories")
    json = models.JSONField(default=list)

    class Meta:
        unique_together = ('season', 'summoner')

    # def __str__(self):
    #     return self.season.split
        

