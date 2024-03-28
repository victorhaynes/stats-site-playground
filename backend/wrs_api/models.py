from django.db import models
# from psqlextra.types import PostgresPartitioningMethod
# from psqlextra.models import PostgresPartitionedModel, PostgresModel


# thought process:
# make sure the model that needs partitioning is unmanaged, give it a name that fits name convention
# then add raw runSQL() in the appropriate place in the migration

class Season(models.Model):    
    season = models.IntegerField()
    split = models.IntegerField()


class Patch(models.Model):
    full_version = models.CharField(max_length=25, primary_key=True)
    version = models.CharField(max_length=6)
    season = models.ForeignKey(Season, on_delete=models.CASCADE, db_column="season")


class Region(models.Model):
    name_optons = [("americas", "americas"), ("asia", "asia"), ("europe", "europe"), ("sea", "sea")]
    name = models.CharField(choices=name_optons, primary_key=True)


class Platform(models.Model):
    code_options = [("na1","na1"), ("euw1","euw1"), ("br1","br1")]
    code = models.CharField(choices=code_options, primary_key=True)   

    def __str__(self):
        return self.code

class GameMode(models.Model):
    queueId = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=30)


class Champion(models.Model):
    championId = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=30)


class LegendaryItem(models.Model):
    itemId = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=30)


class TierTwoBoot(models.Model):
    itemId = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=30)


class Summoner(models.Model):
    puuid = models.CharField(max_length=100)
    gameName = models.CharField(max_length=50)
    tagLine = models.CharField(max_length=10)
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, db_column="platform", to_field="code")
    profileIconId = models.IntegerField()
    encryptedSummonerId = models.CharField(max_length=100)
    most_recent_game = models.CharField(max_length=25, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        unique_together = ["puuid", "platform"]
        db_table = "wrs_api_summoner"
        managed = False

    def __str__(self):
        try:
            return f"{self.gameName}#{self.tagLine}"
        except KeyError:
            return "MISSING INFO"

# Unmanaged - custom PSQL table definition, composite PK (season_id, puuid, platform)
# Partitioned
class SummonerOverview(models.Model):
    season_id = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="summoner_overviews")
    # Got rid of to_field="puuid" since technically it is not a PK to Django, but it is part of a composite PK in PSQL
    puuid = models.ForeignKey(Summoner, on_delete=models.CASCADE, related_name="summoner_overviews")
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, db_column="platform", to_field="code")
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        try:
            return f"{self.overview['tier']}"
        except KeyError:
            return f"UNRANKED"
    
    class Meta:
        unique_together = ["season_id", "puuid", "platform"]
        db_table = "wrs_api_summoneroverview"
        managed = False


# class Match(models.Model):
#     matchId = models.CharField(max_length=20)
#     season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="matches")
#     patch = models.ForeignKey(Patch, on_delete=models.CASCADE, related_name="matches", to_field="full_version")
#     queueId = models.ForeignKey(GameMode, on_delete=models.CASCADE, to_field="queueId")
#     summoners = models.ManyToManyField(Summoner)
#     platform = models.ForeignKey(Platform, on_delete=models.CASCADE, db_column="platform", to_field="code")
#     metadata = models.JSONField(default=dict)

# class ChampionStat(models.Model):    
#     champion = models.ForeignKey(Champion, on_delete=models.CASCADE, to_field="championId")
#     wins = models.IntegerField()
#     losses = models.IntegerField()
#     picked = models.IntegerField()
#     banned = models.IntegerField()
#     season = models.ForeignKey(Season, on_delete=models.CASCADE)
#     patch = models.ForeignKey(Patch, on_delete=models.CASCADE, to_field="full_version")
#     platform = models.ForeignKey(Platform, on_delete=models.CASCADE, db_column="platform", to_field="code")


# class BuiltFirstStat(models.Model):
#     legendary_item = models.ForeignKey(LegendaryItem, on_delete=models.CASCADE)
#     champion = models.ForeignKey(Champion, on_delete=models.CASCADE, to_field="championId")
#     wins = models.IntegerField()
#     losses = models.IntegerField()
#     season = models.ForeignKey(Season, on_delete=models.CASCADE)
#     patch = models.ForeignKey(Patch, on_delete=models.CASCADE, to_field="full_version")
#     platform = models.ForeignKey(Platform, on_delete=models.CASCADE, db_column="platform", to_field="code")


# class BuiltSecondStat(models.Model):
#     legendary_item = models.ForeignKey(LegendaryItem, on_delete=models.CASCADE)
#     champion = models.ForeignKey(Champion, on_delete=models.CASCADE, to_field="championId")
#     wins = models.IntegerField()
#     losses = models.IntegerField()
#     season = models.ForeignKey(Season, on_delete=models.CASCADE)
#     patch = models.ForeignKey(Patch, on_delete=models.CASCADE, to_field="full_version")
#     platform = models.ForeignKey(Platform, on_delete=models.CASCADE, db_column="platform", to_field="code")


# class BuiltThirdStat(models.Model):
#     legendary_item = models.ForeignKey(LegendaryItem, on_delete=models.CASCADE)
#     champion = models.ForeignKey(Champion, on_delete=models.CASCADE, to_field="championId")
#     wins = models.IntegerField()
#     losses = models.IntegerField()
#     season = models.ForeignKey(Season, on_delete=models.CASCADE)
#     patch = models.ForeignKey(Patch, on_delete=models.CASCADE, to_field="full_version")
#     platform = models.ForeignKey(Platform, on_delete=models.CASCADE, db_column="platform", to_field="code")


# class BuiltForthStat(models.Model):
#     legendary_item = models.ForeignKey(LegendaryItem, on_delete=models.CASCADE)
#     champion = models.ForeignKey(Champion, on_delete=models.CASCADE, to_field="championId")
#     wins = models.IntegerField()
#     losses = models.IntegerField()
#     season = models.ForeignKey(Season, on_delete=models.CASCADE)
#     patch = models.ForeignKey(Patch, on_delete=models.CASCADE, to_field="full_version")
#     platform = models.ForeignKey(Platform, on_delete=models.CASCADE, db_column="platform", to_field="code")


# class BuiltFifthStat(models.Model):
#     legendary_item = models.ForeignKey(LegendaryItem, on_delete=models.CASCADE)
#     champion = models.ForeignKey(Champion, on_delete=models.CASCADE, to_field="championId")
#     wins = models.IntegerField()
#     losses = models.IntegerField()
#     season = models.ForeignKey(Season, on_delete=models.CASCADE)
#     patch = models.ForeignKey(Patch, on_delete=models.CASCADE, to_field="full_version")
#     platform = models.ForeignKey(Platform, on_delete=models.CASCADE, db_column="platform", to_field="code")


# class BuiltSixthStat(models.Model):
#     legendary_item = models.ForeignKey(LegendaryItem, on_delete=models.CASCADE)
#     champion = models.ForeignKey(Champion, on_delete=models.CASCADE, to_field="championId")
#     wins = models.IntegerField()
#     losses = models.IntegerField()
#     season = models.ForeignKey(Season, on_delete=models.CASCADE)
#     patch = models.ForeignKey(Patch, on_delete=models.CASCADE, to_field="full_version")
#     platform = models.ForeignKey(Platform, on_delete=models.CASCADE, db_column="platform", to_field="code")


# class BuiltTierTwoBootStat(models.Model):
#     name = models.ForeignKey(TierTwoBoot, on_delete=models.CASCADE)
#     champion = models.ForeignKey(Champion, on_delete=models.CASCADE, to_field="championId")
#     wins = models.IntegerField()
#     losses = models.IntegerField()
#     season = models.ForeignKey(Season, on_delete=models.CASCADE)
#     patch = models.ForeignKey(Patch, on_delete=models.CASCADE, to_field="full_version")
#     platform = models.ForeignKey(Platform, on_delete=models.CASCADE, db_column="platform", to_field="code")






























