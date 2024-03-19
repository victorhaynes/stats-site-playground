from django.db import models
    

## 120 M ranked games globally per split, all regions

class Summoner(models.Model):
    puuid = models.CharField(max_length=100)
    gameName = models.CharField(max_length=50)
    tagLine = models.CharField(max_length=10)
    region = models.CharField(max_length=40)
    profileIconId = models.IntegerField(blank=True)
    encryptedSummonerId = models.CharField(max_length=100)
    summonerName = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # class Meta:
    #     unique_together = ('gameName', 'tagLine', 'region')

    def __str__(self):
        try:
            return f"{self.gameName}#{self.tagLine}"
        except KeyError:
            return "MISSING INFO"

# class AllMatchesPlayed(models.Model):
#     # season = yada - belongs to season
#     # matchID = yada
#     # region = yada - belongs to region
#     # summoner_id = yada - belong to summoner
#     # detailed_json = yada
#     pass

# class MetaInfo(models.Model):
#     season = models.IntegerField()
#     split = models.IntegerField()
#     patch = models.CharField(max_length=15, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         unique_together = ('season', 'split', 'patch')

class Season(models.Model):
    season = models.IntegerField()
    split = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    split_1_start_date = models.DateField()
    split_1_start_end = models.DateField()
    split_2_start_date = models.DateField()
    split_2_start_end = models.DateField()
    split_3_start_date = models.DateField()
    split_3_start_end = models.DateField()

    def __str__(self):
        return f"season: {self.season}, split: {self.split}"


# Persistent and will match source of truth when updated
class SummonerOverview(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="summoner_overviews")
    summoner = models.ForeignKey(Summoner, on_delete=models.CASCADE, related_name="summoner_overviews")
    json = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# Persistent and will be complete history per season (necessary for LP +/- gains, feature unimplemented)
class MatchHistory(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="histories")
    summoner = models.ForeignKey(Summoner, on_delete=models.CASCADE, related_name="histories")
    json = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('season', 'summoner')

    # def __str__(self):
    #     return self.season.split
        

