from django.db import models, connection
from django.core.exceptions import ValidationError


# Implementing PSQL declarative partitioning & PSQL composite keys in Django:
# 1) have a correct model
# 2) make migration
# 3) sql migrate
# 4) format/understand generated sql
# 5) delete migration
# 6) unmanage model
# 7) re-generate unmanged migration
# 8) migrations.RunSQL()
# 9) modify the raw SQL and test

# thought process:
# make sure the model that needs partitioning is unmanaged, give it a name that fits name convention
# then add raw runSQL() in the appropriate place in the migration

class RiotApiVersion(models.Model):
    asset = models.CharField(max_length=30, primary_key=True)
    version = models.CharField(max_length=30)

# Seeded
class Role(models.Model):
    role_options = [("TOP", "TOP"), ("JUNGLE", "JUNGLE"), ("MIDDLE", "MIDDLE"), ("BOTTOM", "BOTTOM"), ("UTILITY", "UTILITY")]
    name = models.CharField(choices=role_options, primary_key=True)


# Seeded
class Rank(models.Model): # Needs both types of indexes
    elo_options = [('Unranked', 'Unranked'), ('Iron 4', 'Iron 4'), ('Iron 3', 'Iron 3'), ('Iron 2', 'Iron 2'), ('Iron 1', 'Iron 1'), ('Bronze 4', 'Bronze 4'), ('Bronze 3', 'Bronze 3'), ('Bronze 2', 'Bronze 2'), ('Bronze 1', 'Bronze 1'), ('Silver 4', 'Silver 4'), ('Silver 3', 'Silver 3'), ('Silver 2', 'Silver 2'), ('Silver 1', 'Silver 1'), ('Gold 4', 'Gold 4'), ('Gold 3', 'Gold 3'), ('Gold 2', 'Gold 2'), ('Gold 1', 'Gold 1'), ('Platinum 4', 'Platinum 4'), ('Platinum 3', 'Platinum 3'), ('Platinum 2', 'Platinum 2'), ('Platinum 1', 'Platinum 1'), ('Emerald 4', 'Emerald 4'), ('Emerald 3', 'Emerald 3'), ('Emerald 2', 'Emerald 2'), ('Emerald 1', 'Emerald 1'), ('Diamond 4', 'Diamond 4'), ('Diamond 3', 'Diamond 3'), ('Diamond 2', 'Diamond 2'), ('Diamond 1', 'Diamond 1'), ('Master', 'Master'), ('Grandmaster', 'Grandmaster'), ('Challenger', 'Challenger')]
    elo = models.CharField(choices=elo_options, primary_key=True) # Game level stats to display in client


# Seeded
class Season(models.Model):    
    season = models.IntegerField()
    split = models.IntegerField()


# Seeded
class Patch(models.Model):
    full_version = models.CharField(max_length=25, primary_key=True)
    version = models.CharField(max_length=6)
    season_id = models.ForeignKey(Season, db_column="season_id",on_delete=models.CASCADE)


# Seeded
class Region(models.Model):
    name_optons = [("americas", "americas"), ("asia", "asia"), ("europe", "europe"), ("sea", "sea"), ("esports", "esports")]
    name = models.CharField(choices=name_optons, primary_key=True)


# Seeded
class Platform(models.Model):
    code_options = [("na1","na1"), ("euw1","euw1"), ("br1","br1")]
    code = models.CharField(choices=code_options, primary_key=True)   
    region = models.ForeignKey(Region, on_delete=models.CASCADE, db_column="region")

    def __str__(self):
        return f"Platform: '{self.code}', of type: {type(self)}"

# Seeded
class GameMode(models.Model):
    queueId = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=45, null=True, blank=True)


# Seeded
class Champion(models.Model):
    championId = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=30, null=True, blank=True)
    metadata = models.JSONField(default=dict, null=True, blank=True)


# Seeded
class SummonerSpell(models.Model):
    spellId = models.IntegerField(primary_key=True, db_column="spellId")
    name = models.CharField(max_length=40, blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True, null=True)

# Seeded
class Keystone(models.Model):
    keystone_id = models.IntegerField(primary_key=True, db_column="keystone_id") # maps to the first perk in the style match v5 JSON
    name = models.CharField(max_length=40, blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True, null=True)


# Seeded
class PrimaryPerkOne(models.Model):
    perk_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=40, blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True, null=True)

    
# Seeded
class PrimaryPerkTwo(models.Model):
    perk_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=40, blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True, null=True)


# Seeded
class PrimaryPerkThree(models.Model):
    perk_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=40, blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True, null=True)


# Seeded
class SecondaryPerkOne(models.Model):
    perk_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=40, blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True, null=True)



# Seeded
class SecondaryPerkTwo(models.Model):
    perk_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=40, blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True, null=True)


# Seeded
class StatShardOne(models.Model):
    shard_id = models.IntegerField(primary_key=True, db_column="shard_id")
    name = models.CharField(max_length=40, blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True, null=True)


# Seeded
class StatShardTwo(models.Model):
    shard_id = models.IntegerField(primary_key=True, db_column="shard_id")
    name = models.CharField(max_length=40, blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True, null=True)


# Seeded
class StatShardThree(models.Model):
    shard_id = models.IntegerField(primary_key=True, db_column="shard_id")
    name = models.CharField(max_length=40, blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True, null=True)


# Seeded
class Item(models.Model):
    itemId = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=120, null=True, blank=True)
    metadata = models.JSONField(default=dict, null=True, blank=True)


# Seeded
class CompletedBoot(models.Model):
    itemId = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=40, blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True, null=True)

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

    def custom_update(self, **kwargs):
        for field, value in kwargs.items():
            setattr(self, field, value)
        self.save()
    
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
    puuid = models.ForeignKey(Summoner, on_delete=models.CASCADE, related_name="summoner_overviews")
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, db_column="platform", to_field="code")
    season_id = models.ForeignKey(Season, db_column="season_id", on_delete=models.CASCADE, related_name="summoner_overviews")
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        try:
            return f"{self.metadata[0]['tier']}"
        except KeyError:
            return f"UNRANKED"
    
    class Meta:
        unique_together = ["season_id", "puuid", "platform"]
        db_table = "wrs_api_summoneroverview"
        managed = False


class Match(models.Model):
    matchId = models.CharField(max_length=20)
    elo = models.ForeignKey(Rank, on_delete=models.CASCADE, db_column="elo", to_field="elo")
    queueId = models.ForeignKey(GameMode, on_delete=models.CASCADE, db_column="queueId")
    season_id = models.ForeignKey(Season, db_column="season_id", on_delete=models.CASCADE, related_name="matches")
    patch = models.ForeignKey(Patch, on_delete=models.CASCADE, related_name="matches", to_field="full_version", db_column="patch")
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, db_column="platform", to_field="code")
    metadata = models.JSONField(default=dict)

    class Meta:
        unique_together = ["matchId", "season_id", "platform"]
        db_table = "wrs_api_match"
        managed = False


class SummonerMatch(models.Model):
    matchId = models.ForeignKey(Match, on_delete=models.CASCADE, db_column="matchId")
    elo = models.ForeignKey(Rank, on_delete=models.CASCADE, db_column="elo", to_field="elo")
    queueId = models.ForeignKey(GameMode, on_delete=models.CASCADE, db_column="queueId")
    puuid = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="summoners", db_column="puuid")
    season_id = models.ForeignKey(Season, db_column="season_id", on_delete=models.CASCADE, related_name="match_summoners")
    patch = models.ForeignKey(Patch, on_delete=models.CASCADE, related_name="match_summoners", to_field="full_version", db_column="patch")
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, db_column="platform", to_field="code")

    class Meta:
        unique_together = ["matchId", "puuid"]
        db_table = "wrs_api_summonermatch"
        managed = False
    

class ChampionStat(models.Model):    
    championId = models.ForeignKey(Champion, on_delete=models.CASCADE, to_field="championId", db_column="championId")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, db_column="role", to_field="name")
    elo = models.ForeignKey(Rank, on_delete=models.CASCADE, db_column="elo", to_field="elo")
    wins = models.IntegerField()
    losses = models.IntegerField()
    picked = models.IntegerField()
    season_id = models.ForeignKey(Season, on_delete=models.CASCADE)
    patch = models.ForeignKey(Patch, on_delete=models.CASCADE, to_field="full_version", db_column="patch")
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, db_column="platform", to_field="code")

    class Meta:
        unique_together = ["championId", "role", "elo", "platform", "patch", "season_id"]
        db_table = "wrs_api_championstat"
        managed = False


class BanStat(models.Model):    
    championId = models.ForeignKey(Champion, on_delete=models.CASCADE, to_field="championId", db_column="championId")
    elo = models.ForeignKey(Rank, on_delete=models.CASCADE, db_column="elo", to_field="elo")
    banned = models.IntegerField()
    season_id = models.ForeignKey(Season, on_delete=models.CASCADE)
    patch = models.ForeignKey(Patch, on_delete=models.CASCADE, to_field="full_version", db_column="patch")
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, db_column="platform", to_field="code")

    class Meta:
        unique_together = ["championId", "elo", "platform", "patch", "season_id"]
        db_table = "wrs_api_banstat"
        managed = False


class RunePageStat(models.Model):
    keystone = models.ForeignKey(Keystone, on_delete=models.CASCADE, db_column="keystone_id")
    primary_one = models.ForeignKey(PrimaryPerkOne, on_delete=models.CASCADE, db_column="primary_one")
    primary_two = models.ForeignKey(PrimaryPerkTwo, on_delete=models.CASCADE, db_column="primary_two")
    primary_three = models.ForeignKey(PrimaryPerkThree, on_delete=models.CASCADE, db_column="primary_three")
    secondary_one = models.ForeignKey(SecondaryPerkOne, on_delete=models.CASCADE, db_column="secondary_one")
    secondary_two = models.ForeignKey(SecondaryPerkTwo, on_delete=models.CASCADE, db_column="secondary_two")
    shard_one = models.ForeignKey(StatShardOne, on_delete=models.CASCADE, db_column="shard_one")
    shard_two = models.ForeignKey(StatShardTwo, on_delete=models.CASCADE, db_column="shard_two")
    shard_three = models.ForeignKey(StatShardThree, on_delete=models.CASCADE, db_column="shard_three")
    championId = models.ForeignKey(Champion, on_delete=models.CASCADE, to_field="championId", db_column="championId")
    elo = models.ForeignKey(Rank, on_delete=models.CASCADE, db_column="elo", to_field="elo")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, db_column="role", to_field="name")
    wins = models.IntegerField()
    losses = models.IntegerField()
    picked = models.IntegerField()
    season_id = models.ForeignKey(Season, on_delete=models.CASCADE, db_column="season_id")
    patch = models.ForeignKey(Patch, on_delete=models.CASCADE, to_field="full_version", db_column="patch")
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, db_column="platform", to_field="code")

    class Meta:
        unique_together = ["keystone", "primary_one", "primary_two", "primary_three", "secondary_one", "secondary_two", "shard_one", "shard_two", "shard_three", "championId", "platform", "patch", "role", "elo", "season_id"]
        db_table = "wrs_api_runepagestat"
        managed = False
    

class ItemBuildStat(models.Model):
    legendary_one = models.ForeignKey(Item, related_name="first_stat", on_delete=models.CASCADE, db_column="legendary_one")
    legendary_two = models.ForeignKey(Item, related_name="second_stat", on_delete=models.CASCADE, db_column="legendary_two", null = True)
    legendary_three = models.ForeignKey(Item, related_name="third_stat", on_delete=models.CASCADE, db_column="legendary_three", null = True)
    legendary_four = models.ForeignKey(Item, related_name="fourth_stat", on_delete=models.CASCADE, db_column="legendary_four", null = True)
    legendary_five = models.ForeignKey(Item, related_name="fifth_stat",on_delete=models.CASCADE, db_column="legendary_five", null = True)
    legendary_six = models.ForeignKey(Item, related_name="sixth_stat", on_delete=models.CASCADE, db_column="legendary_six", null = True)
    championId = models.ForeignKey(Champion, on_delete=models.CASCADE, to_field="championId", db_column="championId")
    elo = models.ForeignKey(Rank, on_delete=models.CASCADE, db_column="elo", to_field="elo")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, db_column="role", to_field="name")
    wins = models.IntegerField()
    losses = models.IntegerField()
    season_id = models.ForeignKey(Season, on_delete=models.CASCADE, db_column="season_id")
    patch = models.ForeignKey(Patch, on_delete=models.CASCADE, to_field="full_version", db_column="patch")
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, db_column="platform", to_field="code")

    class Meta:
        unique_together = ["legendary_one", "legendary_two", "legendary_three", "legendary_four", "legendary_five", "legendary_six", "championId", "platform", "patch", "role", "elo", "season_id"]
        db_table = "wrs_api_itembuildstat"
        managed = False


class CompletedBootStat(models.Model):
    completed_boot = models.ForeignKey(CompletedBoot, on_delete=models.CASCADE, db_column="completed_boot")
    championId = models.ForeignKey(Champion, on_delete=models.CASCADE, to_field="championId", db_column="championId")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, db_column="role", to_field="name")
    elo = models.ForeignKey(Rank, on_delete=models.CASCADE, db_column="elo", to_field="elo")
    wins = models.IntegerField()
    losses = models.IntegerField()
    season_id = models.ForeignKey(Season, on_delete=models.CASCADE, db_column="season_id")
    patch = models.ForeignKey(Patch, on_delete=models.CASCADE, to_field="full_version", db_column="patch")
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, db_column="platform", to_field="code")

    class Meta:
        unique_together = ["completed_boot", "role", "elo", "championId", "platform", "patch", "season_id"]
        db_table = "wrs_api_completedbootstat"
        managed = False


class SummonerSpellStat(models.Model):
    spell_one = models.ForeignKey(SummonerSpell, related_name="spell_one_stat", on_delete=models.CASCADE, db_column="spell_one")
    spell_two = models.ForeignKey(SummonerSpell, related_name="spell_two_stat", on_delete=models.CASCADE, db_column="spell_two")
    championId = models.ForeignKey(Champion, on_delete=models.CASCADE, to_field="championId", db_column="championId")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, db_column="role", to_field="name")
    elo = models.ForeignKey(Rank, on_delete=models.CASCADE, db_column="elo", to_field="elo")
    wins = models.IntegerField()
    losses = models.IntegerField()
    season_id = models.ForeignKey(Season, on_delete=models.CASCADE, db_column="season_id")
    patch = models.ForeignKey(Patch, on_delete=models.CASCADE, to_field="full_version", db_column="patch")
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, db_column="platform", to_field="code")

    class Meta:
        unique_together = ["spell_one", "spell_two", "role", "elo", "championId", "platform", "patch", "season_id"]
        db_table = "wrs_api_summonerspellstat"
        managed = False


class PersonalChampStat(models.Model):
    puuid = models.ForeignKey(Summoner, on_delete=models.CASCADE, db_column="puuid")
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, db_column="platform", to_field="code")
    queueId = models.ForeignKey(GameMode, on_delete=models.CASCADE, db_column="queueId")
    championId = models.ForeignKey(Champion, on_delete=models.CASCADE, to_field="championId", db_column="championId")
    games = models.IntegerField()
    season_id = models.ForeignKey(Season, on_delete=models.CASCADE, db_column="season_id")
    wins = models.IntegerField()
    losses = models.IntegerField() 
    kills = models.IntegerField()
    deaths = models.IntegerField()
    assists = models.IntegerField()
    cs = models.IntegerField()
    csm = models.FloatField()

    class Meta:
        unique_together = ["puuid", "platform", "championId", "season_id"]
        db_table = "wrs_api_personalchampstat"
        managed = False


class PreferredRole(models.Model):
    puuid = models.ForeignKey(Summoner, on_delete=models.CASCADE, db_column="puuid")
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, db_column="platform", to_field="code")
    season_id = models.ForeignKey(Season, on_delete=models.CASCADE, db_column="season_id")
    top = models.IntegerField()
    jungle = models.IntegerField()
    middle = models.IntegerField()
    bottom = models.IntegerField()
    support = models.IntegerField()

    class Meta:
        unique_together = ["puuid", "platform", "season_id"]
        db_table = "wrs_api_preferredrole"
        managed = False