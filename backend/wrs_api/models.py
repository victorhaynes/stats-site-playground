from django.db import models, connection
from django.core.exceptions import ValidationError
# from psqlextra.types import PostgresPartitioningMethod
# from psqlextra.models import PostgresPartitionedModel, PostgresModel


# FOR TESTING: look into composite index in PSQL code, may be necessary

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

# Seeded
class Role(models.Model):
    role_options = [("TOP", "TOP"), ("JUNGLE", "JUNGLE"), ("MIDDLE", "MIDDLE"), ("BOTTOM", "BOTTOM"), ("UTILITY", "UTILITY")]
    name = models.CharField(choices=role_options, primary_key=True)


# Seeded
class Rank(models.Model): # Needs both types of indexes
    elo_options = [('Unranked', 'Unranked'), ('Iron 4', 'Iron 4'), ('Iron 3', 'Iron 3'), ('Iron 2', 'Iron 2'), ('Iron 1', 'Iron 1'), ('Bronze 4', 'Bronze 4'), ('Bronze 3', 'Bronze 3'), ('Bronze 2', 'Bronze 2'), ('Bronze 1', 'Bronze 1'), ('Silver 4', 'Silver 4'), ('Silver 3', 'Silver 3'), ('Silver 2', 'Silver 2'), ('Silver 1', 'Silver 1'), ('Gold 4', 'Gold 4'), ('Gold 3', 'Gold 3'), ('Gold 2', 'Gold 2'), ('Gold 1', 'Gold 1'), ('Platinum 4', 'Platinum 4'), ('Platinum 3', 'Platinum 3'), ('Platinum 2', 'Platinum 2'), ('Platinum 1', 'Platinum 1'), ('Emerald 4', 'Emerald 4'), ('Emerald 3', 'Emerald 3'), ('Emerald 2', 'Emerald 2'), ('Emerald 1', 'Emerald 1'), ('Diamond 4', 'Diamond 4'), ('Diamond 3', 'Diamond 3'), ('Diamond 2', 'Diamond 2'), ('Diamond 1', 'Diamond 1'), ('Master', 'Master'), ('Grandmaster', 'Grandmaster'), ('Challenger', 'Challenger')]
    elo = models.CharField(choices=elo_options, primary_key=True) # Game level stats to display in client
    # tier_options = [('Unranked', 'Unranked'), ('Iron', 'Iron'), ('Bronze', 'Bronze'), ('Silver', 'Silver'), ('Gold', 'Gold'), ('Platinum', 'Platinum'), ('Emerald', 'Emerald'), ('Diamond', 'Diamond'), ('Master', 'Master'), ('Grandmaster', 'Grandmaster'), ('Challenger', 'Challenger')]
    # division_options = [(0,0),(1,1),(2,2), (3,3), (4,4)]
    # tier = models.CharField(choices=tier_options) # Global level stats for calculations and display
    # division = models.CharField(choices=division_options)


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
    
    # OC1 is SEA but can also be ASIA when SEA is not an option
    # def clean(self):
    #     super().clean()
    #     if (self.code == "na1" or self.code == "br1" or self.code == "la1" or self.code == "la2") and self.region != "americas":
    #         raise ValidationError(f"Platform: '${self.code}' must be associated with 'americas' region")
    #     elif (self.code == "jp1" or self.code == "kr1" or self.code == "oc1") and self.region != "asia":
    #         raise ValidationError(f"Platform: '${self.code}' must be associated with 'asia' region")
    #     elif (self.code == "oc1" or self.code == "ph2" or self.code == "sg2" or self.code == "th2" or self.code == "tw2" or self.code == "vn2") and self.region != "sea":
    #         raise ValidationError(f"Platform: '${self.code}' must be associated with 'asia' region")


# Seeded
class GameMode(models.Model):
    queueId = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=30)


# Seeded
class Champion(models.Model):
    championId = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=30)


# Seeded
class SummonerSpell(models.Model):
    spellId = models.IntegerField(primary_key=True, db_column="spellId")
    name = models.CharField(max_length=20)

# Seeded
class Keystone(models.Model):
    name_options = [
        ("Conqueror", "Conqueror"),
        ("Fleet Footwork", "Fleet Footwork"),
        ("Press the Attack", "Press the Attack"),
        ("Lethal Tempo", "Lethal Tempo"),
        ("Summon Aery", "Summon Aery"),
        ("Arcane Comet", "Arcane Comet"),
        ("Phase Rush", "Phase Rush"),
        ("Grasp of the Undying", "Grasp of the Undying"),
        ("Aftershock", "Aftershock"),
        ("Guardian", "Guardian"),
        ("Hail of Blades", "Hail of Blades"),
        ("Predator", "Predator"),
        ("Dark Harvest", "Dark Harvest"),
        ("Electrocute", "Electrocute"),
        ("Glacial Augment", "Glacial Augment"),
        ("First Strike", "First Strike"),
        ("Unsealed Spellbook", "Unsealed Spellbook")
    ]
    keystone_id = models.IntegerField(primary_key=True, db_column="keystone_id") # maps to the first perk in the style match v5 JSON
    name = models.CharField(choices=name_options)


# Seeded
class PrimaryPerkOne(models.Model):
    perk_one_options = [
        ('Overheal', 'Overheal'),
        ('Triumph', 'Triumph'),
        ('Presence of Mind', 'Presence of Mind'),
        ('Cheap Shot', 'Cheap Shot'),
        ('Taste of Blood', 'Taste of Blood'),
        ('Sudden Impact', 'Sudden Impact'),
        ('Nullifying Orb', 'Nullifying Orb'),
        ('Manaflow Band', 'Manaflow Band'),
        ('Nimbus Cloak', 'Nimbus Cloak'),
        ('Demolish', 'Demolish'),
        ('Font of Life', 'Font of Life'),
        ('Shield Bash', 'Shield Bash'),
        ('Hextech Flashtraption', 'Hextech Flashtraption'),
        ('Magical Footwear', 'Magical Footwear'),
        ('Triple Tonic', 'Triple Tonic')
    ]
    perk_id = models.IntegerField(primary_key=True)
    name = models.CharField(choices=perk_one_options)

    
# Seeded
class PrimaryPerkTwo(models.Model):
    perk_two_options = [
        ('Legend: Alacrity', 'Legend: Alacrity'),
        ('Legend: Tenacity', 'Legend: Tenacity'),
        ('Legend: Bloodline', 'Legend: Bloodline'),
        ('Zombie Ward', 'Zombie Ward'),
        ('Ghost Poro', 'Ghost Poro'),
        ('Eyeball Collection', 'Eyeball Collection'),
        ('Transcendence', 'Transcendence'),
        ('Celerity', 'Celerity'),
        ('Absolute Focus', 'Absolute Focus'),
        ('Conditioning', 'Conditioning'),
        ('Second Wind', 'Second Wind'),
        ('Bone Plating', 'Bone Plating'),
        ("Future's Market", "Future's Market"),
        ('Minion Dematerializer', 'Minion Dematerializer'),
        ('Biscuit Delivery', 'Biscuit Delivery')
    ]
    perk_id = models.IntegerField(primary_key=True)
    name = models.CharField(choices=perk_two_options)


# Seeded
class PrimaryPerkThree(models.Model):
    perk_three_options = [
        ('Coup de Grace', 'Coup de Grace'),
        ('Cut Down', 'Cut Down'),
        ('Last Stand', 'Last Stand'),
        ('Treasure Hunter', 'Treasure Hunter'),
        ('Ingenious Hunter', 'Ingenious Hunter'),
        ('Relentless Hunter', 'Relentless Hunter'),
        ('Ultimate Hunter', 'Ultimate Hunter'),
        ('Scorch', 'Scorch'),
        ('Waterwalking', 'Waterwalking'),
        ('Gathering Storm', 'Gathering Storm'),
        ('Overgrowth', 'Overgrowth'),
        ('Revitalize', 'Revitalize'),
        ('Unflinching', 'Unflinching'),
        ('Cosmic Insight', 'Cosmic Insight'),
        ('Approach Velocity', 'Approach Velocity'),
        ('Time Warp Tonic', 'Time Warp Tonic')
    ]
    perk_id = models.IntegerField(primary_key=True)
    name = models.CharField(choices=perk_three_options)


# Seeded
class SecondaryPerkOne(models.Model):
    secondary_options = [
        ('Overheal', 'Overheal'),
        ('Triumph', 'Triumph'),
        ('Presence of Mind', 'Presence of Mind'),
        ('Cheap Shot', 'Cheap Shot'),
        ('Taste of Blood', 'Taste of Blood'),
        ('Sudden Impact', 'Sudden Impact'),
        ('Nullifying Orb', 'Nullifying Orb'),
        ('Manaflow Band', 'Manaflow Band'),
        ('Nimbus Cloak', 'Nimbus Cloak'),
        ('Demolish', 'Demolish'),
        ('Font of Life', 'Font of Life'),
        ('Shield Bash', 'Shield Bash'),
        ('Hextech Flashtraption', 'Hextech Flashtraption'),
        ('Magical Footwear', 'Magical Footwear'),
        ('Triple Tonic', 'Triple Tonic'),
        ('Legend: Alacrity', 'Legend: Alacrity'),
        ('Legend: Tenacity', 'Legend: Tenacity'),
        ('Legend: Bloodline', 'Legend: Bloodline'),
        ('Zombie Ward', 'Zombie Ward'),
        ('Ghost Poro', 'Ghost Poro'),
        ('Eyeball Collection', 'Eyeball Collection'),
        ('Transcendence', 'Transcendence'),
        ('Celerity', 'Celerity'),
        ('Absolute Focus', 'Absolute Focus'),
        ('Conditioning', 'Conditioning'),
        ('Second Wind', 'Second Wind'),
        ('Bone Plating', 'Bone Plating'),
        ("Future's Market", "Future's Market"),
        ('Minion Dematerializer', 'Minion Dematerializer'),
        ('Biscuit Delivery', 'Biscuit Delivery'),
        ('Coup de Grace', 'Coup de Grace'),
        ('Cut Down', 'Cut Down'),
        ('Last Stand', 'Last Stand'),
        ('Treasure Hunter', 'Treasure Hunter'),
        ('Ingenious Hunter', 'Ingenious Hunter'),
        ('Relentless Hunter', 'Relentless Hunter'),
        ('Ultimate Hunter', 'Ultimate Hunter'),
        ('Scorch', 'Scorch'),
        ('Waterwalking', 'Waterwalking'),
        ('Gathering Storm', 'Gathering Storm'),
        ('Overgrowth', 'Overgrowth'),
        ('Revitalize', 'Revitalize'),
        ('Unflinching', 'Unflinching'),
        ('Cosmic Insight', 'Cosmic Insight'),
        ('Approach Velocity', 'Approach Velocity'),
        ('Time Warp Tonic', 'Time Warp Tonic')
    ]
    perk_id = models.IntegerField(primary_key=True)
    name = models.CharField(choices=secondary_options)
    


# Seeded
class SecondaryPerkTwo(models.Model):
    secondary_options = [
        ('Overheal', 'Overheal'),
        ('Triumph', 'Triumph'),
        ('Presence of Mind', 'Presence of Mind'),
        ('Cheap Shot', 'Cheap Shot'),
        ('Taste of Blood', 'Taste of Blood'),
        ('Sudden Impact', 'Sudden Impact'),
        ('Nullifying Orb', 'Nullifying Orb'),
        ('Manaflow Band', 'Manaflow Band'),
        ('Nimbus Cloak', 'Nimbus Cloak'),
        ('Demolish', 'Demolish'),
        ('Font of Life', 'Font of Life'),
        ('Shield Bash', 'Shield Bash'),
        ('Hextech Flashtraption', 'Hextech Flashtraption'),
        ('Magical Footwear', 'Magical Footwear'),
        ('Triple Tonic', 'Triple Tonic'),
        ('Legend: Alacrity', 'Legend: Alacrity'),
        ('Legend: Tenacity', 'Legend: Tenacity'),
        ('Legend: Bloodline', 'Legend: Bloodline'),
        ('Zombie Ward', 'Zombie Ward'),
        ('Ghost Poro', 'Ghost Poro'),
        ('Eyeball Collection', 'Eyeball Collection'),
        ('Transcendence', 'Transcendence'),
        ('Celerity', 'Celerity'),
        ('Absolute Focus', 'Absolute Focus'),
        ('Conditioning', 'Conditioning'),
        ('Second Wind', 'Second Wind'),
        ('Bone Plating', 'Bone Plating'),
        ("Future's Market", "Future's Market"),
        ('Minion Dematerializer', 'Minion Dematerializer'),
        ('Biscuit Delivery', 'Biscuit Delivery'),
        ('Coup de Grace', 'Coup de Grace'),
        ('Cut Down', 'Cut Down'),
        ('Last Stand', 'Last Stand'),
        ('Treasure Hunter', 'Treasure Hunter'),
        ('Ingenious Hunter', 'Ingenious Hunter'),
        ('Relentless Hunter', 'Relentless Hunter'),
        ('Ultimate Hunter', 'Ultimate Hunter'),
        ('Scorch', 'Scorch'),
        ('Waterwalking', 'Waterwalking'),
        ('Gathering Storm', 'Gathering Storm'),
        ('Overgrowth', 'Overgrowth'),
        ('Revitalize', 'Revitalize'),
        ('Unflinching', 'Unflinching'),
        ('Cosmic Insight', 'Cosmic Insight'),
        ('Approach Velocity', 'Approach Velocity'),
        ('Time Warp Tonic', 'Time Warp Tonic')
    ]
    perk_id = models.IntegerField(primary_key=True)
    name = models.CharField(choices=secondary_options)
    

# Seeded
class StatShardOne(models.Model):
    shard_one_options = [
        ("Adaptive Force", "Adaptive Force"),
        ('Attack Speed', 'Attack Speed'),
        ('Ability Haste', 'Ability Haste')
    ]
    shard_id = models.IntegerField(primary_key=True, db_column="shard_id")
    name = models.CharField(choices=shard_one_options)


# Seeded
class StatShardTwo(models.Model):
    shard_two_options = [
        ("Adaptive Force", "Adaptive Force"),
        ('Move Speed', 'Move Speed'),
        ('Health Scaling', 'Health Scaling')
    ]
    shard_id = models.IntegerField(primary_key=True, db_column="shard_id")
    name = models.CharField(choices=shard_two_options)


# Seeded
class StatShardThree(models.Model):
    shard_three_options = [
        ("Health", "Health"),
        ('Tenacity And Slow Resist', 'Tenacity And Slow Resist'),
        ('Health Scaling', 'Health Scaling')
    ]
    shard_id = models.IntegerField(primary_key=True, db_column="shard_id")
    name = models.CharField(choices=shard_three_options)


# Seeded
class LegendaryItem(models.Model):
    itemId = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=30)

# Seeded
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


# Match is partitioned and Summoner is partitioned, in order to join Summoner on SummonerMatch and only select relevant fields we need season & patch present in this join table
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
    
    # TO DO: Run migration, make sure it works, alter migration/tables to consider summoner spell, finish rune page model, write rune page seeds, and role
    # Make sure that related models are updated/ERD is correct in concept for runepage also, 
    # update write logic to make sure that elo and runes are being captured, then work on builtstats and boot stats and leaderbaord

    # valdiate with rune page building logic per the lol client
        
    # Currently, new model role, elo/rank, runepagestat, keystone, primary/secondary, seed file done. Need to factor role into the appropriate stat models,
    # update table/psql, check idnexes, update match v5 writing function so elo is included. 


# Make sure that when writing a stat we are checking that there is at least one legendary item, if there isn't do not write a  build stat
class ItemBuildStat(models.Model):
    legendary_one = models.ForeignKey(LegendaryItem, related_name="first_stat", on_delete=models.CASCADE, db_column="legendary_one")
    legendary_two = models.ForeignKey(LegendaryItem, related_name="second_stat", on_delete=models.CASCADE, db_column="legendary_two", null = True)
    legendary_three = models.ForeignKey(LegendaryItem, related_name="third_stat", on_delete=models.CASCADE, db_column="legendary_three", null = True)
    legendary_four = models.ForeignKey(LegendaryItem, related_name="fourth_stat", on_delete=models.CASCADE, db_column="legendary_four", null = True)
    legendary_five = models.ForeignKey(LegendaryItem, related_name="fifth_stat",on_delete=models.CASCADE, db_column="legendary_five", null = True)
    legendary_six = models.ForeignKey(LegendaryItem, related_name="sixth_stat", on_delete=models.CASCADE, db_column="legendary_six", null = True)
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


class TierTwoBootStat(models.Model):
    tier_two_boot = models.ForeignKey(TierTwoBoot, on_delete=models.CASCADE, db_column="tier_two_boot")
    championId = models.ForeignKey(Champion, on_delete=models.CASCADE, to_field="championId", db_column="championId")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, db_column="role", to_field="name")
    elo = models.ForeignKey(Rank, on_delete=models.CASCADE, db_column="elo", to_field="elo")
    wins = models.IntegerField()
    losses = models.IntegerField()
    season_id = models.ForeignKey(Season, on_delete=models.CASCADE, db_column="season_id")
    patch = models.ForeignKey(Patch, on_delete=models.CASCADE, to_field="full_version", db_column="patch")
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, db_column="platform", to_field="code")

    class Meta:
        unique_together = ["tier_two_boot", "role", "elo", "championId", "platform", "patch", "season_id"]
        db_table = "wrs_api_tiertwobootstat"
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


# class BuiltTierTwoBootStat(models.Model):
#     tier_two_boot = models.ForeignKey(LegendaryItem, on_delete=models.CASCADE, db_column="tier_two_boot")
#     championId = models.ForeignKey(Champion, on_delete=models.CASCADE, to_field="championId", db_column="championId")
#     role = models.ForeignKey(Role, on_delete=models.CASCADE, db_column="role", to_field="name")
#     elo = models.ForeignKey(Rank, on_delete=models.CASCADE, db_column="elo", to_field="elo")
#     wins = models.IntegerField()
#     losses = models.IntegerField()
#     season_id = models.ForeignKey(Season, on_delete=models.CASCADE, db_column="season_id")
#     patch = models.ForeignKey(Patch, on_delete=models.CASCADE, to_field="full_version", db_column="patch")
#     platform = models.ForeignKey(Platform, on_delete=models.CASCADE, db_column="platform", to_field="code")

#     class Meta:
#         unique_together = ["tier_two_boot", "role", "elo", "championId", "platform", "patch"]
#         db_table = "wrs_api_builttiertwobootstat"
#         managed = False


# class BuiltFirstStat(models.Model):
#     legendary_item = models.ForeignKey(LegendaryItem, on_delete=models.CASCADE, db_column="legendary_item")
#     championId = models.ForeignKey(Champion, on_delete=models.CASCADE, to_field="championId", db_column="championId")
#     role = models.ForeignKey(Role, on_delete=models.CASCADE, db_column="role", to_field="name")
#     elo = models.ForeignKey(Rank, on_delete=models.CASCADE, db_column="elo", to_field="elo")
#     wins = models.IntegerField()
#     losses = models.IntegerField()
#     season_id = models.ForeignKey(Season, on_delete=models.CASCADE, db_column="season_id")
#     patch = models.ForeignKey(Patch, on_delete=models.CASCADE, to_field="full_version", db_column="patch")
#     platform = models.ForeignKey(Platform, on_delete=models.CASCADE, db_column="platform", to_field="code")

#     class Meta:
#         unique_together = ["legendary_item", "role", "elo" "championId", "platform", "patch"]
#         db_table = "wrs_api_builtfirststat"
#         managed = False


# class BuiltSecondStat(models.Model):
#     legendary_item = models.ForeignKey(LegendaryItem, on_delete=models.CASCADE, db_column="legendary_item")
#     championId = models.ForeignKey(Champion, on_delete=models.CASCADE, to_field="championId", db_column="championId")
#     role = models.ForeignKey(Role, on_delete=models.CASCADE, db_column="role", to_field="name")
#     elo = models.ForeignKey(Rank, on_delete=models.CASCADE, db_column="elo", to_field="elo")
#     wins = models.IntegerField()
#     losses = models.IntegerField()
#     season_id = models.ForeignKey(Season, on_delete=models.CASCADE, db_column="season_id")
#     patch = models.ForeignKey(Patch, on_delete=models.CASCADE, to_field="full_version", db_column="patch")
#     platform = models.ForeignKey(Platform, on_delete=models.CASCADE, db_column="platform", to_field="code")

#     class Meta:
#         unique_together = ["legendary_item", "role", "elo" "championId", "platform", "patch"]
#         db_table = "wrs_api_builtsecondstat"
#         managed = False


# class BuiltThirdStat(models.Model):
#     legendary_item = models.ForeignKey(LegendaryItem, on_delete=models.CASCADE, db_column="legendary_item")
#     championId = models.ForeignKey(Champion, on_delete=models.CASCADE, to_field="championId", db_column="championId")
#     role = models.ForeignKey(Role, on_delete=models.CASCADE, db_column="role", to_field="name")
#     elo = models.ForeignKey(Rank, on_delete=models.CASCADE, db_column="elo", to_field="elo")
#     wins = models.IntegerField()
#     losses = models.IntegerField()
#     season_id = models.ForeignKey(Season, on_delete=models.CASCADE, db_column="season_id")
#     patch = models.ForeignKey(Patch, on_delete=models.CASCADE, to_field="full_version", db_column="patch")
#     platform = models.ForeignKey(Platform, on_delete=models.CASCADE, db_column="platform", to_field="code")

#     class Meta:
#         unique_together = ["legendary_item", "role", "elo" "championId", "platform", "patch"]
#         db_table = "wrs_api_builtthirdstat"
#         managed = False


# class BuiltFourthStat(models.Model):
#     legendary_item = models.ForeignKey(LegendaryItem, on_delete=models.CASCADE, db_column="legendary_item")
#     championId = models.ForeignKey(Champion, on_delete=models.CASCADE, to_field="championId", db_column="championId")
#     role = models.ForeignKey(Role, on_delete=models.CASCADE, db_column="role", to_field="name")
#     elo = models.ForeignKey(Rank, on_delete=models.CASCADE, db_column="elo", to_field="elo")
#     wins = models.IntegerField()
#     losses = models.IntegerField()
#     season_id = models.ForeignKey(Season, on_delete=models.CASCADE, db_column="season_id")
#     patch = models.ForeignKey(Patch, on_delete=models.CASCADE, to_field="full_version", db_column="patch")
#     platform = models.ForeignKey(Platform, on_delete=models.CASCADE, db_column="platform", to_field="code")

#     class Meta:
#         unique_together = ["legendary_item", "role", "elo" "championId", "platform", "patch"]
#         db_table = "wrs_api_builtfourthstat"
#         managed = False


# class BuiltFifthStat(models.Model):
#     legendary_item = models.ForeignKey(LegendaryItem, on_delete=models.CASCADE, db_column="legendary_item")
#     championId = models.ForeignKey(Champion, on_delete=models.CASCADE, to_field="championId", db_column="championId")
#     role = models.ForeignKey(Role, on_delete=models.CASCADE, db_column="role", to_field="name")
#     elo = models.ForeignKey(Rank, on_delete=models.CASCADE, db_column="elo", to_field="elo")
#     wins = models.IntegerField()
#     losses = models.IntegerField()
#     season_id = models.ForeignKey(Season, on_delete=models.CASCADE, db_column="season_id")
#     patch = models.ForeignKey(Patch, on_delete=models.CASCADE, to_field="full_version", db_column="patch")
#     platform = models.ForeignKey(Platform, on_delete=models.CASCADE, db_column="platform", to_field="code")

#     class Meta:
#         unique_together = ["legendary_item", "role", "elo" "championId", "platform", "patch"]
#         db_table = "wrs_api_builtfifthstat"
#         managed = False


# class BuiltSixthStat(models.Model):
#     legendary_item = models.ForeignKey(LegendaryItem, on_delete=models.CASCADE, db_column="legendary_item")
#     championId = models.ForeignKey(Champion, on_delete=models.CASCADE, to_field="championId", db_column="championId")
#     role = models.ForeignKey(Role, on_delete=models.CASCADE, db_column="role", to_field="name")
#     elo = models.ForeignKey(Rank, on_delete=models.CASCADE, db_column="elo", to_field="elo")
#     wins = models.IntegerField()
#     losses = models.IntegerField()
#     season_id = models.ForeignKey(Season, on_delete=models.CASCADE, db_column="season_id")
#     patch = models.ForeignKey(Patch, on_delete=models.CASCADE, to_field="full_version", db_column="patch")
#     platform = models.ForeignKey(Platform, on_delete=models.CASCADE, db_column="platform", to_field="code")

#     class Meta:
#         unique_together = ["legendary_item", "role", "elo" "championId", "platform", "patch"]
#         db_table = "wrs_api_builtsixthstat"
#         managed = False













#################### MOST RECENT MIGRATIONS ####################
#################### MOST RECENT MIGRATIONS ####################
#################### MOST RECENT MIGRATIONS ####################
#################### MOST RECENT MIGRATIONS ####################
#################### MOST RECENT MIGRATIONS ####################
#################### MOST RECENT MIGRATIONS ####################
#################### MOST RECENT MIGRATIONS ####################
#################### MOST RECENT MIGRATIONS ####################
#################### MOST RECENT MIGRATIONS ####################
#################### MOST RECENT MIGRATIONS ####################
#################### MOST RECENT MIGRATIONS ####################
#################### MOST RECENT MIGRATIONS ####################
#################### MOST RECENT MIGRATIONS ####################
#################### MOST RECENT MIGRATIONS ####################
#################### MOST RECENT MIGRATIONS ####################
#################### MOST RECENT MIGRATIONS ####################
#################### MOST RECENT MIGRATIONS ####################
#################### MOST RECENT MIGRATIONS ####################
#################### MOST RECENT MIGRATIONS ####################
#################### MOST RECENT MIGRATIONS ####################



# # Generated by Django 4.2.7 on 2024-05-01 18:13

# from django.db import migrations, models
# import django.db.models.deletion


# class Migration(migrations.Migration):

#     initial = True

#     dependencies = [
#     ]

#     operations = [
#         migrations.CreateModel(
#             name='BanStat',
#             fields=[
#                 ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
#                 ('banned', models.IntegerField()),
#             ],
#             options={
#                 'db_table': 'wrs_api_banstat',
#                 'managed': False,
#             },
#         ),
#         migrations.CreateModel(
#             name='ChampionStat',
#             fields=[
#                 ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
#                 ('wins', models.IntegerField()),
#                 ('losses', models.IntegerField()),
#                 ('picked', models.IntegerField()),
#                 ('banned', models.IntegerField()),
#             ],
#             options={
#                 'db_table': 'wrs_api_championstat',
#                 'managed': False,
#             },
#         ),
#         migrations.CreateModel(
#             name='ItemBuildStat',
#             fields=[
#                 ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
#                 ('wins', models.IntegerField()),
#                 ('losses', models.IntegerField()),
#             ],
#             options={
#                 'db_table': 'wrs_api_itembuildstat',
#                 'managed': False,
#             },
#         ),
#         migrations.CreateModel(
#             name='Match',
#             fields=[
#                 ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
#                 ('matchId', models.CharField(max_length=20)),
#                 ('metadata', models.JSONField(default=dict)),
#             ],
#             options={
#                 'db_table': 'wrs_api_match',
#                 'managed': False,
#             },
#         ),
#         migrations.CreateModel(
#             name='RunePageStat',
#             fields=[
#                 ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
#                 ('wins', models.IntegerField()),
#                 ('losses', models.IntegerField()),
#                 ('picked', models.IntegerField()),
#             ],
#             options={
#                 'db_table': 'wrs_api_runepagestat',
#                 'managed': False,
#             },
#         ),
#         migrations.CreateModel(
#             name='Summoner',
#             fields=[
#                 ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
#                 ('puuid', models.CharField(max_length=100)),
#                 ('gameName', models.CharField(max_length=50)),
#                 ('tagLine', models.CharField(max_length=10)),
#                 ('profileIconId', models.IntegerField()),
#                 ('encryptedSummonerId', models.CharField(max_length=100)),
#                 ('most_recent_game', models.CharField(max_length=25, null=True)),
#                 ('created_at', models.DateTimeField(auto_now_add=True)),
#                 ('updated_at', models.DateTimeField(auto_now=True)),
#             ],
#             options={
#                 'db_table': 'wrs_api_summoner',
#                 'managed': False,
#             },
#         ),
#         migrations.CreateModel(
#             name='SummonerMatch',
#             fields=[
#                 ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
#             ],
#             options={
#                 'db_table': 'wrs_api_summonermatch',
#                 'managed': False,
#             },
#         ),
#         migrations.CreateModel(
#             name='SummonerOverview',
#             fields=[
#                 ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
#                 ('metadata', models.JSONField(default=dict)),
#                 ('created_at', models.DateTimeField(auto_now_add=True)),
#                 ('updated_at', models.DateTimeField(auto_now=True)),
#             ],
#             options={
#                 'db_table': 'wrs_api_summoneroverview',
#                 'managed': False,
#             },
#         ),
#         migrations.CreateModel(
#             name='SummonerSpellStat',
#             fields=[
#                 ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
#                 ('wins', models.IntegerField()),
#                 ('losses', models.IntegerField()),
#             ],
#             options={
#                 'db_table': 'wrs_api_summonerspellstat',
#                 'managed': False,
#             },
#         ),
#         migrations.CreateModel(
#             name='TierTwoBootStat',
#             fields=[
#                 ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
#                 ('wins', models.IntegerField()),
#                 ('losses', models.IntegerField()),
#             ],
#             options={
#                 'db_table': 'wrs_api_tiertwobootstat',
#                 'managed': False,
#             },
#         ),
#         migrations.CreateModel(
#             name='Champion',
#             fields=[
#                 ('championId', models.IntegerField(primary_key=True, serialize=False)),
#                 ('name', models.CharField(max_length=30)),
#             ],
#         ),
#         migrations.CreateModel(
#             name='GameMode',
#             fields=[
#                 ('queueId', models.IntegerField(primary_key=True, serialize=False)),
#                 ('name', models.CharField(max_length=30)),
#             ],
#         ),
#         migrations.CreateModel(
#             name='Keystone',
#             fields=[
#                 ('keystone_id', models.IntegerField(db_column='keystone_id', primary_key=True, serialize=False)),
#                 ('name', models.CharField(choices=[('Conqueror', 'Conqueror'), ('Fleet Footwork', 'Fleet Footwork'), ('Press the Attack', 'Press the Attack'), ('Lethal Tempo', 'Lethal Tempo'), ('Summon Aery', 'Summon Aery'), ('Arcane Comet', 'Arcane Comet'), ('Phase Rush', 'Phase Rush'), ('Grasp of the Undying', 'Grasp of the Undying'), ('Aftershock', 'Aftershock'), ('Guardian', 'Guardian'), ('Hail of Blades', 'Hail of Blades'), ('Predator', 'Predator'), ('Dark Harvest', 'Dark Harvest'), ('Electrocute', 'Electrocute'), ('Glacial Augment', 'Glacial Augment'), ('First Strike', 'First Strike'), ('Unsealed Spellbook', 'Unsealed Spellbook')])),
#             ],
#         ),
#         migrations.CreateModel(
#             name='LegendaryItem',
#             fields=[
#                 ('itemId', models.IntegerField(primary_key=True, serialize=False)),
#                 ('name', models.CharField(max_length=30)),
#             ],
#         ),
#         migrations.CreateModel(
#             name='PrimaryPerkOne',
#             fields=[
#                 ('perk_id', models.IntegerField(primary_key=True, serialize=False)),
#                 ('name', models.CharField(choices=[('Overheal', 'Overheal'), ('Triumph', 'Triumph'), ('Presence of Mind', 'Presence of Mind'), ('Cheap Shot', 'Cheap Shot'), ('Taste of Blood', 'Taste of Blood'), ('Sudden Impact', 'Sudden Impact'), ('Nullifying Orb', 'Nullifying Orb'), ('Manaflow Band', 'Manaflow Band'), ('Nimbus Cloak', 'Nimbus Cloak'), ('Demolish', 'Demolish'), ('Font of Life', 'Font of Life'), ('Shield Bash', 'Shield Bash'), ('Hextech Flashtraption', 'Hextech Flashtraption'), ('Magical Footwear', 'Magical Footwear'), ('Triple Tonic', 'Triple Tonic')])),
#             ],
#         ),
#         migrations.CreateModel(
#             name='PrimaryPerkThree',
#             fields=[
#                 ('perk_id', models.IntegerField(primary_key=True, serialize=False)),
#                 ('name', models.CharField(choices=[('Coup de Grace', 'Coup de Grace'), ('Cut Down', 'Cut Down'), ('Last Stand', 'Last Stand'), ('Treasure Hunter', 'Treasure Hunter'), ('Ingenious Hunter', 'Ingenious Hunter'), ('Relentless Hunter', 'Relentless Hunter'), ('Ultimate Hunter', 'Ultimate Hunter'), ('Scorch', 'Scorch'), ('Waterwalking', 'Waterwalking'), ('Gathering Storm', 'Gathering Storm'), ('Overgrowth', 'Overgrowth'), ('Revitalize', 'Revitalize'), ('Unflinching', 'Unflinching'), ('Cosmic Insight', 'Cosmic Insight'), ('Approach Velocity', 'Approach Velocity'), ('Time Warp Tonic', 'Time Warp Tonic')])),
#             ],
#         ),
#         migrations.CreateModel(
#             name='PrimaryPerkTwo',
#             fields=[
#                 ('perk_id', models.IntegerField(primary_key=True, serialize=False)),
#                 ('name', models.CharField(choices=[('Legend: Alacrity', 'Legend: Alacrity'), ('Legend: Tenacity', 'Legend: Tenacity'), ('Legend: Bloodline', 'Legend: Bloodline'), ('Zombie Ward', 'Zombie Ward'), ('Ghost Poro', 'Ghost Poro'), ('Eyeball Collection', 'Eyeball Collection'), ('Transcendence', 'Transcendence'), ('Celerity', 'Celerity'), ('Absolute Focus', 'Absolute Focus'), ('Conditioning', 'Conditioning'), ('Second Wind', 'Second Wind'), ('Bone Plating', 'Bone Plating'), ("Future's Market", "Future's Market"), ('Minion Dematerializer', 'Minion Dematerializer'), ('Biscuit Delivery', 'Biscuit Delivery')])),
#             ],
#         ),
#         migrations.CreateModel(
#             name='Rank',
#             fields=[
#                 ('elo', models.CharField(choices=[('Unranked', 'Unranked'), ('Iron 4', 'Iron 4'), ('Iron 3', 'Iron 3'), ('Iron 2', 'Iron 2'), ('Iron 1', 'Iron 1'), ('Bronze 4', 'Bronze 4'), ('Bronze 3', 'Bronze 3'), ('Bronze 2', 'Bronze 2'), ('Bronze 1', 'Bronze 1'), ('Silver 4', 'Silver 4'), ('Silver 3', 'Silver 3'), ('Silver 2', 'Silver 2'), ('Silver 1', 'Silver 1'), ('Gold 4', 'Gold 4'), ('Gold 3', 'Gold 3'), ('Gold 2', 'Gold 2'), ('Gold 1', 'Gold 1'), ('Platinum 4', 'Platinum 4'), ('Platinum 3', 'Platinum 3'), ('Platinum 2', 'Platinum 2'), ('Platinum 1', 'Platinum 1'), ('Emerald 4', 'Emerald 4'), ('Emerald 3', 'Emerald 3'), ('Emerald 2', 'Emerald 2'), ('Emerald 1', 'Emerald 1'), ('Diamond 4', 'Diamond 4'), ('Diamond 3', 'Diamond 3'), ('Diamond 2', 'Diamond 2'), ('Diamond 1', 'Diamond 1'), ('Master', 'Master'), ('Grandmaster', 'Grandmaster'), ('Challenger', 'Challenger')], primary_key=True, serialize=False)),
#             ],
#         ),
#         migrations.CreateModel(
#             name='Region',
#             fields=[
#                 ('name', models.CharField(choices=[('americas', 'americas'), ('asia', 'asia'), ('europe', 'europe'), ('sea', 'sea'), ('esports', 'esports')], primary_key=True, serialize=False)),
#             ],
#         ),
#         migrations.CreateModel(
#             name='Role',
#             fields=[
#                 ('name', models.CharField(choices=[('TOP', 'TOP'), ('JUNGLE', 'JUNGLE'), ('MIDDLE', 'MIDDLE'), ('BOTTOM', 'BOTTOM'), ('UTILITY', 'UTILITY')], primary_key=True, serialize=False)),
#             ],
#         ),
#         migrations.CreateModel(
#             name='Season',
#             fields=[
#                 ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
#                 ('season', models.IntegerField()),
#                 ('split', models.IntegerField()),
#             ],
#         ),
#         migrations.CreateModel(
#             name='SecondaryPerkOne',
#             fields=[
#                 ('perk_id', models.IntegerField(primary_key=True, serialize=False)),
#                 ('name', models.CharField(choices=[('Overheal', 'Overheal'), ('Triumph', 'Triumph'), ('Presence of Mind', 'Presence of Mind'), ('Cheap Shot', 'Cheap Shot'), ('Taste of Blood', 'Taste of Blood'), ('Sudden Impact', 'Sudden Impact'), ('Nullifying Orb', 'Nullifying Orb'), ('Manaflow Band', 'Manaflow Band'), ('Nimbus Cloak', 'Nimbus Cloak'), ('Demolish', 'Demolish'), ('Font of Life', 'Font of Life'), ('Shield Bash', 'Shield Bash'), ('Hextech Flashtraption', 'Hextech Flashtraption'), ('Magical Footwear', 'Magical Footwear'), ('Triple Tonic', 'Triple Tonic'), ('Legend: Alacrity', 'Legend: Alacrity'), ('Legend: Tenacity', 'Legend: Tenacity'), ('Legend: Bloodline', 'Legend: Bloodline'), ('Zombie Ward', 'Zombie Ward'), ('Ghost Poro', 'Ghost Poro'), ('Eyeball Collection', 'Eyeball Collection'), ('Transcendence', 'Transcendence'), ('Celerity', 'Celerity'), ('Absolute Focus', 'Absolute Focus'), ('Conditioning', 'Conditioning'), ('Second Wind', 'Second Wind'), ('Bone Plating', 'Bone Plating'), ("Future's Market", "Future's Market"), ('Minion Dematerializer', 'Minion Dematerializer'), ('Biscuit Delivery', 'Biscuit Delivery'), ('Coup de Grace', 'Coup de Grace'), ('Cut Down', 'Cut Down'), ('Last Stand', 'Last Stand'), ('Treasure Hunter', 'Treasure Hunter'), ('Ingenious Hunter', 'Ingenious Hunter'), ('Relentless Hunter', 'Relentless Hunter'), ('Ultimate Hunter', 'Ultimate Hunter'), ('Scorch', 'Scorch'), ('Waterwalking', 'Waterwalking'), ('Gathering Storm', 'Gathering Storm'), ('Overgrowth', 'Overgrowth'), ('Revitalize', 'Revitalize'), ('Unflinching', 'Unflinching'), ('Cosmic Insight', 'Cosmic Insight'), ('Approach Velocity', 'Approach Velocity'), ('Time Warp Tonic', 'Time Warp Tonic')])),
#             ],
#         ),
#         migrations.CreateModel(
#             name='SecondaryPerkTwo',
#             fields=[
#                 ('perk_id', models.IntegerField(primary_key=True, serialize=False)),
#                 ('name', models.CharField(choices=[('Overheal', 'Overheal'), ('Triumph', 'Triumph'), ('Presence of Mind', 'Presence of Mind'), ('Cheap Shot', 'Cheap Shot'), ('Taste of Blood', 'Taste of Blood'), ('Sudden Impact', 'Sudden Impact'), ('Nullifying Orb', 'Nullifying Orb'), ('Manaflow Band', 'Manaflow Band'), ('Nimbus Cloak', 'Nimbus Cloak'), ('Demolish', 'Demolish'), ('Font of Life', 'Font of Life'), ('Shield Bash', 'Shield Bash'), ('Hextech Flashtraption', 'Hextech Flashtraption'), ('Magical Footwear', 'Magical Footwear'), ('Triple Tonic', 'Triple Tonic'), ('Legend: Alacrity', 'Legend: Alacrity'), ('Legend: Tenacity', 'Legend: Tenacity'), ('Legend: Bloodline', 'Legend: Bloodline'), ('Zombie Ward', 'Zombie Ward'), ('Ghost Poro', 'Ghost Poro'), ('Eyeball Collection', 'Eyeball Collection'), ('Transcendence', 'Transcendence'), ('Celerity', 'Celerity'), ('Absolute Focus', 'Absolute Focus'), ('Conditioning', 'Conditioning'), ('Second Wind', 'Second Wind'), ('Bone Plating', 'Bone Plating'), ("Future's Market", "Future's Market"), ('Minion Dematerializer', 'Minion Dematerializer'), ('Biscuit Delivery', 'Biscuit Delivery'), ('Coup de Grace', 'Coup de Grace'), ('Cut Down', 'Cut Down'), ('Last Stand', 'Last Stand'), ('Treasure Hunter', 'Treasure Hunter'), ('Ingenious Hunter', 'Ingenious Hunter'), ('Relentless Hunter', 'Relentless Hunter'), ('Ultimate Hunter', 'Ultimate Hunter'), ('Scorch', 'Scorch'), ('Waterwalking', 'Waterwalking'), ('Gathering Storm', 'Gathering Storm'), ('Overgrowth', 'Overgrowth'), ('Revitalize', 'Revitalize'), ('Unflinching', 'Unflinching'), ('Cosmic Insight', 'Cosmic Insight'), ('Approach Velocity', 'Approach Velocity'), ('Time Warp Tonic', 'Time Warp Tonic')])),
#             ],
#         ),
#         migrations.CreateModel(
#             name='StatShardOne',
#             fields=[
#                 ('shard_id', models.IntegerField(db_column='shard_id', primary_key=True, serialize=False)),
#                 ('name', models.CharField(choices=[('Adaptive Force', 'Adaptive Force'), ('Attack Speed', 'Attack Speed'), ('Ability Haste', 'Ability Haste')])),
#             ],
#         ),
#         migrations.CreateModel(
#             name='StatShardThree',
#             fields=[
#                 ('shard_id', models.IntegerField(db_column='shard_id', primary_key=True, serialize=False)),
#                 ('name', models.CharField(choices=[('Health', 'Health'), ('Tenacity And Slow Resist', 'Tenacity And Slow Resist'), ('Health Scaling', 'Health Scaling')])),
#             ],
#         ),
#         migrations.CreateModel(
#             name='StatShardTwo',
#             fields=[
#                 ('shard_id', models.IntegerField(db_column='shard_id', primary_key=True, serialize=False)),
#                 ('name', models.CharField(choices=[('Adaptive Force', 'Adaptive Force'), ('Move Speed', 'Move Speed'), ('Health Scaling', 'Health Scaling')])),
#             ],
#         ),
#         migrations.CreateModel(
#             name='SummonerSpell',
#             fields=[
#                 ('spellId', models.IntegerField(db_column='spellId', primary_key=True, serialize=False)),
#                 ('name', models.CharField(max_length=20)),
#             ],
#         ),
#         migrations.CreateModel(
#             name='TierTwoBoot',
#             fields=[
#                 ('itemId', models.IntegerField(primary_key=True, serialize=False)),
#                 ('name', models.CharField(max_length=30)),
#             ],
#         ),
#         migrations.CreateModel(
#             name='Platform',
#             fields=[
#                 ('code', models.CharField(choices=[('na1', 'na1'), ('euw1', 'euw1'), ('br1', 'br1')], primary_key=True, serialize=False)),
#                 ('region', models.ForeignKey(db_column='region', on_delete=django.db.models.deletion.CASCADE, to='wrs_api.region')),
#             ],
#         ),
#         migrations.CreateModel(
#             name='Patch',
#             fields=[
#                 ('full_version', models.CharField(max_length=25, primary_key=True, serialize=False)),
#                 ('version', models.CharField(max_length=6)),
#                 ('season_id', models.ForeignKey(db_column='season_id', on_delete=django.db.models.deletion.CASCADE, to='wrs_api.season')),
#             ],
#         ),
#         migrations.RunSQL(sql=[
#             """
#             --- make "id" no longer a primary key (SERIAL NOT NULL)
#             --- use PSQL declarative partitioning where necessary to partition tables
#             --- create composite primary keys where necessary for partitioning
#             --- for tables that references composite primary keys the composite fields must be present in the related table
#             --- define the foreign key has a combination of the primary key fields in the same order of primary key they are referencing
#             --- remove everything after NOT NULL on "id" (PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY), create partition, add partitions, insert partitions after foreign key constraint, add composite PK
#             --- ADD ON DELETE CASCADE to all FOREIGN KEYS
#             --- cosmetically clean up ALTER table commands (make them part of the table definition)
                
                
#                 --- Model Summoner
#                 --- Model Summoner
#                 --- Model Summoner
#                 CREATE TABLE "wrs_api_summoner" (
#                     "id" SERIAL NOT NULL,
#                     "puuid" varchar(100) NOT NULL,
#                     "gameName" varchar(50) NOT NULL,
#                     "tagLine" varchar(10) NOT NULL,
#                     "profileIconId" integer NOT NULL,
#                     "encryptedSummonerId" varchar(100) NOT NULL,
#                     "most_recent_game" varchar(25) NULL,
#                     "created_at" timestamp with time zone NOT NULL,
#                     "updated_at" timestamp with time zone NOT NULL,
#                     "platform" varchar NOT NULL,
#                     FOREIGN KEY ("platform") REFERENCES wrs_api_platform ("code") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     UNIQUE ("puuid", "platform"),
#                     PRIMARY KEY (platform, puuid)
#                 ) PARTITION BY LIST (platform);

#                 CREATE TABLE wrs_api_summoner_na1 PARTITION OF wrs_api_summoner FOR VALUES IN ('na1');
#                 CREATE TABLE wrs_api_summoner_euw1 PARTITION OF wrs_api_summoner FOR VALUES IN ('euw1');
#                 CREATE TABLE wrs_api_summoner_br1 PARTITION OF wrs_api_summoner FOR VALUES IN ('br1');

#                 --- DO NOT NEED FOR PUUID: CREATE INDEX "wrs_api_summoner_puuid_ec1c8f0f_like" ON "wrs_api_summoner" ("puuid" varchar_pattern_ops);
#                 CREATE INDEX "wrs_api_summoner_puuid_ec1c8f0f" ON "wrs_api_summoner" ("puuid");
#                 CREATE INDEX "wrs_api_summoner_platform_39a7e8f3" ON "wrs_api_summoner" ("platform");
#                 --- CREATE INDEX "wrs_api_summoner_platform_39a7e8f3_like" ON "wrs_api_summoner" ("platform" varchar_pattern_ops);

                
#                 --- Model SummonerOverview
#                 --- Model SummonerOverview
#                 --- Model SummonerOverview
#                 CREATE TABLE "wrs_api_summoneroverview" (
#                     "id" SERIAL NOT NULL,
#                     "puuid" varchar(100) NOT NULL,
#                     "platform" varchar NOT NULL, 
#                     "season_id" bigint NOT NULL, 
#                     "metadata" jsonb NOT NULL,
#                     "created_at" timestamp with time zone NOT NULL,
#                     "updated_at" timestamp with time zone NOT NULL,
#                     FOREIGN KEY (platform, puuid) REFERENCES wrs_api_summoner (platform, puuid) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY (season_id) REFERENCES wrs_api_season (id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("platform") REFERENCES wrs_api_platform ("code") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     UNIQUE ("season_id", "puuid", "platform"),
#                     PRIMARY KEY (puuid, season_id, platform)
#                 ) PARTITION BY LIST (platform);
                
#                 CREATE TABLE wrs_api_summoneroverview_na1 PARTITION OF wrs_api_summoneroverview FOR VALUES IN ('na1');
#                 CREATE TABLE wrs_api_summoneroverview_euw1 PARTITION OF wrs_api_summoneroverview FOR VALUES IN ('euw1');
#                 CREATE TABLE wrs_api_summoneroverview_br1 PARTITION OF wrs_api_summoneroverview FOR VALUES IN ('br1');

#                 CREATE INDEX "wrs_api_summoneroverview_platform_99315587" ON "wrs_api_summoneroverview" ("platform");
#                 --- DO NOT NEED FOR PLATFORM: CREATE INDEX "wrs_api_summoneroverview_platform_99315587_like" ON "wrs_api_summoneroverview" ("platform" varchar_pattern_ops);
#                 CREATE INDEX "wrs_api_summoneroverview_season_id_4cf689b6" ON "wrs_api_summoneroverview" ("season_id");
#                 CREATE INDEX "wrs_api_summoneroverview_summoner_id_4f6afb74" ON "wrs_api_summoneroverview" ("puuid");

                
#                 --- Model Match
#                 --- Model Match
#                 --- Model Match
#                 CREATE TABLE "wrs_api_match" (
#                     "id" SERIAL NOT NULL,
#                     "matchId" varchar(20) NOT NULL,
#                     "elo" varchar NOT NULL,
#                     "queueId" integer NOT NULL, 
#                     "season_id" bigint NOT NULL,
#                     "patch" varchar(25) NOT NULL, 
#                     "platform" varchar NOT NULL, 
#                     "metadata" jsonb NOT NULL, 
#                     PRIMARY KEY ("platform", "matchId"),
#                     FOREIGN KEY ("elo") REFERENCES wrs_api_rank ("elo") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("queueId") REFERENCES wrs_api_gamemode ("queueId") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("patch") REFERENCES wrs_api_patch ("full_version") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("season_id") REFERENCES wrs_api_season ("id") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("platform") REFERENCES "wrs_api_platform" ("code") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED
#                 ) PARTITION BY LIST ("platform");


#                 CREATE TABLE wrs_api_match_na1 PARTITION OF wrs_api_match FOR VALUES IN ('na1');
#                 CREATE TABLE wrs_api_match_euw1 PARTITION OF wrs_api_match FOR VALUES IN ('euw1');
#                 CREATE TABLE wrs_api_match_br1 PARTITION OF wrs_api_match FOR VALUES IN ('br1');

#                 CREATE INDEX "wrs_api_match_patch_0b245097" ON "wrs_api_match" ("patch");
#                 CREATE INDEX "wrs_api_match_patch_0b245097_like" ON "wrs_api_match" ("patch" varchar_pattern_ops);
#                 CREATE INDEX "wrs_api_match_platform_2b2c1736" ON "wrs_api_match" ("platform");
#                 --- DO NOT NEED FOR PLATFORM: CREATE INDEX "wrs_api_match_platform_2b2c1736_like" ON "wrs_api_match" ("platform" varchar_pattern_ops);
#                 CREATE INDEX "wrs_api_match_queueId_id_28ffec5b" ON "wrs_api_match" ("queueId");
#                 CREATE INDEX "wrs_api_match_season_id_996a93bd" ON "wrs_api_match" ("season_id");
#                 CREATE INDEX "wrs_api_match_elo_118c15ef" ON "wrs_api_match" ("elo");
#                 CREATE INDEX "wrs_api_match_elo_442j40i8_like" ON "wrs_api_match" ("elo" varchar_pattern_ops);

                
#                 --- Model summonermatch
#                 --- Model summonermatch
#                 --- Model summonermatch
#                 CREATE TABLE "wrs_api_summonermatch" (
#                     "id" SERIAL NOT NULL,
#                     "matchId" varchar(20) NOT NULL,
#                     "elo" varchar NOT NULL,
#                     "queueId" integer NOT NULL, 
#                     "puuid" varchar(100) NOT NULL,
#                     "season_id" bigint NOT NULL, 
#                     "patch" VARCHAR(25) NOT NULL,
#                     "platform" varchar NOT NULL,
#                     FOREIGN KEY ("elo") REFERENCES wrs_api_rank ("elo") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("platform", "matchId") REFERENCES wrs_api_match ("platform", "matchId") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("platform", "puuid") REFERENCES wrs_api_summoner ("platform", "puuid") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("queueId") REFERENCES wrs_api_gamemode ("queueId") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("patch") REFERENCES wrs_api_patch ("full_version") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("season_id") REFERENCES wrs_api_season ("id") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("platform") REFERENCES "wrs_api_platform" ("code") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     UNIQUE ("matchId", "puuid", "platform"),
#                     PRIMARY KEY ("platform", "matchId", "puuid")
#                 ) PARTITION BY LIST (platform);

#                 CREATE TABLE wrs_api_summonermatch_na1 PARTITION OF wrs_api_summonermatch FOR VALUES IN ('na1');
#                 CREATE TABLE wrs_api_summonermatch_euw1 PARTITION OF wrs_api_summonermatch FOR VALUES IN ('euw1');
#                 CREATE TABLE wrs_api_summonermatch_br1 PARTITION OF wrs_api_summonermatch FOR VALUES IN ('br1');

#                 CREATE INDEX "wrs_api_summonermatch_matchId_d9b8b076" ON "wrs_api_summonermatch" ("matchId");
#                 CREATE INDEX "wrs_api_summonermatch_queueId_id_39ggfd6c" ON "wrs_api_summonermatch" ("queueId");
#                 CREATE INDEX "wrs_api_summonermatch_puuid_1a034af0" ON "wrs_api_summonermatch" ("puuid");
#                 CREATE INDEX "wrs_api_summonermatch_patch_c0a9c187" ON "wrs_api_summonermatch" ("patch");
#                 CREATE INDEX "wrs_api_summonermatch_season_id_2b145bg1" ON "wrs_api_summonermatch" ("season_id");
#                 CREATE INDEX "wrs_api_summonermatch_platform_d11ab006" ON "wrs_api_summonermatch" ("platform");
#                 CREATE INDEX "wrs_api_summonermatch_elo_114b13cc" ON "wrs_api_summonermatch" ("elo");
#                 CREATE INDEX "wrs_api_summonermatch_elo_221d20f4_like" ON "wrs_api_summonermatch" ("elo" varchar_pattern_ops);
                

#                 --- Model ChampionStat
#                 --- Model ChampionStat
#                 --- Model ChampionStat
#                 CREATE TABLE "wrs_api_championstat" (
#                     "id" SERIAL NOT NULL,
#                     "championId" INTEGER NOT NULL,
#                     "role" varchar NOT NULL,
#                     "elo" varchar NOT NULL,
#                     "wins" INTEGER NOT NULL,
#                     "losses" INTEGER NOT NULL,
#                     "picked" INTEGER NOT NULL,
#                     "patch" VARCHAR(25) NOT NULL,
#                     "platform" VARCHAR NOT NULL,
#                     "season_id" BIGINT NOT NULL,
#                     FOREIGN KEY ("championId") REFERENCES wrs_api_champion ("championId") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("elo") REFERENCES wrs_api_rank ("elo") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("role") REFERENCES wrs_api_role ("name") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("patch") REFERENCES wrs_api_patch ("full_version") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("platform") REFERENCES wrs_api_platform ("code") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("season_id") REFERENCES wrs_api_season ("id") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     UNIQUE ("platform","championId", "patch", "role", "elo", "season_id"),
#                     PRIMARY KEY ("platform","championId", "patch", "role", "elo", "season_id")
#                 ) PARTITION BY LIST ("platform");

#                 CREATE TABLE wrs_api_championstat_na1 PARTITION OF wrs_api_championstat FOR VALUES IN ('na1');
#                 CREATE TABLE wrs_api_championstat_br1 PARTITION OF wrs_api_championstat FOR VALUES IN ('br1');
#                 CREATE TABLE wrs_api_championstat_euw1 PARTITION OF wrs_api_championstat FOR VALUES IN ('euw1');

#                 CREATE INDEX wrs_api_championstat_championId_c231a738 ON wrs_api_championstat ("championId");
#                 CREATE INDEX wrs_api_championstat_patch_db5180eb ON wrs_api_championstat ("patch");
#                 CREATE INDEX wrs_api_championstat_patch__db5180eb_like ON wrs_api_championstat ("patch" varchar_pattern_ops);
#                 CREATE INDEX wrs_api_championstat_platform_88d7ca7a ON wrs_api_championstat ("platform");
#                 CREATE INDEX wrs_api_championstat_season_id_24005562 ON wrs_api_championstat ("season_id");
#                 CREATE INDEX wrs_api_championstat_elo_332g39hj ON "wrs_api_championstat" ("elo");
#                 CREATE INDEX wrs_api_championstat_elo_875i14ln ON "wrs_api_championstat" ("role");
#                 CREATE INDEX wrs_api_championstat_elo_764f15t8_like ON "wrs_api_championstat" ("elo" varchar_pattern_ops);


#                 --- Model BanStat
#                 --- Model BanStat
#                 --- Model BanStat
#                 CREATE TABLE "wrs_api_banstat" (
#                     "id" SERIAL NOT NULL,
#                     "championId" INTEGER NOT NULL,
#                     "elo" varchar NOT NULL,
#                     "banned" INTEGER NOT NULL,
#                     "patch" VARCHAR(25) NOT NULL,
#                     "platform" VARCHAR NOT NULL,
#                     "season_id" BIGINT NOT NULL,
#                     FOREIGN KEY ("championId") REFERENCES wrs_api_champion ("championId") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("elo") REFERENCES wrs_api_rank ("elo") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("patch") REFERENCES wrs_api_patch ("full_version") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("platform") REFERENCES wrs_api_platform ("code") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("season_id") REFERENCES wrs_api_season ("id") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     UNIQUE ("platform","championId", "patch", "elo", "season_id"),
#                     PRIMARY KEY ("platform","championId", "patch", "elo", "season_id")
#                 ) PARTITION BY LIST ("platform");

#                 CREATE TABLE wrs_api_banstat_na1 PARTITION OF wrs_api_banstat FOR VALUES IN ('na1');
#                 CREATE TABLE wrs_api_banstat_br1 PARTITION OF wrs_api_banstat FOR VALUES IN ('br1');
#                 CREATE TABLE wrs_api_banstat_euw1 PARTITION OF wrs_api_banstat FOR VALUES IN ('euw1');

#                 CREATE INDEX wrs_api_banstat_championId_c231a738 ON wrs_api_banstat ("championId");
#                 CREATE INDEX wrs_api_banstat_patch_db5180eb ON wrs_api_banstat ("patch");
#                 CREATE INDEX wrs_api_banstat_patch__db5180eb_like ON wrs_api_banstat ("patch" varchar_pattern_ops);
#                 CREATE INDEX wrs_api_banstat_platform_88d7ca7a ON wrs_api_banstat ("platform");
#                 CREATE INDEX wrs_api_banstat_season_id_24005562 ON wrs_api_banstat ("season_id");
#                 CREATE INDEX wrs_api_banstat_elo_332g39hj ON "wrs_api_banstat" ("elo");
#                 CREATE INDEX wrs_api_banstat_elo_764f15t8_like ON "wrs_api_banstat" ("elo" varchar_pattern_ops);



#                 --- Model RunePageStat
#                 --- Model RunePageStat     
#                 --- Model RunePageStat
#                 CREATE TABLE wrs_api_runepagestat (
#                     "id" SERIAL NOT NULL,
#                     "keystone" INTEGER NOT NULL,
#                     "primary_one" INTEGER NOT NULL,
#                     "primary_two" INTEGER NOT NULL,
#                     "primary_three" INTEGER NOT NULL,
#                     "secondary_one" INTEGER NOT NULL,
#                     "secondary_two" INTEGER NOT NULL,
#                     "shard_one" INTEGER NOT NULL,
#                     "shard_two" INTEGER NOT NULL,
#                     "shard_three" INTEGER NOT NULL,
#                     "championId" INTEGER NOT NULL,
#                     "role" varchar NOT NULL,
#                     "elo" varchar NOT NULL,
#                     "wins" INTEGER NOT NULL,
#                     "losses" INTEGER NOT NULL,
#                     "picked" INTEGER NOT NULL,
#                     "patch" VARCHAR(25) NOT NULL,
#                     "platform" VARCHAR NOT NULL,
#                     "season_id" BIGINT NOT NULL,
#                     FOREIGN KEY ("elo") REFERENCES wrs_api_rank ("elo") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("role") REFERENCES wrs_api_role ("name") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("championId") REFERENCES wrs_api_champion ("championId") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("keystone") REFERENCES wrs_api_keystone ("keystone_id") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("primary_one") REFERENCES wrs_api_primaryperkone ("perk_id") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("primary_two") REFERENCES wrs_api_primaryperktwo ("perk_id") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("primary_three") REFERENCES wrs_api_primaryperkthree ("perk_id") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("secondary_one") REFERENCES wrs_api_secondaryperkone ("perk_id") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("secondary_two") REFERENCES wrs_api_secondaryperktwo ("perk_id") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("shard_one") REFERENCES wrs_api_statshardone ("shard_id") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("shard_two") REFERENCES wrs_api_statshardtwo ("shard_id") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("shard_three") REFERENCES wrs_api_statshardthree ("shard_id") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("patch") REFERENCES wrs_api_patch ("full_version") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("platform") REFERENCES wrs_api_platform ("code") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("season_id") REFERENCES wrs_api_season ("id") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     UNIQUE ("keystone", "primary_one", "primary_two", "primary_three", "secondary_one", "secondary_two", "shard_one", "shard_two", "shard_three", "championId", "platform", "patch", "role", "elo", "season_id"),
#                     PRIMARY KEY ("keystone", "primary_one", "primary_two", "primary_three", "secondary_one", "secondary_two", "shard_one", "shard_two", "shard_three", "championId", "platform", "patch", "role", "elo", "season_id")
#                 ) PARTITION BY LIST ("platform");

#                 CREATE TABLE wrs_api_runepagestat_na1 PARTITION OF wrs_api_runepagestat FOR VALUES IN ('na1');
#                 CREATE TABLE wrs_api_runepagestat_br1 PARTITION OF wrs_api_runepagestat FOR VALUES IN ('br1');
#                 CREATE TABLE wrs_api_runepagestat_euw1 PARTITION OF wrs_api_runepagestat FOR VALUES IN ('euw1');                

#                 CREATE INDEX wrs_api_runepagestat_championId_37f26e8d ON wrs_api_runepagestat ("championId");
#                 CREATE INDEX idx_wrs_api_runepagestat_keystone ON wrs_api_runepagestat ("keystone");
#                 CREATE INDEX idx_wrs_api_runepagestat_primary_one ON wrs_api_runepagestat ("primary_one");
#                 CREATE INDEX idx_wrs_api_runepagestat_primary_two ON wrs_api_runepagestat ("primary_two");
#                 CREATE INDEX idx_wrs_api_runepagestat_primary_three ON wrs_api_runepagestat ("primary_three");
#                 CREATE INDEX idx_wrs_api_runepagestat_secondary_one ON wrs_api_runepagestat ("secondary_one");
#                 CREATE INDEX idx_wrs_api_runepagestat_secondary_two ON wrs_api_runepagestat ("secondary_two");
#                 CREATE INDEX idx_wrs_api_runepagestat_shard_one ON wrs_api_runepagestat ("shard_one");
#                 CREATE INDEX idx_wrs_api_runepagestat_shard_two ON wrs_api_runepagestat ("shard_two");
#                 CREATE INDEX idx_wrs_api_runepagestat_shard_three ON wrs_api_runepagestat ("shard_three");
#                 CREATE INDEX idx_wrs_api_runepagestat_role ON wrs_api_runepagestat ("role");
#                 CREATE INDEX wrs_api_runepagestat_patch_a2f5b0fa ON wrs_api_runepagestat ("patch");
#                 CREATE INDEX wrs_api_runepagestat_patch_a2f5b0fa_like ON wrs_api_runepagestat ("patch" varchar_pattern_ops);
#                 CREATE INDEX wrs_api_runepagestat_platform_83170699 ON wrs_api_runepagestat ("platform");
#                 CREATE INDEX wrs_api_runepagestat_season_id_e2eb2542 ON wrs_api_runepagestat ("season_id");
#                 CREATE INDEX wrs_api_runepagestat_elo_764f15t8 ON wrs_api_runepagestat ("elo");
#                 CREATE INDEX wrs_api_runepagestat_elo_764f15t8_like ON wrs_api_runepagestat ("elo" varchar_pattern_ops);    

                
#                 --- Model ItemBuildStat
#                 --- Model ItemBuildStat     
#                 --- Model ItemBuildStat
#                 CREATE TABLE wrs_api_itembuildstat (
#                     "id" SERIAL NOT NULL,
#                     "legendary_one" INTEGER NOT NULL,
#                     "legendary_two" INTEGER NULL,
#                     "legendary_three" INTEGER NULL,
#                     "legendary_four" INTEGER NULL,
#                     "legendary_five" INTEGER NULL,
#                     "legendary_six" INTEGER NULL,
#                     "championId" INTEGER NOT NULL,
#                     "role" varchar NOT NULL,
#                     "elo" varchar NOT NULL,
#                     "wins" INTEGER NOT NULL,
#                     "losses" INTEGER NOT NULL,
#                     "patch" VARCHAR(25) NOT NULL,
#                     "platform" VARCHAR NOT NULL,
#                     "season_id" BIGINT NOT NULL,
#                     FOREIGN KEY ("elo") REFERENCES wrs_api_rank ("elo") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("role") REFERENCES wrs_api_role ("name") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("championId") REFERENCES wrs_api_champion ("championId") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("legendary_one") REFERENCES wrs_api_legendaryitem ("itemId") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("legendary_two") REFERENCES wrs_api_legendaryitem ("itemId") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("legendary_three") REFERENCES wrs_api_legendaryitem ("itemId") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("legendary_four") REFERENCES wrs_api_legendaryitem ("itemId") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("legendary_five") REFERENCES wrs_api_legendaryitem ("itemId") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("legendary_six") REFERENCES wrs_api_legendaryitem ("itemId") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("patch") REFERENCES wrs_api_patch ("full_version") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("platform") REFERENCES wrs_api_platform ("code") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("season_id") REFERENCES wrs_api_season ("id") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     UNIQUE ("legendary_one", "legendary_two", "legendary_three", "legendary_four", "legendary_five", "legendary_six", "championId", "platform", "patch", "role", "elo", "season_id"),
#                     PRIMARY KEY ("legendary_one", "legendary_two", "legendary_three", "legendary_four", "legendary_five", "legendary_six", "championId", "platform", "patch", "role", "elo", "season_id")
#                 ) PARTITION BY LIST ("platform");

#                 CREATE TABLE wrs_api_itembuildstat_na1 PARTITION OF wrs_api_itembuildstat FOR VALUES IN ('na1');
#                 CREATE TABLE wrs_api_itembuildstat_br1 PARTITION OF wrs_api_itembuildstat FOR VALUES IN ('br1');
#                 CREATE TABLE wrs_api_itembuildstat_euw1 PARTITION OF wrs_api_itembuildstat FOR VALUES IN ('euw1');                

#                 CREATE INDEX wrs_api_itembuildstat_championId_37f26e8d ON wrs_api_itembuildstat ("championId");                
#                 CREATE INDEX wrs_api_itembuildstat_legendary_one_e24cdaad ON wrs_api_itembuildstat ("legendary_one");
#                 CREATE INDEX wrs_api_itembuildstat_legendary_two_e24cdaad ON wrs_api_itembuildstat ("legendary_two");
#                 CREATE INDEX wrs_api_itembuildstat_legendary_three_e24cdaad ON wrs_api_itembuildstat ("legendary_three");
#                 CREATE INDEX wrs_api_itembuildstat_legendary_four_e24cdaad ON wrs_api_itembuildstat ("legendary_four");
#                 CREATE INDEX wrs_api_itembuildstat_legendary_five_e24cdaad ON wrs_api_itembuildstat ("legendary_five");
#                 CREATE INDEX wrs_api_itembuildstat_legendary_six_e24cdaad ON wrs_api_itembuildstat ("legendary_six");
#                 CREATE INDEX wrs_api_itembuildstat_patch_a2f5b0fa ON wrs_api_itembuildstat ("patch");
#                 CREATE INDEX wrs_api_itembuildstat_patch_a2f5b0fa_like ON wrs_api_itembuildstat ("patch" varchar_pattern_ops);
#                 CREATE INDEX wrs_api_itembuildstat_platform_83170699 ON wrs_api_itembuildstat ("platform");
#                 CREATE INDEX wrs_api_itembuildstat_season_id_e2eb2542 ON wrs_api_itembuildstat ("season_id");
#                 CREATE INDEX wrs_api_itembuildstat_role_221f02t3 ON wrs_api_itembuildstat ("role");
#                 CREATE INDEX wrs_api_itembuildstat_elo_764f15t8 ON wrs_api_itembuildstat ("elo");
#                 CREATE INDEX wrs_api_itembuildstat_elo_764f15t8_like ON wrs_api_itembuildstat ("elo" varchar_pattern_ops);
                

#                 -- Model TierTwoBootStat
#                 -- Model TierTwoBootStat   
#                 -- Model TierTwoBootStat
#                 CREATE TABLE wrs_api_tiertwobootstat (
#                     "id" SERIAL NOT NULL,
#                     "tier_two_boot" INTEGER NOT NULL,
#                     "championId" INTEGER NOT NULL,
#                     "role" varchar NOT NULL,
#                     "elo" varchar NOT NULL,
#                     "wins" INTEGER NOT NULL,
#                     "losses" INTEGER NOT NULL,
#                     "patch" VARCHAR(25) NOT NULL,
#                     "platform" VARCHAR NOT NULL,
#                     "season_id" BIGINT NOT NULL,
#                     FOREIGN KEY ("elo") REFERENCES wrs_api_rank ("elo") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("role") REFERENCES wrs_api_role ("name") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("championId") REFERENCES wrs_api_champion ("championId") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("tier_two_boot") REFERENCES wrs_api_tiertwoboot ("itemId") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("patch") REFERENCES wrs_api_patch (full_version) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("platform") REFERENCES wrs_api_platform (code) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("season_id") REFERENCES wrs_api_season (id) DEFERRABLE INITIALLY DEFERRED,
#                     UNIQUE ("platform", "tier_two_boot", "championId","patch", "role", "elo", "season_id"),
#                     PRIMARY KEY ("platform", "tier_two_boot", "championId","patch", "role", "elo", "season_id")
#                 ) PARTITION BY LIST ("platform");

#                 CREATE TABLE wrs_api_tiertwobootstat_na1 PARTITION OF wrs_api_tiertwobootstat FOR VALUES IN ('na1');
#                 CREATE TABLE wrs_api_tiertwobootstat_br1 PARTITION OF wrs_api_tiertwobootstat FOR VALUES IN ('br1');
#                 CREATE TABLE wrs_api_tiertwobootstat_euw1 PARTITION OF wrs_api_tiertwobootstat FOR VALUES IN ('euw1');

#                 CREATE INDEX wrs_api_tiertwobootstat_championId ON wrs_api_tiertwobootstat ("championId");
#                 CREATE INDEX wrs_api_tiertwobootstat_tier_two_boot ON wrs_api_tiertwobootstat ("tier_two_boot");
#                 CREATE INDEX wrs_api_tiertwobootstat_patch ON wrs_api_tiertwobootstat ("patch");
#                 CREATE INDEX wrs_api_tiertwobootstat_patch_like ON wrs_api_tiertwobootstat ("patch" varchar_pattern_ops);
#                 CREATE INDEX wrs_api_tiertwobootstat_platform ON wrs_api_tiertwobootstat ("platform");
#                 CREATE INDEX wrs_api_tiertwobootstat_season_id ON wrs_api_tiertwobootstat ("season_id");
#                 CREATE INDEX wrs_api_tiertwobootstat_role ON wrs_api_tiertwobootstat ("role");
#                 CREATE INDEX wrs_api_tiertwobootstat_elo_p9q0r1s2 ON wrs_api_tiertwobootstat ("elo");
#                 CREATE INDEX wrs_api_tiertwobootstat_elo_p9q0r1s2_like ON wrs_api_tiertwobootstat ("elo" varchar_pattern_ops);

                
#                 -- Model SummonerSpellStat
#                 -- Model SummonerSpellStat   
#                 -- Model SummonerSpellStat
#                 CREATE TABLE wrs_api_summonerspellstat (
#                     "id" SERIAL NOT NULL,
#                     "spell_one" INTEGER NOT NULL,
#                     "spell_two" INTEGER NOT NULL,
#                     "championId" INTEGER NOT NULL,
#                     "role" varchar NOT NULL,
#                     "elo" varchar NOT NULL,
#                     "wins" INTEGER NOT NULL,
#                     "losses" INTEGER NOT NULL,
#                     "picked" INTEGER NOT NULL,
#                     "patch" VARCHAR(25) NOT NULL,
#                     "platform" VARCHAR NOT NULL,
#                     "season_id" BIGINT NOT NULL,
#                     FOREIGN KEY ("elo") REFERENCES wrs_api_rank ("elo") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("championId") REFERENCES wrs_api_champion ("championId") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("spell_one") REFERENCES wrs_api_summonerspell ("spellId") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("spell_two") REFERENCES wrs_api_summonerspell ("spellId") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("patch") REFERENCES wrs_api_patch (full_version) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("platform") REFERENCES wrs_api_platform (code) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("season_id") REFERENCES wrs_api_season (id) DEFERRABLE INITIALLY DEFERRED,
#                     UNIQUE ("platform", "spell_one", "spell_two", "championId","patch", "role", "elo", "season_id"),
#                     PRIMARY KEY ("platform", "spell_one", "spell_two", "championId","patch", "role", "elo", "season_id")
#                 ) PARTITION BY LIST ("platform");

#                 CREATE TABLE wrs_api_summonerspellstat_na1 PARTITION OF wrs_api_summonerspellstat FOR VALUES IN ('na1');
#                 CREATE TABLE wrs_api_summonerspellstat_br1 PARTITION OF wrs_api_summonerspellstat FOR VALUES IN ('br1');
#                 CREATE TABLE wrs_api_summonerspellstat_euw1 PARTITION OF wrs_api_summonerspellstat FOR VALUES IN ('euw1');

#                 CREATE INDEX wrs_api_summonerspellstat_championId ON wrs_api_summonerspellstat ("championId");
#                 CREATE INDEX wrs_api_summonerspellstat_spell_one ON wrs_api_summonerspellstat ("spell_one");
#                 CREATE INDEX wrs_api_summonerspellstat_spell_two ON wrs_api_summonerspellstat ("spell_two");
#                 CREATE INDEX wrs_api_summonerspellstat_patch ON wrs_api_summonerspellstat ("patch");
#                 CREATE INDEX wrs_api_summonerspellstat_patch_like ON wrs_api_summonerspellstat ("patch" varchar_pattern_ops);
#                 CREATE INDEX wrs_api_summonerspellstat_platform ON wrs_api_summonerspellstat ("platform");
#                 CREATE INDEX wrs_api_summonerspellstat_season_id ON wrs_api_summonerspellstat ("season_id");
#                 CREATE INDEX wrs_api_summonerspellstat_role ON wrs_api_summonerspellstat ("role");
#                 CREATE INDEX wrs_api_summonerspellstat_elo_p9q0r1s2 ON wrs_api_summonerspellstat ("elo");
#                 CREATE INDEX wrs_api_summonerspellstat_elo_p9q0r1s2_like ON wrs_api_summonerspellstat ("elo" varchar_pattern_ops);
#             """],
#             reverse_sql=[
#                 """
#                     DROP TABLE wrs_api_summoner_na1 CASCADE;
#                     DROP TABLE wrs_api_summoner_euw1 CASCADE;
#                     DROP TABLE wrs_api_summoner_br1 CASCADE;
#                     DROP TABLE wrs_api_summoner CASCADE;

#                     DROP TABLE wrs_api_summoneroverview_na1 CASCADE;
#                     DROP TABLE wrs_api_summoneroverview_euw1 CASCADE;
#                     DROP TABLE wrs_api_summoneroverview_br1 CASCADE;
#                     DROP TABLE wrs_api_summoneroverview CASCADE;

#                     DROP TABLE wrs_api_match_na1 CASCADE;
#                     DROP TABLE wrs_api_match_euw1 CASCADE;
#                     DROP TABLE wrs_api_match_br1 CASCADE;
#                     DROP TABLE wrs_api_match CASCADE;

#                     DROP TABLE wrs_api_summonermatch_na1 CASCADE;
#                     DROP TABLE wrs_api_summonermatch_euw1 CASCADE;
#                     DROP TABLE wrs_api_summonermatch_br1 CASCADE;
#                     DROP TABLE wrs_api_summonermatch CASCADE;

#                     DROP TABLE wrs_api_championstat_na1 CASCADE;
#                     DROP TABLE wrs_api_championstat_euw1 CASCADE;
#                     DROP TABLE wrs_api_championstat_br1 CASCADE;
#                     DROP TABLE wrs_api_championstat CASCADE;

#                     DROP TABLE wrs_api_runepagestat_na1 CASCADE;
#                     DROP TABLE wrs_api_runepagestat_euw1 CASCADE;
#                     DROP TABLE wrs_api_runepagestat_br1 CASCADE;
#                     DROP TABLE wrs_api_runepagestat CASCADE;

#                     DROP TABLE wrs_api_itembuildstat_na1 CASCADE;
#                     DROP TABLE wrs_api_itembuildstat_euw1 CASCADE;
#                     DROP TABLE wrs_api_itembuildstat_br1 CASCADE;
#                     DROP TABLE wrs_api_itembuildstat CASCADE;

#                     DROP TABLE wrs_api_tiertwobootstat_na1 CASCADE;
#                     DROP TABLE wrs_api_tiertwobootstat_euw1 CASCADE;
#                     DROP TABLE wrs_api_tiertwobootstat_br1 CASCADE;
#                     DROP TABLE wrs_api_tiertwobootstat CASCADE;

#                     DROP TABLE wrs_api_summonerspellstat_na1 CASCADE;
#                     DROP TABLE wrs_api_summonerspellstat_euw1 CASCADE;
#                     DROP TABLE wrs_api_summonerspellstat_br1 CASCADE;
#                     DROP TABLE wrs_api_summonerspellstat CASCADE;

#                     DROP TABLE wrs_api_banstat_na1 CASCADE;
#                     DROP TABLE wrs_api_banstat_euw1 CASCADE;
#                     DROP TABLE wrs_api_banstat_br1 CASCADE;
#                     DROP TABLE wrs_api_banstat CASCADE;
#                 """
#             ]
#         )
#     ]
