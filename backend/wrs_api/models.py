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

class Season(models.Model):    
    season = models.IntegerField()
    split = models.IntegerField()


class Patch(models.Model):
    full_version = models.CharField(max_length=25, primary_key=True)
    version = models.CharField(max_length=6)
    season_id = models.ForeignKey(Season, db_column="season_id",on_delete=models.CASCADE)


class Region(models.Model):
    name_optons = [("americas", "americas"), ("asia", "asia"), ("europe", "europe"), ("sea", "sea"), ("esports", "esports")]
    name = models.CharField(choices=name_optons, primary_key=True)


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


    # def refresh_overview(self, updated_overview):
    #     with connection.cursor() as cursor:
    #         cursor.execute(
    #             """
    #                 UPDATE wrs_api_summoneroverview
    #                 SET metadata = %s
    #                 WHERE puuid = %s
    #                 AND platform = %s
    #                 AND season_id = %s;
    #             """,
    #             [updated_overview, self.puuid, self.platform.code, self.season_id]
    #         )

    # def refresh_overview(self, metadata):
    #     with connection.cursor() as cursor:
    #         cursor.execute(
    #             """
    #             UPDATE wrs_api_summoneroverview 
    #             SET metadata = %s 
    #             WHERE "puuid" = %s
    #             AND "platform" = %s
    #             RETURNING *;
    #             """,
    #             [metadata, self.puuid, self.platform.code]
    #         )
    #         new_overviews = cursor.fetchall()
    #     return new_overviews


############ IS JOIN TABLE MISSING AN INDEX ON PLATFORM? ################
############ IS JOIN TABLE MISSING AN INDEX ON PLATFORM? ################
############ IS JOIN TABLE MISSING AN INDEX ON PLATFORM? ################
############ IS JOIN TABLE MISSING AN INDEX ON PLATFORM? ################
############ IS JOIN TABLE MISSING AN INDEX ON PLATFORM? ################
############ IS JOIN TABLE MISSING AN INDEX ON PLATFORM? ################
############ IS JOIN TABLE MISSING AN INDEX ON PLATFORM? ################
        
# For Django's sake matchId is a primary key
# In PSQL primary key: matchId & platform
class Match(models.Model):
    matchId = models.CharField(max_length=20)
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
    wins = models.IntegerField()
    losses = models.IntegerField()
    picked = models.IntegerField()
    banned = models.IntegerField()
    season_id = models.ForeignKey(Season, on_delete=models.CASCADE)
    patch = models.ForeignKey(Patch, on_delete=models.CASCADE, to_field="full_version", db_column="patch")
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, db_column="platform", to_field="code")

    class Meta:
        unique_together = ["championId", "platform", "patch"]
        db_table = "wrs_api_championstat"
        managed = False


class BuiltFirstStat(models.Model):
    legendary_item = models.ForeignKey(LegendaryItem, on_delete=models.CASCADE, db_column="legendary_item")
    championId = models.ForeignKey(Champion, on_delete=models.CASCADE, to_field="championId", db_column="championId")
    wins = models.IntegerField()
    losses = models.IntegerField()
    season_id = models.ForeignKey(Season, on_delete=models.CASCADE, db_column="season_id")
    patch = models.ForeignKey(Patch, on_delete=models.CASCADE, to_field="full_version", db_column="patch")
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, db_column="platform", to_field="code")

    class Meta:
        unique_together = ["legendary_item", "championId", "platform", "patch"]
        db_table = "wrs_api_builtfirststat"
        managed = False


class BuiltSecondStat(models.Model):
    legendary_item = models.ForeignKey(LegendaryItem, on_delete=models.CASCADE, db_column="legendary_item")
    championId = models.ForeignKey(Champion, on_delete=models.CASCADE, to_field="championId", db_column="championId")
    wins = models.IntegerField()
    losses = models.IntegerField()
    season_id = models.ForeignKey(Season, on_delete=models.CASCADE, db_column="season_id")
    patch = models.ForeignKey(Patch, on_delete=models.CASCADE, to_field="full_version", db_column="patch")
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, db_column="platform", to_field="code")

    class Meta:
        unique_together = ["legendary_item", "championId", "platform", "patch"]
        db_table = "wrs_api_builtsecondstat"
        managed = False


class BuiltThirdStat(models.Model):
    legendary_item = models.ForeignKey(LegendaryItem, on_delete=models.CASCADE, db_column="legendary_item")
    championId = models.ForeignKey(Champion, on_delete=models.CASCADE, to_field="championId", db_column="championId")
    wins = models.IntegerField()
    losses = models.IntegerField()
    season_id = models.ForeignKey(Season, on_delete=models.CASCADE, db_column="season_id")
    patch = models.ForeignKey(Patch, on_delete=models.CASCADE, to_field="full_version", db_column="patch")
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, db_column="platform", to_field="code")

    class Meta:
        unique_together = ["legendary_item", "championId", "platform", "patch"]
        db_table = "wrs_api_builtthirdstat"
        managed = False


class BuiltFourthStat(models.Model):
    legendary_item = models.ForeignKey(LegendaryItem, on_delete=models.CASCADE, db_column="legendary_item")
    championId = models.ForeignKey(Champion, on_delete=models.CASCADE, to_field="championId", db_column="championId")
    wins = models.IntegerField()
    losses = models.IntegerField()
    season_id = models.ForeignKey(Season, on_delete=models.CASCADE, db_column="season_id")
    patch = models.ForeignKey(Patch, on_delete=models.CASCADE, to_field="full_version", db_column="patch")
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, db_column="platform", to_field="code")

    class Meta:
        unique_together = ["legendary_item", "championId", "platform", "patch"]
        db_table = "wrs_api_builtfourthstat"
        managed = False


class BuiltFifthStat(models.Model):
    legendary_item = models.ForeignKey(LegendaryItem, on_delete=models.CASCADE, db_column="legendary_item")
    championId = models.ForeignKey(Champion, on_delete=models.CASCADE, to_field="championId", db_column="championId")
    wins = models.IntegerField()
    losses = models.IntegerField()
    season_id = models.ForeignKey(Season, on_delete=models.CASCADE, db_column="season_id")
    patch = models.ForeignKey(Patch, on_delete=models.CASCADE, to_field="full_version", db_column="patch")
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, db_column="platform", to_field="code")

    class Meta:
        unique_together = ["legendary_item", "championId", "platform", "patch"]
        db_table = "wrs_api_builtfifthstat"
        managed = False


class BuiltSixthStat(models.Model):
    legendary_item = models.ForeignKey(LegendaryItem, on_delete=models.CASCADE, db_column="legendary_item")
    championId = models.ForeignKey(Champion, on_delete=models.CASCADE, to_field="championId", db_column="championId")
    wins = models.IntegerField()
    losses = models.IntegerField()
    season_id = models.ForeignKey(Season, on_delete=models.CASCADE, db_column="season_id")
    patch = models.ForeignKey(Patch, on_delete=models.CASCADE, to_field="full_version", db_column="patch")
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, db_column="platform", to_field="code")

    class Meta:
        unique_together = ["legendary_item", "championId", "platform", "patch"]
        db_table = "wrs_api_builtsixthstat"
        managed = False


class BuiltTierTwoBootStat(models.Model):
    tier_two_boot = models.ForeignKey(LegendaryItem, on_delete=models.CASCADE, db_column="tier_two_boot")
    championId = models.ForeignKey(Champion, on_delete=models.CASCADE, to_field="championId", db_column="championId")
    wins = models.IntegerField()
    losses = models.IntegerField()
    season_id = models.ForeignKey(Season, on_delete=models.CASCADE, db_column="season_id")
    patch = models.ForeignKey(Patch, on_delete=models.CASCADE, to_field="full_version", db_column="patch")
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, db_column="platform", to_field="code")

    class Meta:
        unique_together = ["tier_two_boot", "championId", "platform", "patch"]
        db_table = "wrs_api_builttiertwobootstat"
        managed = False















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


# # Generated by Django 4.2.7 on 2024-04-01 22:21

# from django.db import migrations, models
# import django.db.models.deletion


# class Migration(migrations.Migration):

#     initial = True

#     dependencies = [
#     ]

#     operations = [
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
#             name='MatchSummoner',
#             fields=[
#                 ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
#             ],
#             options={
#                 'db_table': 'wrs_api_match_summoners',
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
#             name='LegendaryItem',
#             fields=[
#                 ('itemId', models.IntegerField(primary_key=True, serialize=False)),
#                 ('name', models.CharField(max_length=30)),
#             ],
#         ),
#         migrations.CreateModel(
#             name='Region',
#             fields=[
#                 ('name', models.CharField(choices=[('americas', 'americas'), ('asia', 'asia'), ('europe', 'europe'), ('sea', 'sea'), ('esports', 'esports')], primary_key=True, serialize=False)),
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
#          migrations.RunSQL(
#             """
#             ---remove everything after NOT NULL on "id" (PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY), create partition, add partitions, insert partitions after foreign key constraint, add composite PK
#             --- at the momenent issue bc id has to be specified, which we dont want                 "id" bigint NOT NULL,
#             --- CHANGE id to SERIAL NOT NULL
#             --- make all ALTER TABLES part of the table definition
#             --- ADD ON DELETE CASCADE to all FOREIGN KEYS

#                 CREATE TABLE "wrs_api_summoner" (
#                     "id" SERIAL NOT NULL,
#                     "puuid" varchar(100) NOT NULL,
#                     "gameName" varchar(50) NOT NULL,
#                     "tagLine" varchar(10) NOT NULL,
#                     "profileIconId" integer NOT NULL,
#                      "encryptedSummonerId" varchar(100) NOT NULL,
#                     "most_recent_game" varchar(25) NULL,
#                     "created_at" timestamp with time zone NOT NULL,
#                     "updated_at" timestamp with time zone NOT NULL,
#                     "platform" varchar NOT NULL,
#                     FOREIGN KEY ("platform") REFERENCES wrs_api_platform ("code") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     CONSTRAINT "wrs_api_summoner_puuid_platform_c4182f4c_uniq" UNIQUE ("puuid", "platform"),
#                     PRIMARY KEY (platform, puuid)
#                 ) PARTITION BY LIST (platform);


#                 ---ALTER TABLE "wrs_api_summoner" ADD CONSTRAINT "wrs_api_summoner_puuid_platform_c4182f4c_uniq" UNIQUE ("puuid", "platform");
#                 ---ALTER TABLE "wrs_api_summoner" ADD CONSTRAINT "wrs_api_summoner_platform_39a7e8f3_fk_wrs_api_platform_code" FOREIGN KEY ("platform") REFERENCES "wrs_api_platform" ("code") DEFERRABLE INITIALLY DEFERRED;

#                 CREATE TABLE wrs_api_summoner_na1 PARTITION OF wrs_api_summoner FOR VALUES IN ('na1');
#                 CREATE TABLE wrs_api_summoner_euw1 PARTITION OF wrs_api_summoner FOR VALUES IN ('euw1');
#                 CREATE TABLE wrs_api_summoner_br1 PARTITION OF wrs_api_summoner FOR VALUES IN ('br1');


#                 CREATE INDEX "wrs_api_summoner_puuid_ec1c8f0f_like" ON "wrs_api_summoner" ("puuid" varchar_pattern_ops);
#                 CREATE INDEX "wrs_api_summoner_platform_39a7e8f3" ON "wrs_api_summoner" ("platform");
#                 CREATE INDEX "wrs_api_summoner_platform_39a7e8f3_like" ON "wrs_api_summoner" ("platform" varchar_pattern_ops);

#                 ---INSERT INTO wrs_api_platform (code) VALUES ("tr1"), ("ph2"), ("la1"), ("tw2"), ("la2"), ("eun1"), ("vn2"), ("kr"), ("oc1"), ("na1"), ("jp1"), ("euw1"), ("sg2"), ("ru"), ("th2"), ("br1");
#                 ---INSERT INTO wrs_api_platform (code) VALUES ('na1'), ('euw1'), ('br1');

#             """
#         ),
#         migrations.RunSQL(
#             """
#                 --- OVERVIEWS
#                 CREATE TABLE "wrs_api_summoneroverview" (
#                 "id" SERIAL NOT NULL,
#                 "puuid" varchar(100) NOT NULL,
#                 "platform" varchar NOT NULL, 
#                 "season_id" bigint NOT NULL, 
#                 "metadata" jsonb NOT NULL,
#                 "created_at" timestamp with time zone NOT NULL,
#                 "updated_at" timestamp with time zone NOT NULL,
#                 FOREIGN KEY (platform, puuid) REFERENCES wrs_api_summoner (platform, puuid) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                 FOREIGN KEY (season_id) REFERENCES wrs_api_season (id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                 FOREIGN KEY ("platform") REFERENCES wrs_api_platform ("code") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                 CONSTRAINT "wrs_api_summoneroverview_season_id_summoner_id_pl_1da9a9db_uniq" UNIQUE ("season_id", "puuid", "platform"),
#                 PRIMARY KEY (puuid, season_id, platform)
#                 ) PARTITION BY LIST (platform);
                

#                 ---ALTER TABLE "wrs_api_summoneroverview" 
#                 ---    ADD CONSTRAINT "wrs_api_summoneroverview_season_id_summoner_id_pl_1da9a9db_uniq" UNIQUE ("season_id", "puuid", "platform");
#                 ---ALTER TABLE "wrs_api_summoneroverview" 
#                 ---    ADD CONSTRAINT "wrs_api_summonerover_platform_99315587_fk_wrs_api_p" FOREIGN KEY ("platform") REFERENCES "wrs_api_platform" ("code") DEFERRABLE INITIALLY DEFERRED;

#                 CREATE TABLE wrs_api_summoneroverview_na1 PARTITION OF wrs_api_summoneroverview FOR VALUES IN ('na1');
#                 CREATE TABLE wrs_api_summoneroverview_euw1 PARTITION OF wrs_api_summoneroverview FOR VALUES IN ('euw1');
#                 CREATE TABLE wrs_api_summoneroverview_br1 PARTITION OF wrs_api_summoneroverview FOR VALUES IN ('br1');

#                 -- ALTER TABLE "wrs_api_summoneroverview" ADD CONSTRAINT "wrs_api_summonerover_season_id_4cf689b6_fk_wrs_api_s" FOREIGN KEY ("puuid") REFERENCES "wrs_api_season" ("id") DEFERRABLE INITIALLY DEFERRED;
#                 -- ALTER TABLE "wrs_api_summoneroverview" ADD CONSTRAINT "wrs_api_summonerover_summoner_id_4f6afb74_fk_wrs_api_s" FOREIGN KEY ("summoner_id") REFERENCES "wrs_api_summoner" ("id") DEFERRABLE INITIALLY DEFERRED;

#                 CREATE INDEX "wrs_api_summoneroverview_platform_99315587" ON "wrs_api_summoneroverview" ("platform");

#                 CREATE INDEX "wrs_api_summoneroverview_platform_99315587_like" ON "wrs_api_summoneroverview" ("platform" varchar_pattern_ops);

#                 -- CREATE INDEX "wrs_api_summoneroverview_season_id_4cf689b6" ON "wrs_api_summoneroverview" ("season_id");

#                 CREATE INDEX "wrs_api_summoneroverview_summoner_id_4f6afb74" ON "wrs_api_summoneroverview" ("puuid");
#             """
#         ),
#         migrations.RunSQL(
#             """
#             --- belongs to queue, patch, season, platform
#             ---partioned on platform
#                 CREATE TABLE "wrs_api_match" (
#                     "id" SERIAL NOT NULL,
#                     "matchId" varchar(20) NOT NULL, 
#                     "queueId" integer NOT NULL, 
#                     "season_id" bigint NOT NULL,
#                     "patch_id" varchar(25) NOT NULL, 
#                     "platform" varchar NOT NULL, 
#                     "metadata" jsonb NOT NULL, 
#                     PRIMARY KEY ("platform", "matchId"),
#                     FOREIGN KEY ("queueId") REFERENCES wrs_api_gamemode ("queueId") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("patch_id") REFERENCES wrs_api_patch ("full_version") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("season_id") REFERENCES wrs_api_season ("id") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                     FOREIGN KEY ("platform") REFERENCES "wrs_api_platform" ("code") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED
#                 ) PARTITION BY LIST ("platform");


#                 CREATE TABLE wrs_api_match_na1 PARTITION OF wrs_api_match FOR VALUES IN ('na1');
#                 CREATE TABLE wrs_api_match_euw1 PARTITION OF wrs_api_match FOR VALUES IN ('euw1');
#                 CREATE TABLE wrs_api_match_br1 PARTITION OF wrs_api_match FOR VALUES IN ('br1');

#                 CREATE INDEX "wrs_api_match_patch_id_0b245097" ON "wrs_api_match" ("patch_id");
#                 CREATE INDEX "wrs_api_match_patch_id_0b245097_like" ON "wrs_api_match" ("patch_id" varchar_pattern_ops);
#                 CREATE INDEX "wrs_api_match_platform_2b2c1736" ON "wrs_api_match" ("platform");
#                 CREATE INDEX "wrs_api_match_platform_2b2c1736_like" ON "wrs_api_match" ("platform" varchar_pattern_ops);
#                 CREATE INDEX "wrs_api_match_queueId_id_28ffec5b" ON "wrs_api_match" ("queueId");
#                 CREATE INDEX "wrs_api_match_season_id_996a93bd" ON "wrs_api_match" ("season_id");

#             """
#         ),
#         migrations.RunSQL(
#             """
#             CREATE TABLE "wrs_api_match_summoners" (
#                 ---"id" bigint NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY, 
#                 "id" SERIAL NOT NULL,
#                 "matchId" varchar(20) NOT NULL, 
#                 "puuid" varchar(100) NOT NULL,
#                 "platform" varchar NOT NULL,
#                 FOREIGN KEY ("platform", "matchId") REFERENCES wrs_api_match ("platform", "matchId") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                 FOREIGN KEY ("platform", "puuid") REFERENCES wrs_api_summoner ("platform", "puuid") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                 FOREIGN KEY ("platform") REFERENCES "wrs_api_platform" ("code") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
#                 CONSTRAINT "wrs_api_match_summoners_matchId_puuid_id_33a445ac_uniq" UNIQUE ("matchId", "puuid", "platform"),
#                 PRIMARY KEY ("platform", "matchId", "puuid")
#             ) PARTITION BY LIST (platform);

            
#             ---ALTER TABLE "wrs_api_match_summoners" 
#             ---    ADD CONSTRAINT "wrs_api_match_summoners_matchId_puuid_id_33a445ac_uniq" 
#             ---    UNIQUE ("matchId", "puuid", "platform");

#             CREATE TABLE wrs_api_match_summoners_na1 PARTITION OF wrs_api_match_summoners FOR VALUES IN ('na1');
#             CREATE TABLE wrs_api_match_summoners_euw1 PARTITION OF wrs_api_match_summoners FOR VALUES IN ('euw1');
#             CREATE TABLE wrs_api_match_summoners_kr1 PARTITION OF wrs_api_match_summoners FOR VALUES IN ('br1');

#             CREATE INDEX "wrs_api_match_summoners_matchId_d9b8b076" ON "wrs_api_match_summoners" ("matchId");
#             CREATE INDEX "wrs_api_match_summoners_puuid_1a034af0" ON "wrs_api_match_summoners" ("puuid");
#              """
#         ),
#     ]
