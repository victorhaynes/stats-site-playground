# from .models import Summoner, Season, SummonerOverview, MatchHistory, MatchDetails
# from .serializers import  SummonerSerializer, SummonerOverviewSerializer, MatchHistorySerializer, MatchDetailsSerializer, SeasonSerializer
from .models import Summoner, SummonerOverview, Platform, Season, Patch, Region, GameMode, Champion, Item, CompletedBoot, Match, SummonerMatch
from django.db import connection, transaction
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited
from django.db.utils import DatabaseError
from .serializers import SummonerSerializer, SummonerCustomSerializer, SummonerOverviewSerializer
from .utilities import dictfetchall, ranked_badge, calculate_average_elo, check_missing_items, RiotApiError, RiotRateLimitApiError, test_rate_limit_key
from functools import wraps
from django.forms.models import model_to_dict
from django_redis import get_redis_connection
from django.core.cache import cache
from .rate_limiter import rate_limited_RIOT_get
# from django.views.decorators.cache import cache_page
import pprint
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
import requests
from requests.exceptions import HTTPError
from dotenv import load_dotenv
import time
import os
import ast
import json
import time
import httpx
import asyncio



#################################################################################
################################################################################# Factor current_season into approp places
### Config ###################################################################### Update season offsets in .env so it'll change automatically
load_dotenv()
riot_key = os.environ["RIOT_KEY"]
headers = {'X-Riot-Token': riot_key}
try:
    current_season = Season.objects.get(season=os.environ["CURRENT_SEASON"], split=os.environ["CURRENT_SPLIT"])
except Exception as error:
    print("Admin must create season records in database." + repr(error))
season_schedule = json.loads(os.environ["SEASON_SCHEDULE"])



def check_timeout(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if the key "429" exists in the Redis cache
        redis_conn = get_redis_connection("default")
        timeout_timer = redis_conn.ttl(":1:429")
        if timeout_timer > 0:
            # If the key exists, return error JSON
            return JsonResponse({"error": f"Too Many Requests. Retry in {timeout_timer}"}, status=429)

        # If the key does not exist, let the function run as normal
        # Note this does not preempt getting a rate limit inside of a loop
        # If that happens a 403 will be returned by django_ratelimit, handle that in client
        return view_func(request, *args, **kwargs)

    return _wrapped_view


#################################################################################
#################################################################################
#################################################################################



######################################################################################
# Helper Function to check database for existing summoner data before hitting Riot API # special text index on gamename and tagline?
######################################################################################
@check_timeout
@api_view(['GET'])
def get_summoner(request):

    if request.query_params.get('update') == 'false' or not request.query_params.get('update'):
        try: 
            summoner = Summoner.objects.get(gameName__iexact=request.query_params.get('gameName'), tagLine__iexact=request.query_params.get('tagLine'), platform=request.query_params.get('platform'))
            if request.query_params.get('queueId') or request.query_params.get('limit'): # Limit is essentially requesting additional records for same summoner
                serialized_summoner = SummonerCustomSerializer(instance=summoner, context={'queueId': request.query_params.get('queueId'), 'limit': request.query_params.get('limit')})
            else:
                serialized_summoner = SummonerCustomSerializer(instance=summoner)
            return JsonResponse(serialized_summoner.data, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION, safe=False)
        
        except Summoner.DoesNotExist as e:
            pass # Continue and get details from Riot API
        except Exception as e:
            return JsonResponse({"message": "There was an issue searching for summoner. Please try again.", "detail": repr(e)}, status=status.HTTP_404_NOT_FOUND, safe=False)

    platform = Platform.objects.get(code=request.query_params.get('platform'))
    # Also eventually fix Flex Queue for Overview, it will be the 1st element in the json resposne if flex history exists
    # Atomically Create/Update: Summoner & SummonerOverview
    try:
        # Handle exceptions OUTSIDE the atomic block, unless it is a non-db exceptions
        with transaction.atomic():
            # GET Basic Account Details
            account_by_gameName_tagLine_url = f"https://{request.query_params.get('region')}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{request.query_params.get('gameName')}/{request.query_params.get('tagLine')}"
            response_account_details = rate_limited_RIOT_get(riot_endpoint=account_by_gameName_tagLine_url, request=request)

            # print("Get puuid success")
            puuid = response_account_details['puuid']
            # GET Encrypted Summoner ID
            encrypted_summonerID_by_puuid_url = f"https://{request.query_params.get('platform')}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
            response_summonerID = rate_limited_RIOT_get(riot_endpoint=encrypted_summonerID_by_puuid_url, request=request)
            summonerID = response_summonerID['id']
            profile_icon = response_summonerID['profileIconId']
            # Check if Summoner with this `puuid` and `platform` already exists in database, If exists and different update. Else create.
            try:
                summoner_searched = Summoner.objects.get(puuid=puuid, platform=request.query_params.get('platform'))
                if (request.query_params.get('platform').lower() != summoner_searched.platform.code.lower() or request.query_params.get('gameName').lower() != summoner_searched.gameName.lower() or request.query_params.get('tagLine').lower() != summoner_searched.tagLine.lower() or profile_icon != summoner_searched.profileIconId or summonerID != summoner_searched.encryptedSummonerId):
                    summoner_searched.custom_update(gameName=request.query_params.get('gameName'), tagLine=request.query_params.get('tagLine'), platform=platform, profileIconId=profile_icon, encryptedSummonerId=summonerID)
            
            except Summoner.DoesNotExist:
                summoner_searched = Summoner.objects.create(puuid=puuid, gameName=request.query_params.get('gameName'), tagLine=request.query_params.get('tagLine'), platform=platform, profileIconId=profile_icon, encryptedSummonerId=summonerID)


            # GET Summoner Overview / Ranked Stats / Elo
            league_elo_by_summonerID_url = f"https://{request.query_params.get('platform')}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summonerID}"
            response_overview = rate_limited_RIOT_get(riot_endpoint=league_elo_by_summonerID_url, request=request)
            
            # if response_account_details.status_code == 200:
            # Update this for FLEX and CHERRY/ARENA too
            summoner_elo = {}
            if len(response_overview) == 0:
                summoner_elo = json.dumps({"rank": "UNRANKED", "tier": "UNRANKED", "wins": 0, "losses": 0, "leaguePoints": 0})
            else:
                summoner_elo = json.dumps([d for d in response_overview if d["queueType"] == "RANKED_SOLO_5x5"][0])
            
            with connection.cursor() as cursor:
                partition_name = "_" + request.query_params.get('platform')
                formatted_table_names = [partition_name] * 1
                cursor.execute(
                """
                    INSERT INTO wrs_api_summoneroverview{} (puuid, platform, season_id, metadata, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    ON CONFLICT (puuid, season_id, platform) 
                    DO UPDATE SET 
                    metadata = EXCLUDED.metadata,
                    updated_at = EXCLUDED.updated_at;
                """.format(*formatted_table_names)
                , [summoner_searched.puuid, platform.code, current_season.id, summoner_elo])



    except RiotApiError as err:
        return JsonResponse(err.error_response, status=err.error_code, safe=False)
    except RiotRateLimitApiError as err:
        return JsonResponse(err.error_response, status=err.error_code, safe=False)
    except Exception as err:
        return JsonResponse(f"error: {repr(err)}", status=status.HTTP_500_INTERNAL_SERVER_ERROR, safe=False)

    # GET Match History and Elo/Overview of every participant in a Summoner's Match History
    try:
        with transaction.atomic():
            # GET all match IDs played for a given Summoner during this split/season
            season_split_start_epoch_seconds = season_schedule[request.query_params.get('platform')][f"season_{current_season.season}"][f"split_{current_season.split}"]["start"]
            season_split_end_epoch_seconds = season_schedule[request.query_params.get('platform')][f"season_{current_season.season}"][f"split_{current_season.split}"]["end"]

            start = 0
            count = 100 # must be <= 100
            all_matches_played = []
            while True:
                matches_url = f"https://{request.query_params.get('region')}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids/?start={start}&count={count}&startTime={season_split_start_epoch_seconds}&endTime={season_split_end_epoch_seconds}"
                response_matches = rate_limited_RIOT_get(riot_endpoint=matches_url, request=request)
                print("Got 100 Matches Successfully:", matches_url)
                if len(response_matches) > 0:
                    for match in response_matches:
                        all_matches_played.append(match)
                    start+=len(response_matches)
                else:
                    break

            print("total fetched", len(all_matches_played))
            print("newest game", all_matches_played[0])
            print("oldest game", all_matches_played[-1])

            print("!!!TESTING ONLY CHECK FOR SOME MATCHES!!!")
            all_matches_played = all_matches_played[0:5]

            # GET details for all matches fetched that are not already in database
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                        SELECT "matchId" FROM wrs_api_summonermatch WHERE platform = %s AND puuid = %s;
                    """
                , [request.query_params.get('platform'), puuid])
                rows = cursor.fetchall()

            my_matches_in_database = []
            for row in rows:
                my_matches_in_database.append(row[0])

            match_details_not_in_database = []
            for game in all_matches_played:
                if game not in my_matches_in_database:
                    try:
                        match_detail_url = f"https://{request.query_params.get('region')}.api.riotgames.com/lol/match/v5/matches/{game}"
                        response_match_detail = rate_limited_RIOT_get(riot_endpoint=match_detail_url, request=request)
                        timeline_url = f"https://{request.query_params.get('region')}.api.riotgames.com/lol/match/v5/matches/{game}/timeline"
                        timeline_response = rate_limited_RIOT_get(riot_endpoint=timeline_url, request=request)
                        print("successfully got details for:", game)
                        print("successfully got timeline for:", game)
                        match_detail = response_match_detail
                        timeline = timeline_response

                        
                        participant_elos = []
                        for participant_data in match_detail["info"]["participants"]:
                            build_path = []

                            # Map PUUID/Participant to Participant ID
                            participant_id_mapping = timeline["info"]["participants"]
                            summoner_participant_id = None
                            for player in participant_id_mapping:
                                if player["puuid"] == participant_data["puuid"]:
                                    summoner_participant_id = player["participantId"]
                                    break

                            print("participant:", summoner_participant_id, participant_data["puuid"])
                                
                            frames = timeline["info"]["frames"]
                            for frame in frames:
                                events = frame["events"]

                                for event in events:
                                    try:
                                        if event["participantId"] == summoner_participant_id and event["type"] == "ITEM_PURCHASED":
                                            build_path.append({"itemId": event["itemId"], "timestamp": event["timestamp"]})
                                    except KeyError:
                                        pass
                            participant_data["buildPath"] = build_path

                            participant_profile = Summoner.objects.filter(puuid=participant_data["puuid"], platform=request.query_params.get('platform'))
                            print("looking up player", participant_data["puuid"])
                            # If not found, GET details externally
                            if len(participant_profile) == 0:
                                # GET Encrypted Summoner ID externally
                                print("Not in database. Getting ESID from Riot API for:", participant_data["puuid"])
                                encrypted_summonerID_by_puuid_url = f"https://{request.query_params.get('platform')}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{participant_data['puuid']}"
                                response_summonerID = rate_limited_RIOT_get(riot_endpoint=encrypted_summonerID_by_puuid_url, request=request)
                                print("ESID STATUS CODE OKAY")

                                participant_summonerID = response_summonerID['id']
                                participant_profile_icon = response_summonerID['profileIconId']
                                participant_stats = [d for d in match_detail["info"]["participants"] if d.get("puuid") == participant_data["puuid"]][0] 
                                participant_gameName = participant_stats["riotIdGameName"]
                                participant_tagLine = participant_stats["riotIdTagline"]
                                new_summoner = Summoner.objects.create(puuid=participant_data["puuid"], gameName=participant_gameName, tagLine=participant_tagLine, platform=platform, profileIconId=participant_profile_icon, encryptedSummonerId=participant_summonerID)

                                # GET Summoner Overview / Ranked Stats / Elo
                                print("Getting ELO update for:", participant_data["puuid"])
                                league_elo_by_summonerID_url = f"https://{request.query_params.get('platform')}.api.riotgames.com/lol/league/v4/entries/by-summoner/{participant_summonerID}"
                                response_overview = rate_limited_RIOT_get(riot_endpoint=league_elo_by_summonerID_url, request=request)
                                print("RANKED ELO STATUS CODE OKAY")

                                # if response_account_details.status_code == 200:
                                participant_elo = {}
                                if len(response_overview) == 0:
                                    participant_elo = json.dumps({"rank": "UNRANKED", "tier": "UNRANKED", "wins": 0, "losses": 0, "leaguePoints": 0})
                                else:
                                    try:
                                        participant_elo = json.dumps([d for d in response_overview if d["queueType"] == "RANKED_SOLO_5x5"][0])
                                    except IndexError: # Only plays flex queue and never ranked
                                        participant_elo = json.dumps({"rank": "UNRANKED", "tier": "UNRANKED", "wins": 0, "losses": 0, "leaguePoints": 0})


                                elo = {"puuid": participant_data["puuid"], "tier": json.loads(participant_elo)["tier"], "rank": json.loads(participant_elo)["rank"]}
                                elo = ranked_badge(elo)
                                participant_elos.append(elo)
                                participant_data["summonerElo"] = elo

                                with connection.cursor() as cursor:
                                    print("Inserting overview for:", participant_data["puuid"])
                                    partition_name = "_" + request.query_params.get('platform')
                                    formatted_table_names = [partition_name] * 1
                                    cursor.execute(
                                    """
                                        INSERT INTO wrs_api_summoneroverview{} (puuid, platform, season_id, metadata, created_at, updated_at)
                                        VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                                        ON CONFLICT (puuid, season_id, platform) 
                                        DO UPDATE SET 
                                        metadata = EXCLUDED.metadata,
                                        updated_at = EXCLUDED.updated_at;
                                    """.format(*formatted_table_names)
                                    , [participant_data["puuid"], platform.code, current_season.id, participant_elo])

                            # If summoner exists, get current elo from database
                            else:
                                with connection.cursor() as cursor:
                                    partition_name = "_" + request.query_params.get('platform')
                                    formatted_table_names = [partition_name] * 1
                                    cursor.execute(
                                        """
                                            SELECT * FROM wrs_api_summoneroverview{} WHERE puuid = %s AND platform = %s
                                            ORDER BY id DESC;
                                        """.format(*formatted_table_names)
                                        ,[participant_data["puuid"], request.query_params.get('platform')])
                                    results = dictfetchall(cursor)
                                ov = json.loads(results[0]["metadata"])

                                elo = {"puuid": participant_data["puuid"], "tier": ov["tier"], "rank": ov["rank"]}
                                elo = ranked_badge(elo)
                                participant_elos.append(elo)
                                participant_data["summonerElo"] = elo

                        match_detail["participantElos"] = participant_elos
                        average_elo = calculate_average_elo(participant_elos, match_detail["info"]["queueId"])
                        match_detail["averageElo"] = average_elo
                        match_details_not_in_database.append(match_detail)
                                
                    except RiotRateLimitApiError:
                        break
                else:
                    print("skipped:", game, "already found")
                    pass


            print(len(match_details_not_in_database))
            if len(match_details_not_in_database) > 0:
                for d in match_details_not_in_database:
                    print(d["metadata"]["matchId"], "not in db")


            for match_detail in match_details_not_in_database:
                with connection.cursor() as cursor:
                    
                    print("Begin iteration for  match:", match_detail["metadata"]["matchId"])
                    split_version = match_detail["info"]["gameVersion"].split('.',1)
                    version = (split_version[0] + "." + split_version[1].split('.',1)[0])
                    patch_tuple = Patch.objects.get_or_create(full_version=match_detail["info"]["gameVersion"], version=version, season_id=current_season)
                    print("Created new patch:", patch_tuple[1])

                    partition_name = "_" + request.query_params.get('platform')
                    formatted_table_names = [partition_name] * 1
                    print("attempting to write match:", match_detail["metadata"]["matchId"], "to table")
                    cursor.execute(
                        """
                            INSERT INTO wrs_api_match{} ("matchId", "queueId", "season_id", "patch", "platform", "elo", "metadata")
                            VALUES (%s, %s, %s, %s, %s, %s, %s);
                        """.format(*formatted_table_names)
                    ,[match_detail["metadata"]["matchId"], match_detail["info"]["queueId"], current_season.id, patch_tuple[0].full_version, request.query_params.get('platform'), match_detail["averageElo"], json.dumps(match_detail)])

                    # Update ban stats for banned champions for all teams ALL STATS SHOULD ONLY BE FOR RANKED 420
                    if match_detail["info"]["queueId"] == 420:
                        partition_name = "_" + request.query_params.get('platform')
                        formatted_table_names = [partition_name] * 2
                        for team in match_detail["info"]["teams"]:
                            bans = team["bans"]
                            for ban in bans:
                                ban_increment = 1
                                cursor.execute(
                                    """
                                        INSERT INTO wrs_api_banstat{} ("championId", "elo", "banned", "season_id", "patch", "platform")
                                        VALUES (%s, %s, %s, %s, %s, %s)
                                        ON CONFLICT ("platform","championId", "patch", "elo", "season_id")
                                        DO UPDATE SET 
                                        banned = wrs_api_banstat{}.banned + EXCLUDED.banned;
                                    """.format(*formatted_table_names)
                                ,[ban["championId"], match_detail["averageElo"], ban_increment, current_season.id, patch_tuple[0].full_version, request.query_params.get('platform')])
                                print("Updated ban for", ban["championId"])

                    
                    # participants = match_detail["metadata"]["participants"]
                    participants = match_detail["info"]["participants"]
                    for participant_object in participants:
                        partition_name = "_" + request.query_params.get('platform')
                        formatted_table_names = [partition_name] * 1
                        cursor.execute(
                            """
                                INSERT INTO wrs_api_summonermatch{} ("matchId", "elo", "queueId", "puuid", "season_id", "patch", "platform")
                                VALUES (%s, %s, %s, %s, %s, %s, %s);
                            """.format(*formatted_table_names)
                        # ,[match_detail["metadata"]["matchId"], match_detail["averageElo"], match_detail["info"]["queueId"], participant_puuid, current_season.id, patch_tuple[0].full_version, request.query_params.get('platform')])
                        ,[match_detail["metadata"]["matchId"], match_detail["averageElo"], match_detail["info"]["queueId"], participant_object["puuid"], current_season.id, patch_tuple[0].full_version, request.query_params.get('platform')])

                        if match_detail["info"]["queueId"] == 420:
                            win = participant_object["win"]
                            remake = participant_object["gameEndedInEarlySurrender"]
                            if remake:
                                win_increment = 0
                                loss_increment = 0
                            elif win:
                                win_increment = 1
                                loss_increment = 0
                            else:
                                win_increment = 0
                                loss_increment = 1
                            pick_increment = 1

                            partition_name = "_" + request.query_params.get('platform')
                            formatted_table_names = [partition_name] * 4
                            cursor.execute(
                                """
                                    INSERT INTO wrs_api_championstat{} ("championId", "role", "elo", "wins", "losses", "picked", "season_id", "patch", "platform")
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                                    ON CONFLICT ("platform","championId", "patch", "role", "elo", "season_id")
                                    DO UPDATE SET 
                                    wins = wrs_api_championstat{}.wins + EXCLUDED.wins,
                                    losses = wrs_api_championstat{}.losses + EXCLUDED.losses,
                                    picked = wrs_api_championstat{}.picked + EXCLUDED.picked;
                                """.format(*formatted_table_names)
                            ,[participant_object["championId"],  participant_object["teamPosition"], match_detail["averageElo"], win_increment, loss_increment, pick_increment, current_season.id, patch_tuple[0].full_version, request.query_params.get('platform')])

                            # Write Rune Page Stats Logic
                            runes_in_order = []
                            for style in participant_object["perks"]["styles"]:
                                for selection in style["selections"]:
                                    runes_in_order.append(selection["perk"])
                            shard1 = participant_object["perks"]["statPerks"]["offense"]
                            shard2 = participant_object["perks"]["statPerks"]["flex"]
                            shard3 = participant_object["perks"]["statPerks"]["defense"]

                            partition_name = "_" + request.query_params.get('platform')
                            formatted_table_names = [partition_name] * 3
                            cursor.execute(
                                """
                                    INSERT INTO wrs_api_runepagestat{} ("keystone", "primary_one", "primary_two", "primary_three", "secondary_one", "secondary_two", "shard_one", "shard_two", "shard_three", "championId", "elo", "role", "wins", "losses", "picked", "season_id", "patch", "platform")
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                    ON CONFLICT ("keystone", "primary_one", "primary_two", "primary_three", "secondary_one", "secondary_two", "shard_one", "shard_two", "shard_three", "championId", "platform", "patch", "role", "elo", "season_id")
                                    DO UPDATE SET 
                                    wins = wrs_api_runepagestat{}.wins + EXCLUDED.wins,
                                    losses = wrs_api_runepagestat{}.losses + EXCLUDED.losses;
                                """.format(*formatted_table_names)
                            ,[runes_in_order[0], runes_in_order[1], runes_in_order[2], runes_in_order[3], runes_in_order[4], runes_in_order[5], shard1, shard2, shard3, participant_object["championId"], match_detail["averageElo"], participant_object["teamPosition"], win_increment, loss_increment, pick_increment, current_season.id, patch_tuple[0].full_version, request.query_params.get('platform')])
                            print("pass4")


                            # Legendary Item Stats writing logic 
                            legendary_items_built_by_player = participant_object["challenges"]["legendaryItemUsed"]

                            
                            cleaned_item_build = check_missing_items(legendary_items_built_by_player)
                            partition_name = "_" + request.query_params.get('platform')
                            formatted_table_names = [partition_name] * 3
                            if cleaned_item_build[0] != -1: # If the first item built is a real item (not dummy -1) write entire build to table
                                cursor.execute(
                                    """
                                        INSERT INTO wrs_api_itembuildstat{} ("legendary_one", "legendary_two", "legendary_three", "legendary_four", "legendary_five", "legendary_six", "championId", "elo", "role", "wins", "losses", "season_id", "patch", "platform")
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                        ON CONFLICT ("legendary_one", "legendary_two", "legendary_three", "legendary_four", "legendary_five", "legendary_six", "championId", "platform", "patch", "role", "elo", "season_id")
                                        DO UPDATE SET 
                                        wins = wrs_api_itembuildstat{}.wins + EXCLUDED.wins,
                                        losses = wrs_api_itembuildstat{}.losses + EXCLUDED.losses;
                                    """.format(*formatted_table_names)
                                ,[cleaned_item_build[0], cleaned_item_build[1], cleaned_item_build[2], cleaned_item_build[3], cleaned_item_build[4], cleaned_item_build[5], participant_object["championId"], match_detail["averageElo"], participant_object["teamPosition"], win_increment, loss_increment, current_season.id, patch_tuple[0].full_version, request.query_params.get('platform')])
                            print("pass5")

                            # Tier Two Boots Stats writing logic 
                            boots_built_by_player = []
                            all_completed_boots = list(CompletedBoot.objects.values_list('itemId', flat=True))
                            for item_built in participant_object["buildPath"]:
                                if item_built["itemId"] in all_completed_boots:
                                    boots_built_by_player.append(item_built["itemId"])
                            
                            
                            partition_name = "_" + request.query_params.get('platform')
                            formatted_table_names = [partition_name] * 3

                            if boots_built_by_player:
                                bootId = boots_built_by_player[0] # Get the first tier two boot built, players sometimes sell and buy a different pair
                                cursor.execute(
                                    """
                                        INSERT INTO wrs_api_completedbootstat{} ("completed_boot","championId", "elo", "role", "wins", "losses", "season_id", "patch", "platform")
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                                        ON CONFLICT ("platform", "completed_boot", "championId","patch", "role", "elo", "season_id")
                                        DO UPDATE SET 
                                        wins = wrs_api_completedbootstat{}.wins + EXCLUDED.wins,
                                        losses = wrs_api_completedbootstat{}.losses + EXCLUDED.losses;
                                    """.format(*formatted_table_names)
                                ,[bootId, participant_object["championId"], match_detail["averageElo"], participant_object["teamPosition"], win_increment, loss_increment, current_season.id, patch_tuple[0].full_version, request.query_params.get('platform')])
                            print("pass6")

                            partition_name = "_" + request.query_params.get('platform')
                            formatted_table_names = [partition_name] * 4
                            # Summoner Spell writing logi
                            spell_one = participant_object["summoner1Id"]
                            spell_two = participant_object["summoner2Id"]                                 
                            cursor.execute(
                                """
                                    INSERT INTO wrs_api_summonerspellstat{} ("spell_one", "spell_two", "championId", "elo", "role", "wins", "losses", "picked", "season_id", "patch", "platform")
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                    ON CONFLICT ("platform", "spell_one", "spell_two", "championId","patch", "role", "elo", "season_id")
                                    DO UPDATE SET 
                                    wins = wrs_api_summonerspellstat{}.wins + EXCLUDED.wins,
                                    losses = wrs_api_summonerspellstat{}.losses + EXCLUDED.losses,
                                    picked = wrs_api_summonerspellstat{}.picked + EXCLUDED.picked;
                                """.format(*formatted_table_names)
                            ,[spell_one, spell_two, participant_object["championId"], match_detail["averageElo"], participant_object["teamPosition"], win_increment, loss_increment, pick_increment, current_season.id, patch_tuple[0].full_version, request.query_params.get('platform')])

            with connection.cursor() as cursor:
                partition_name = "_" + request.query_params.get('platform')
                formatted_table_names = [partition_name] * 4
                cursor.execute(
                    """
                        SELECT "matchId" FROM wrs_api_summonermatch{} WHERE wrs_api_summonermatch{}.puuid = %s AND wrs_api_summonermatch{}.platform = %s
                        ORDER BY wrs_api_summonermatch{}."matchId" DESC
                        LIMIT 1;
                    """.format(*formatted_table_names)
                ,[puuid, request.query_params.get('platform')])
                result = cursor.fetchone()
                if result is not None:
                    last_saved_game = result[0]
                    if summoner_searched.most_recent_game != last_saved_game:
                        summoner_searched.custom_update(most_recent_game=last_saved_game)
                    print(last_saved_game)

    except RiotApiError as err:
        return JsonResponse(err.error_response, status=err.error_code, safe=False)
    except Exception as err:
        return JsonResponse(f"Could not update databse. Error: {str(err)}", safe=False, status=status.HTTP_409_CONFLICT)

        
    summoner_searched = Summoner.objects.get(puuid=puuid, platform=request.query_params.get('platform'))
    serialized_summoner = SummonerCustomSerializer(summoner_searched)

    return JsonResponse(serialized_summoner.data, safe=False, status=status.HTTP_202_ACCEPTED)



######################################################################################
# Get all Challenger Players for a PLATFORM and TIER (300 Challengers for NA1)
######################################################################################
@api_view(['GET'])
@transaction.atomic
def get_ranked_ladder(request):
    # redis_conn = get_redis_connection("default")
    # cached_ladder = redis_conn.get(f"{request.query_params.get('platform')}_ladder")


    # UPDATE THIS SO IT WORKS FOR TIERS !!!!!!!!!!!!!!

    cached_ladder = cache.get(f"{request.query_params.get('platform')}_{request.query_params.get('tier')}_ladder")

    if cached_ladder:
        summoners = json.loads(cached_ladder)
        http_status_code = status.HTTP_208_ALREADY_REPORTED

    else: 
        try:
            platform = Platform.objects.get(code=request.query_params.get('platform'))

            url_page1 = f'https://{request.query_params.get("platform")}.api.riotgames.com/lol/league-exp/v4/entries/RANKED_SOLO_5x5/CHALLENGER/I?page=1'
            url_page2 = f'https://{request.query_params.get("platform")}.api.riotgames.com/lol/league-exp/v4/entries/RANKED_SOLO_5x5/CHALLENGER/I?page=2'

            challenger_page1_response = requests.get(url_page1, headers=headers, verify=True)
            challenger_page2_response = requests.get(url_page2, headers=headers, verify=True)
            print("Got all challenger players OK")
            page1 = challenger_page1_response.json()
            page2 = challenger_page2_response.json()
            challenger_players = page1 + page2
            challenger_players = challenger_players[:25]

            summoners = []
            for player_overview in challenger_players:
                print("attempting for player:", player_overview["summonerId"])
                try:
                    existing_challenger = Summoner.objects.get(encryptedSummonerId=player_overview["summonerId"], platform=platform)
                    print("FOUND! UPDATING OVERVIW")
                    # The above is not necessarily optimal, you will fail foreign key constraint if summoner doesn't exist we don't need to check
                    # but remain now for simplcity
                    with connection.cursor() as cursor:
                        cursor.execute(
                        """
                            INSERT INTO wrs_api_summoneroverview (puuid, platform, season_id, metadata, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                            ON CONFLICT (puuid, season_id, platform) 
                            DO UPDATE SET 
                            metadata = EXCLUDED.metadata,
                            updated_at = EXCLUDED.updated_at;
                        """
                        , [existing_challenger.puuid, request.query_params.get('platform'), current_season.id, json.dumps(player_overview)])

                    updated_summoner = model_to_dict(existing_challenger)
                    updated_summoner["metadata"] = player_overview
                    summoners.append(updated_summoner)

                except Summoner.DoesNotExist:
                    print("NOT FOUND! FETCHING DETAILS OVERVIW")
                    # GET PUUID from Encrypted summonerId / list of Challenger Players
                    encrypted_sum_id_to_puuid_url = f"https://{request.query_params.get('platform')}.api.riotgames.com/lol/summoner/v4/summoners/{player_overview['summonerId']}"            
                    puuid_details_response = requests.get(encrypted_sum_id_to_puuid_url, headers=headers, verify=True)
                    if puuid_details_response.status_code == 200:
                        print("success ONE")
                        data = puuid_details_response.json()
                        puuid = data["puuid"]
                        profileIconId = data["profileIconId"]
                    else:
                        # return JsonResponse({"Riot API returned error": puuid_details_response.status_code, "message": puuid_details_response.json(), "meta": 523}, status=puuid_details_response.status_code)
                        error_message = puuid_details_response.json()["status"]["message"]
                        raise RiotApiError(int(puuid_details_response.status_code), error_message)
                    
                    # Get Display Name from PUUID
                    puuid_to_display_name_url = f"https://{request.query_params.get('region')}.api.riotgames.com/riot/account/v1/accounts/by-puuid/{puuid}"
                    display_name_details = requests.get(puuid_to_display_name_url, headers=headers, verify=True)
                    if display_name_details.status_code == 200:
                        print("success TWO")
                        data = display_name_details.json()
                        gameName = data["gameName"]
                        tagLine = data["tagLine"]
                        print("parsed successfully")
                    else:
                        # return JsonResponse({"Riot API returned error": display_name_details.status_code, "message": display_name_details.json(), "meta": 531}, status=display_name_details.status_code)
                        error_message = display_name_details.json()["status"]["message"]
                        raise RiotApiError(int(display_name_details.status_code), error_message)

                    print("check here")
                    # Write New Player to database
                    challenger_player = Summoner.objects.create(puuid=puuid, gameName=gameName, tagLine=tagLine, platform=platform, profileIconId=profileIconId, encryptedSummonerId=player_overview["summonerId"])
                    print("challenger saved to db")
                    # account_by_gameName_tagLine_url = f"https://{request.query_params.get('region')}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{request.query_params.get('gameName')}/{request.query_params.get('tagLine')}"
                    # response_account_details = requests.get(account_by_gameName_tagLine_url, headers=headers, verify=True)

                        
                    # Write Summoner Overview / Ranked Stats / Elo
                    # league_elo_by_summonerID_url = f"https://{request.query_params.get('platform')}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summonerID}"
                    # response_overview = requests.get(league_elo_by_summonerID_url, headers=headers, verify=True)
                    
                # if display_name_details.status_code == 200:
                    print("WRITING OVERVIEW FOR", player_overview["summonerId"])
                    with connection.cursor() as cursor:
                        cursor.execute(
                        """
                            INSERT INTO wrs_api_summoneroverview (puuid, platform, season_id, metadata, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                            ON CONFLICT (puuid, season_id, platform) 
                            DO UPDATE SET 
                            metadata = EXCLUDED.metadata,
                            updated_at = EXCLUDED.updated_at;
                        """
                        , [challenger_player.puuid, request.query_params.get('platform'), current_season.id, json.dumps(player_overview)])
                    print("Wrote successfully")

                # else:
                #     # return JsonResponse({"Riot API returned error": response_account_details.status_code, "message": response_account_details.json(), "meta": 143}, status=response_account_details.status_code)   
                #     error_message = response_account_details.json()["status"]["message"]
                #     raise RiotApiError(int(response_account_details.status_code), error_message)

                    updated_summoner = model_to_dict(challenger_player)
                    updated_summoner["metadata"] = player_overview
                    summoners.append(updated_summoner)

            cache.set(f"{request.query_params.get('platform')}_{request.query_params.get('tier')}_ladder", json.dumps(summoners), timeout=3600)
            # redis_conn.set(f"{request.query_params.get('platform')}_ladder", json.dumps(summoners), ex=3600)
            http_status_code = status.HTTP_201_CREATED


        except RiotApiError as err:
            print("here1", err)
            print("here2", err.as_dict())
            return JsonResponse(err.as_dict(), status=err.largest_code(), safe=False)

    return JsonResponse(summoners, safe=False, status=http_status_code)

