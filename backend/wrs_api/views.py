# from .models import Summoner, Season, SummonerOverview, MatchHistory, MatchDetails
# from .serializers import  SummonerSerializer, SummonerOverviewSerializer, MatchHistorySerializer, MatchDetailsSerializer, SeasonSerializer
from .models import Summoner, SummonerOverview, Platform, Season, Patch, Region, GameMode, Champion, Item, CompletedBoot, Match, SummonerMatch
from django.db import connection, transaction, IntegrityError
import psycopg2
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited
from django.db.utils import DatabaseError
from .serializers import SummonerSerializer, SummonerCustomSerializer, SummonerOverviewSerializer
from .utilities import dictfetchall, ranked_badge, calculate_average_elo, check_missing_items, RiotApiError, RiotApiRateLimitError, test_rate_limit_key
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

# def custom403handler(request, exception=None): // Not needed?
#     print("custom handler was hit")
#     if isinstance(exception, Ratelimited):
#         return JsonResponse("WR.GG Enforcing rate limit", safe=False, status=429)
#     return JsonResponse("Forbidden", safe=False, status=403)


# Check if my rate limiter failed to prevent any 429s recently OR if Riot issues a Service Rate Limit for all external apps
def check_riot_enforced_timeout(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if the key "429" exists in the Redis cache
        redis_conn = get_redis_connection("default")
        timeout_timer = redis_conn.ttl(":1:429")
        error_message = {
                            "status": {
                                "status_code": 429,
                                "message": f"Rate Limited by Riot. Retry in {timeout_timer}",
                                "retry_after": int(timeout_timer)
                            }
                        }
        if timeout_timer > 0:
            # If the key exists, return error JSON
            return JsonResponse(error_message, status=429)

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
@check_riot_enforced_timeout
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
            return JsonResponse({f"Error: There was an issue searching for summoner. Please try again. Detail: {repr(e)}"}, status=status.HTTP_404_NOT_FOUND, safe=False)

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
            gameName = response_account_details["gameName"]
            tagLine = response_account_details["tagLine"]
            # GET Encrypted Summoner ID
            encrypted_summonerID_by_puuid_url = f"https://{request.query_params.get('platform')}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
            response_summonerID = rate_limited_RIOT_get(riot_endpoint=encrypted_summonerID_by_puuid_url, request=request)
            summonerID = response_summonerID['id']
            profile_icon = response_summonerID['profileIconId']
            # Check if Summoner with this `puuid` and `platform` already exists in database, If exists and different update. Else create.
            try:
                summoner_searched = Summoner.objects.get(puuid=puuid, platform=request.query_params.get('platform'))
                if (request.query_params.get('platform').lower() != summoner_searched.platform.code.lower() or gameName.lower() != summoner_searched.gameName.lower() or tagLine.lower() != summoner_searched.tagLine.lower() or profile_icon != summoner_searched.profileIconId or summonerID != summoner_searched.encryptedSummonerId):
                    summoner_searched.custom_update(gameName=gameName, tagLine=tagLine, platform=platform, profileIconId=profile_icon, encryptedSummonerId=summonerID)
            
            except Summoner.DoesNotExist:
                summoner_searched = Summoner.objects.create(puuid=puuid, gameName=gameName, tagLine=tagLine, platform=platform, profileIconId=profile_icon, encryptedSummonerId=summonerID)


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
    except RiotApiRateLimitError as err:
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
            all_matches_played = all_matches_played[0:2]

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
                                        INSERT INTO wrs_api_summoneroverview (puuid, platform, season_id, metadata, created_at, updated_at)
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
                                            SELECT * FROM wrs_api_summoneroverview WHERE puuid = %s AND platform = %s
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
                                
                    except RiotApiRateLimitError:
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
                    # Write match to wrs_api_match
                    cursor.execute(
                        """
                            DO $$
                            DECLARE
                                v_match_id TEXT;
                                v_queue_id INTEGER;
                                v_season_id INTEGER;
                                v_patch TEXT;
                                v_platform TEXT;
                                v_elo TEXT;
                                v_metadata JSONB;
                            BEGIN
                                v_match_id := %s;
                                v_queue_id := %s;
                                v_season_id := %s;
                                v_patch := %s;
                                v_platform := %s;
                                v_elo := %s;
                                v_metadata := %s::JSONB;

                                -- Set all constraints to immediate check, foreign key constraints are deffered and won't trigger exception handling
                                SET CONSTRAINTS ALL IMMEDIATE;

                                -- Attempt insertion into wrs_api_match
                                BEGIN
                                    INSERT INTO wrs_api_match ("matchId", "queueId", "season_id", "patch", "platform", "elo", "metadata")
                                    VALUES (v_match_id, v_queue_id, v_season_id, v_patch, v_platform, v_elo, v_metadata);

                                EXCEPTION
                                    WHEN foreign_key_violation THEN
                                        -- Handle the foreign key violation
                                        RAISE NOTICE 'Queue id %% does not exist. Must insert: %%', v_queue_id, SQLERRM;

                                        -- Write referenced row to wrs_api_gamemode
                                        INSERT INTO wrs_api_gamemode ("queueId", "name")
                                        VALUES (v_queue_id, NULL)
                                        ON CONFLICT ("queueId") DO NOTHING;

                                        -- Retry the insert into wrs_api_match
                                        INSERT INTO wrs_api_match ("matchId", "queueId", "season_id", "patch", "platform", "elo", "metadata")
                                        VALUES (v_match_id, v_queue_id, v_season_id, v_patch, v_platform, v_elo, v_metadata);   
                                END;
                            END $$;                           
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
                                        DO $$
                                        DECLARE
                                            v_champion_id INTEGER;
                                            v_elo TEXT;
                                            v_banned INTEGER;
                                            v_season_id INTEGER;
                                            v_patch TEXT;
                                            v_platform TEXT;
                                        BEGIN
                                            v_champion_id := %s;
                                            v_elo := %s;
                                            v_banned := %s;
                                            v_season_id := %s;
                                            v_patch := %s;
                                            v_platform := %s;

                                            -- Set all constraints to immediate check, foreign key constraints are deffered and won't trigger exception handling
                                            SET CONSTRAINTS ALL IMMEDIATE;

                                            -- Attempt insertion into wrs_api_banstat
                                            BEGIN
                                                INSERT INTO wrs_api_banstat ("championId", "elo", "banned", "season_id", "patch", "platform")
                                                VALUES (v_champion_id, v_elo, v_banned, v_season_id, v_patch, v_platform)
                                                ON CONFLICT ("platform", "championId", "patch", "elo", "season_id")
                                                DO UPDATE SET 
                                                banned = wrs_api_banstat.banned + EXCLUDED.banned;
                                            EXCEPTION
                                                WHEN foreign_key_violation THEN
                                                    -- Handle the foreign key violation
                                                    RAISE NOTICE 'Champion id %% does not exist. Must insert: %%', v_champion_id, SQLERRM;

                                                    -- Write referenced row to wrs_api_champion
                                                    INSERT INTO wrs_api_champion ("championId", "name", metadata)
                                                    VALUES (v_champion_id, NULL, NULL)
                                                    ON CONFLICT ("championId") DO NOTHING;

                                                    -- Retry the insert into wrs_api_banstat
                                                    INSERT INTO wrs_api_banstat ("championId", "elo", "banned", "season_id", "patch", "platform")
                                                    VALUES (v_champion_id, v_elo, v_banned, v_season_id, v_patch, v_platform)
                                                    ON CONFLICT ("platform", "championId", "patch", "elo", "season_id")
                                                    DO UPDATE SET 
                                                    banned = wrs_api_banstat.banned + EXCLUDED.banned;
                                            END;
                                        END $$;
                                    """.format(*formatted_table_names)
                                ,[ban["championId"], match_detail["averageElo"], ban_increment, current_season.id, patch_tuple[0].full_version, request.query_params.get('platform')])
                                print("Updated ban for", ban["championId"])
                                # Note: re-check the query plan and make sure we don't explictly need to include the "_<platform>" suffix
                                # if query plan is not selecting partitions optimally then pass in the table suffixes. Right now does nothing

                    
                    # participants = match_detail["metadata"]["participants"]
                    participants = match_detail["info"]["participants"]
                    for participant_object in participants:
                        print("iterating for:", participant_object["puuid"])
                        partition_name = "_" + request.query_params.get('platform')
                        formatted_table_names = [partition_name] * 1
                        cursor.execute(
                            """
                                INSERT INTO wrs_api_summonermatch ("matchId", "elo", "queueId", "puuid", "season_id", "patch", "platform")
                                VALUES (%s, %s, %s, %s, %s, %s, %s);
                            """.format(*formatted_table_names)
                        # ,[match_detail["metadata"]["matchId"], match_detail["averageElo"], match_detail["info"]["queueId"], participant_puuid, current_season.id, patch_tuple[0].full_version, request.query_params.get('platform')])
                        ,[match_detail["metadata"]["matchId"], match_detail["averageElo"], match_detail["info"]["queueId"], participant_object["puuid"], current_season.id, patch_tuple[0].full_version, request.query_params.get('platform')])

                        if match_detail["info"]["queueId"] == 420 and match_detail["info"]["endOfGameResult"] == "GameComplete": # Ranked & Not Terminated by Vanguard Anti-cheat
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
                            # Logic for champion win/loss/pick/role stat writing
                            cursor.execute(
                                """
                                DO $$
                                DECLARE
                                    v_champion_id INTEGER;
                                    v_role TEXT;
                                    v_elo TEXT;
                                    v_wins INTEGER;
                                    v_losses INTEGER;
                                    v_picked INTEGER;
                                    v_season_id INTEGER;
                                    v_patch TEXT;
                                    v_platform TEXT;
                                BEGIN
                                    v_champion_id := %s;
                                    v_role := %s;
                                    v_elo := %s;
                                    v_wins := %s;
                                    v_losses := %s;
                                    v_picked := %s;
                                    v_season_id := %s;
                                    v_patch := %s;
                                    v_platform := %s;

                                    -- Set all constraints to immediate check to ensure we catch foreign key violations immediately
                                    SET CONSTRAINTS ALL IMMEDIATE;

                                    -- Attempt insertion into wrs_api_championstat
                                    BEGIN
                                        INSERT INTO wrs_api_championstat ("championId", "role", "elo", "wins", "losses", "picked", "season_id", "patch", "platform")
                                        VALUES (v_champion_id, v_role, v_elo, v_wins, v_losses, v_picked, v_season_id, v_patch, v_platform)
                                        ON CONFLICT ("platform", "championId", "patch", "role", "elo", "season_id")
                                        DO UPDATE SET 
                                        wins = wrs_api_championstat.wins + EXCLUDED.wins,
                                        losses = wrs_api_championstat.losses + EXCLUDED.losses,
                                        picked = wrs_api_championstat.picked + EXCLUDED.picked;
                                    EXCEPTION
                                        WHEN foreign_key_violation THEN
                                            -- Handle the foreign key violation
                                            RAISE NOTICE 'Champion id %% does not exist. Must insert: %%', v_champion_id, SQLERRM;

                                            -- Write referenced row to wrs_api_champion
                                            INSERT INTO wrs_api_champion ("championId", "name", metadata)
                                            VALUES (v_champion_id, NULL, NULL)
                                            ON CONFLICT ("championId") DO NOTHING;

                                            -- Retry the insert into wrs_api_championstat
                                            INSERT INTO wrs_api_championstat ("championId", "role", "elo", "wins", "losses", "picked", "season_id", "patch", "platform")
                                            VALUES (v_champion_id, v_role, v_elo, v_wins, v_losses, v_picked, v_season_id, v_patch, v_platform)
                                            ON CONFLICT ("platform", "championId", "patch", "role", "elo", "season_id")
                                            DO UPDATE SET 
                                            wins = wrs_api_championstat.wins + EXCLUDED.wins,
                                            losses = wrs_api_championstat.losses + EXCLUDED.losses,
                                            picked = wrs_api_championstat.picked + EXCLUDED.picked;
                                    END;
                                END $$;
                                """.format(*formatted_table_names)
                            ,[participant_object["championId"],  participant_object["teamPosition"], match_detail["averageElo"], win_increment, loss_increment, pick_increment, current_season.id, patch_tuple[0].full_version, request.query_params.get('platform')])
                            print("Updated Champion Stats for:", participant_object["puuid"], "'s champion")

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
                                DO $$
                                DECLARE
                                    v_keystone INTEGER;
                                    v_primary_one INTEGER;
                                    v_primary_two INTEGER;
                                    v_primary_three INTEGER;
                                    v_secondary_one INTEGER;
                                    v_secondary_two INTEGER;
                                    v_shard_one INTEGER;
                                    v_shard_two INTEGER;
                                    v_shard_three INTEGER;
                                    v_champion_id INTEGER;
                                    v_elo TEXT;
                                    v_role TEXT;
                                    v_wins INTEGER;
                                    v_losses INTEGER;
                                    v_picked INTEGER;
                                    v_season_id INTEGER;
                                    v_patch TEXT;
                                    v_platform TEXT;
                                BEGIN
                                    v_keystone := %s;
                                    v_primary_one := %s;
                                    v_primary_two := %s;
                                    v_primary_three := %s;
                                    v_secondary_one := %s;
                                    v_secondary_two := %s;
                                    v_shard_one := %s;
                                    v_shard_two := %s;
                                    v_shard_three := %s;
                                    v_champion_id := %s;
                                    v_elo := %s;
                                    v_role := %s;
                                    v_wins := %s;
                                    v_losses := %s;
                                    v_picked := %s;
                                    v_season_id := %s;
                                    v_patch := %s;
                                    v_platform := %s;

                                    -- Set all constraints to immediate check to ensure we catch foreign key violations immediately
                                    SET CONSTRAINTS ALL IMMEDIATE;

                                    -- Attempt insertion into wrs_api_runepagestat
                                    BEGIN
                                        INSERT INTO wrs_api_runepagestat (keystone, primary_one, primary_two, primary_three, secondary_one, secondary_two, shard_one, shard_two, shard_three, "championId", elo, role, wins, losses, picked, season_id, patch, platform)
                                        VALUES (v_keystone, v_primary_one, v_primary_two, v_primary_three, v_secondary_one, v_secondary_two, v_shard_one, v_shard_two, v_shard_three, v_champion_id, v_elo, v_role, v_wins, v_losses, v_picked, v_season_id, v_patch, v_platform)
                                        ON CONFLICT (keystone, primary_one, primary_two, primary_three, secondary_one, secondary_two, shard_one, shard_two, shard_three, "championId", platform, patch, role, elo, season_id)
                                        DO UPDATE SET 
                                        wins = EXCLUDED.wins,
                                        losses = EXCLUDED.losses;
                                    EXCEPTION
                                        WHEN foreign_key_violation THEN
                                            -- Handle the foreign key violation
                                            RAISE NOTICE 'Foreign key violation caught: %%', SQLERRM;

                                            -- Write referenced rows to their respective tables and retry insertion into wrs_api_runepagestat
                                            BEGIN
                                                -- Insert into wrs_api_champion table
                                                BEGIN
                                                    INSERT INTO wrs_api_champion ("championId", "name", metadata)
                                                    VALUES (v_champion_id, NULL, NULL)
                                                    ON CONFLICT ("championId") DO NOTHING;
                                                END;
                                                -- Insert into wrs_api_keystone table
                                                BEGIN
                                                    INSERT INTO wrs_api_keystone (keystone_id, name, metadata)
                                                    VALUES (v_keystone, NULL, NULL)
                                                    ON CONFLICT (keystone_id) DO NOTHING;
                                                END;

                                                -- Insert into wrs_api_primaryperkone table
                                                BEGIN
                                                    INSERT INTO wrs_api_primaryperkone (perk_id, name, metadata)
                                                    VALUES (v_primary_one, NULL, NULL)
                                                    ON CONFLICT (perk_id) DO NOTHING;
                                                END;

                                                -- Insert into wrs_api_primaryperktwo table
                                                BEGIN
                                                    INSERT INTO wrs_api_primaryperktwo (perk_id, name, metadata)
                                                    VALUES (v_primary_two, NULL, NULL)
                                                    ON CONFLICT (perk_id) DO NOTHING;
                                                END;

                                                -- Insert into wrs_api_primaryperkthree table
                                                BEGIN
                                                    INSERT INTO wrs_api_primaryperkthree (perk_id, name, metadata)
                                                    VALUES (v_primary_three, NULL, NULL)
                                                    ON CONFLICT (perk_id) DO NOTHING;
                                                END;

                                                -- Insert into wrs_api_secondaryperkone table
                                                BEGIN
                                                    INSERT INTO wrs_api_secondaryperkone (perk_id, name, metadata)
                                                    VALUES (v_secondary_one, NULL, NULL)
                                                    ON CONFLICT (perk_id) DO NOTHING;
                                                END;

                                                -- Insert into wrs_api_secondaryperktwo table
                                                BEGIN
                                                    INSERT INTO wrs_api_secondaryperktwo (perk_id, name, metadata)
                                                    VALUES (v_secondary_two, NULL, NULL)
                                                    ON CONFLICT (perk_id) DO NOTHING;
                                                END;

                                                -- Insert into wrs_api_statshardone table
                                                BEGIN
                                                    INSERT INTO wrs_api_statshardone (shard_id, name, metadata)
                                                    VALUES (v_shard_one, NULL, NULL)
                                                    ON CONFLICT (shard_id) DO NOTHING;
                                                END;

                                                -- Insert into wrs_api_statshardtwo table
                                                BEGIN
                                                    INSERT INTO wrs_api_statshardtwo (shard_id, name, metadata)
                                                    VALUES (v_shard_two, NULL, NULL)
                                                    ON CONFLICT (shard_id) DO NOTHING;
                                                END;

                                                -- Insert into wrs_api_statshardthree table
                                                BEGIN
                                                    INSERT INTO wrs_api_statshardthree (shard_id, name, metadata)
                                                    VALUES (v_shard_three, NULL, NULL)
                                                    ON CONFLICT (shard_id) DO NOTHING;
                                                END;

                                                -- Retry insertion into wrs_api_runepagestat
                                                BEGIN
                                                    INSERT INTO wrs_api_runepagestat (keystone, primary_one, primary_two, primary_three, secondary_one, secondary_two, shard_one, shard_two, shard_three, "championId", elo, role, wins, losses, picked, season_id, patch, platform)
                                                    VALUES (v_keystone, v_primary_one, v_primary_two, v_primary_three, v_secondary_one, v_secondary_two, v_shard_one, v_shard_two, v_shard_three, v_champion_id, v_elo, v_role, v_wins, v_losses, v_picked, v_season_id, v_patch, v_platform)
                                                    ON CONFLICT (keystone, primary_one, primary_two, primary_three, secondary_one, secondary_two, shard_one, shard_two, shard_three, "championId", platform, patch, role, elo, season_id)
                                                    DO UPDATE SET 
                                                    wins = EXCLUDED.wins,
                                                    losses = EXCLUDED.losses;
                                                END;
                                            END;
                                    END;
                                END $$;
                                """.format(*formatted_table_names)
                            ,[runes_in_order[0], runes_in_order[1], runes_in_order[2], runes_in_order[3], runes_in_order[4], runes_in_order[5], shard1, shard2, shard3, participant_object["championId"], match_detail["averageElo"], participant_object["teamPosition"], win_increment, loss_increment, pick_increment, current_season.id, patch_tuple[0].full_version, request.query_params.get('platform')])
                            print("Updated rune page stats for", participant_object["puuid"])


                            # Legendary Item Stats writing logic 
                            legendary_items_built_by_player = participant_object["challenges"]["legendaryItemUsed"]

                            
                            cleaned_item_build = check_missing_items(legendary_items_built_by_player)
                            partition_name = "_" + request.query_params.get('platform')
                            formatted_table_names = [partition_name] * 3
                            if cleaned_item_build[0] != -1: # If the first item built is a real item (not dummy -1) write entire build to table
                                cursor.execute(
                                    """
                                    DO $$
                                    DECLARE
                                        v_legendary_one INTEGER;
                                        v_legendary_two INTEGER;
                                        v_legendary_three INTEGER;
                                        v_legendary_four INTEGER;
                                        v_legendary_five INTEGER;
                                        v_legendary_six INTEGER;
                                        v_champion_id INTEGER;
                                        v_elo TEXT;
                                        v_role TEXT;
                                        v_wins INTEGER;
                                        v_losses INTEGER;
                                        v_season_id INTEGER;
                                        v_patch TEXT;
                                        v_platform TEXT;
                                    BEGIN
                                        v_legendary_one := %s;
                                        v_legendary_two := %s;
                                        v_legendary_three := %s;
                                        v_legendary_four := %s;
                                        v_legendary_five := %s;
                                        v_legendary_six := %s;
                                        v_champion_id := %s;
                                        v_elo := %s;
                                        v_role := %s;
                                        v_wins := %s;
                                        v_losses := %s;
                                        v_season_id := %s;
                                        v_patch := %s;
                                        v_platform := %s;

                                        -- Set all constraints to immediate check to ensure we catch foreign key violations immediately
                                        SET CONSTRAINTS ALL IMMEDIATE;

                                        -- Attempt insertion into wrs_api_itembuildstat
                                        BEGIN
                                            INSERT INTO wrs_api_itembuildstat (legendary_one, legendary_two, legendary_three, legendary_four, legendary_five, legendary_six, "championId", elo, role, wins, losses, season_id, patch, platform)
                                            VALUES (v_legendary_one, v_legendary_two, v_legendary_three, v_legendary_four, v_legendary_five, v_legendary_six, v_champion_id, v_elo, v_role, v_wins, v_losses, v_season_id, v_patch, v_platform)
                                            ON CONFLICT (legendary_one, legendary_two, legendary_three, legendary_four, legendary_five, legendary_six, "championId", platform, patch, role, elo, season_id)
                                            DO UPDATE SET 
                                            wins = EXCLUDED.wins,
                                            losses = EXCLUDED.losses;
                                        EXCEPTION
                                            WHEN foreign_key_violation THEN
                                                -- Handle the foreign key violation
                                                RAISE NOTICE 'Foreign key violation caught: %%', SQLERRM;

                                                -- Write referenced rows to their respective tables and retry insertion into wrs_api_itembuildstat
                                                BEGIN
                                                    -- Insert into wrs_api_item table for each legendary item
                                                    BEGIN
                                                        INSERT INTO wrs_api_item ("itemId", name, metadata)
                                                        VALUES (v_legendary_one, NULL, NULL)
                                                        ON CONFLICT ("itemId") DO NOTHING;
                                                    END;

                                                    BEGIN
                                                        INSERT INTO wrs_api_item ("itemId", name, metadata)
                                                        VALUES (v_legendary_two, NULL, NULL)
                                                        ON CONFLICT ("itemId") DO NOTHING;
                                                    END;

                                                    BEGIN
                                                        INSERT INTO wrs_api_item ("itemId", name, metadata)
                                                        VALUES (v_legendary_three, NULL, NULL)
                                                        ON CONFLICT ("itemId") DO NOTHING;
                                                    END;

                                                    BEGIN
                                                        INSERT INTO wrs_api_item ("itemId", name, metadata)
                                                        VALUES (v_legendary_four, NULL, NULL)
                                                        ON CONFLICT ("itemId") DO NOTHING;
                                                    END;

                                                    BEGIN
                                                        INSERT INTO wrs_api_item ("itemId", name, metadata)
                                                        VALUES (v_legendary_five, NULL, NULL)
                                                        ON CONFLICT ("itemId") DO NOTHING;
                                                    END;

                                                    BEGIN
                                                        INSERT INTO wrs_api_item ("itemId", name, metadata)
                                                        VALUES (v_legendary_six, NULL, NULL)
                                                        ON CONFLICT ("itemId") DO NOTHING;
                                                    END;

                                                    -- Retry insertion into wrs_api_itembuildstat
                                                    BEGIN
                                                        INSERT INTO wrs_api_itembuildstat (legendary_one, legendary_two, legendary_three, legendary_four, legendary_five, legendary_six, "championId", elo, role, wins, losses, season_id, patch, platform)
                                                        VALUES (v_legendary_one, v_legendary_two, v_legendary_three, v_legendary_four, v_legendary_five, v_legendary_six, v_champion_id, v_elo, v_role, v_wins, v_losses, v_season_id, v_patch, v_platform)
                                                        ON CONFLICT (legendary_one, legendary_two, legendary_three, legendary_four, legendary_five, legendary_six, "championId", platform, patch, role, elo, season_id)
                                                        DO UPDATE SET 
                                                        wins = EXCLUDED.wins,
                                                        losses = EXCLUDED.losses;
                                                    END;
                                                END;
                                        END;
                                    END $$;
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
                                boot_id = boots_built_by_player[-1] # Get the last completed boot built, players sometimes sell and buy a different pair
                                cursor.execute(
                                    """
                                    DO $$
                                    DECLARE
                                        v_completed_boot INTEGER;
                                        v_champion_id INTEGER;
                                        v_elo TEXT;
                                        v_role TEXT;
                                        v_wins INTEGER;
                                        v_losses INTEGER;
                                        v_season_id INTEGER;
                                        v_patch TEXT;
                                        v_platform TEXT;
                                    BEGIN
                                        v_completed_boot := %s;
                                        v_champion_id := %s;
                                        v_elo := %s;
                                        v_role := %s;
                                        v_wins := %s;
                                        v_losses := %s;
                                        v_season_id := %s;
                                        v_patch := %s;
                                        v_platform := %s;

                                        -- Set all constraints to immediate check to ensure we catch foreign key violations immediately
                                        SET CONSTRAINTS ALL IMMEDIATE;

                                        -- Attempt insertion into wrs_api_completedbootstat
                                        BEGIN
                                            INSERT INTO wrs_api_completedbootstat ("completed_boot", "championId", "elo", "role", "wins", "losses", "season_id", "patch", "platform")
                                            VALUES (v_completed_boot, v_champion_id, v_elo, v_role, v_wins, v_losses, v_season_id, v_patch, v_platform)
                                            ON CONFLICT ("platform", "completed_boot", "championId", "patch", "role", "elo", "season_id")
                                            DO UPDATE SET 
                                            wins = wrs_api_completedbootstat.wins + EXCLUDED.wins,
                                            losses = wrs_api_completedbootstat.losses + EXCLUDED.losses;
                                        EXCEPTION
                                            WHEN foreign_key_violation THEN
                                                -- Handle the foreign key violation
                                                RAISE NOTICE 'Foreign key violation caught: %%', SQLERRM;

                                                -- Write referenced row to wrs_api_boot and retry the insertion into wrs_api_completedbootstat
                                                BEGIN
                                                    -- Insert into wrs_api_completedboot
                                                    INSERT INTO wrs_api_completedboot ("itemId", name, metadata)
                                                    VALUES (v_completed_boot, NULL, NULL)
                                                    ON CONFLICT ("itemId") DO NOTHING;

                                                    -- Retry insertion into wrs_api_completedbootstat
                                                    INSERT INTO wrs_api_completedbootstat ("completed_boot", "championId", "elo", "role", "wins", "losses", "season_id", "patch", "platform")
                                                    VALUES (v_completed_boot, v_champion_id, v_elo, v_role, v_wins, v_losses, v_season_id, v_patch, v_platform)
                                                    ON CONFLICT ("platform", "completed_boot", "championId", "patch", "role", "elo", "season_id")
                                                    DO UPDATE SET 
                                                    wins = wrs_api_completedbootstat.wins + EXCLUDED.wins,
                                                    losses = wrs_api_completedbootstat.losses + EXCLUDED.losses;
                                                END;
                                        END;
                                    END $$;
                                    """.format(*formatted_table_names)
                                ,[boot_id, participant_object["championId"], match_detail["averageElo"], participant_object["teamPosition"], win_increment, loss_increment, current_season.id, patch_tuple[0].full_version, request.query_params.get('platform')])
                            print("pass6")

                            partition_name = "_" + request.query_params.get('platform')
                            formatted_table_names = [partition_name] * 4
                            # Summoner Spell writing logi
                            spell_one = participant_object["summoner1Id"]
                            spell_two = participant_object["summoner2Id"]                                 
                            cursor.execute(
                                """
                                DO $$
                                DECLARE
                                    v_spell_one INTEGER;
                                    v_spell_two INTEGER;
                                    v_champion_id INTEGER;
                                    v_elo TEXT;
                                    v_role TEXT;
                                    v_wins INTEGER;
                                    v_losses INTEGER;
                                    v_picked INTEGER;
                                    v_season_id INTEGER;
                                    v_patch TEXT;
                                    v_platform TEXT;
                                BEGIN
                                    v_spell_one := %s;
                                    v_spell_two := %s;
                                    v_champion_id := %s;
                                    v_elo := %s;
                                    v_role := %s;
                                    v_wins := %s;
                                    v_losses := %s;
                                    v_picked := %s;
                                    v_season_id := %s;
                                    v_patch := %s;
                                    v_platform := %s;

                                    -- Set all constraints to immediate check to ensure we catch foreign key violations immediately
                                    SET CONSTRAINTS ALL IMMEDIATE;

                                    -- Attempt insertion into wrs_api_summonerspellstat
                                    BEGIN
                                        INSERT INTO wrs_api_summonerspellstat ("spell_one", "spell_two", "championId", "elo", "role", "wins", "losses", "picked", "season_id", "patch", "platform")
                                        VALUES (v_spell_one, v_spell_two, v_champion_id, v_elo, v_role, v_wins, v_losses, v_picked, v_season_id, v_patch, v_platform)
                                        ON CONFLICT ("platform", "spell_one", "spell_two", "championId", "patch", "role", "elo", "season_id")
                                        DO UPDATE SET 
                                        wins = wrs_api_summonerspellstat.wins + EXCLUDED.wins,
                                        losses = wrs_api_summonerspellstat.losses + EXCLUDED.losses,
                                        picked = wrs_api_summonerspellstat.picked + EXCLUDED.picked;
                                    EXCEPTION
                                        WHEN foreign_key_violation THEN
                                            -- Handle the foreign key violation
                                            RAISE NOTICE 'Foreign key violation caught: %%', SQLERRM;

                                            -- Write referenced row to wrs_api_summonerspell and retry the insertion into wrs_api_summonerspellstat
                                            BEGIN
                                                -- Insert into wrs_api_summonerspell
                                                INSERT INTO wrs_api_summonerspell ("spellId", "name", "metadata")
                                                VALUES (v_spell_one, NULL, NULL), (v_spell_two, NULL, NULL)
                                                ON CONFLICT ("spellId") DO NOTHING;

                                                -- Retry insertion into wrs_api_summonerspellstat
                                                INSERT INTO wrs_api_summonerspellstat ("spell_one", "spell_two", "championId", "elo", "role", "wins", "losses", "picked", "season_id", "patch", "platform")
                                                VALUES (v_spell_one, v_spell_two, v_champion_id, v_elo, v_role, v_wins, v_losses, v_picked, v_season_id, v_patch, v_platform)
                                                ON CONFLICT ("platform", "spell_one", "spell_two", "championId", "patch", "role", "elo", "season_id")
                                                DO UPDATE SET 
                                                wins = wrs_api_summonerspellstat.wins + EXCLUDED.wins,
                                                losses = wrs_api_summonerspellstat.losses + EXCLUDED.losses,
                                                picked = wrs_api_summonerspellstat.picked + EXCLUDED.picked;
                                            END;
                                    END;
                                END $$;
                                """.format(*formatted_table_names)
                            ,[spell_one, spell_two, participant_object["championId"], match_detail["averageElo"], participant_object["teamPosition"], win_increment, loss_increment, pick_increment, current_season.id, patch_tuple[0].full_version, request.query_params.get('platform')])


                        remake = participant_object["gameEndedInEarlySurrender"]
                        win = participant_object["win"]
                        if win:
                            win_increment = 1
                            loss_increment = 0
                        else:
                            win_increment = 0
                            loss_increment = 1
                        game_increment = 1
                        if match_detail["info"]["gameMode"] == "CLASSIC" and not remake and match_detail["info"]["endOfGameResult"] == "GameComplete":
                            total_cs = int(participant_object["neutralMinionsKilled"]) + int(participant_object["totalMinionsKilled"])
                            game_length = int(match_detail["info"]["gameDuration"]) / 60
                            cs_per_minute = float(total_cs/game_length)
                            cs_per_minute = round(cs_per_minute, 1)

                            partition_name = "_" + request.query_params.get('platform')
                            formatted_table_names = [partition_name] * 10
                            # Personal Champion KDA/Stats writing logic                               
                            cursor.execute(
                                """
                                DO $$
                                DECLARE
                                    v_games INTEGER;
                                    v_wins INTEGER;
                                    v_losses INTEGER;
                                    v_kills INTEGER;
                                    v_deaths INTEGER;
                                    v_assists INTEGER;
                                    v_cs INTEGER;
                                    v_csm NUMERIC;
                                    v_championId INTEGER;
                                    v_platform TEXT;
                                    v_puuid TEXT;
                                    v_queueId INTEGER;
                                    v_season_id INTEGER;
                                BEGIN
                                    v_games := %s;
                                    v_wins := %s;
                                    v_losses := %s;
                                    v_kills := %s;
                                    v_deaths := %s;
                                    v_assists := %s;
                                    v_cs := %s;
                                    v_csm := %s;
                                    v_championId := %s;
                                    v_platform := %s;
                                    v_puuid := %s;
                                    v_queueId := %s;
                                    v_season_id := %s;

                                    -- Set all constraints to immediate check, foreign key constraints are deferred and won't trigger exception handling
                                    SET CONSTRAINTS ALL IMMEDIATE;

                                    -- Attempt insertion into wrs_api_personalchampstat
                                    BEGIN
                                        INSERT INTO wrs_api_personalchampstat ("games", "wins", "losses", "kills", "deaths", "assists", "cs", "csm", "championId", "platform", "puuid", "queueId", "season_id")
                                        VALUES (v_games, v_wins, v_losses, v_kills, v_deaths, v_assists, v_cs, v_csm, v_championId, v_platform, v_puuid, v_queueId, v_season_id)
                                        ON CONFLICT ("puuid", "platform", "championId", "season_id")
                                        DO UPDATE SET
                                        games = wrs_api_personalchampstat.games + EXCLUDED.games,
                                        wins = wrs_api_personalchampstat.wins + EXCLUDED.wins,
                                        losses = wrs_api_personalchampstat.losses + EXCLUDED.losses,
                                        kills = wrs_api_personalchampstat.kills + EXCLUDED.kills,
                                        deaths = wrs_api_personalchampstat.deaths + EXCLUDED.deaths,
                                        assists = wrs_api_personalchampstat.assists + EXCLUDED.assists,
                                        cs = wrs_api_personalchampstat.cs + EXCLUDED.cs,
                                        csm = wrs_api_personalchampstat.csm + EXCLUDED.csm;

                                    EXCEPTION
                                        WHEN foreign_key_violation THEN
                                            -- Handle the foreign key violation
                                            RAISE NOTICE 'Foreign key violation for championId %%. Must insert missing reference.', v_championId;

                                            -- Write referenced row to wrs_api_champion
                                            INSERT INTO wrs_api_champion ("championId", "name", "metadata")
                                            VALUES (v_championId, NULL, NULL)
                                            ON CONFLICT ("championId") DO NOTHING;

                                            -- Retry the insert into wrs_api_personalchampstat
                                            INSERT INTO wrs_api_personalchampstat ("games", "wins", "losses", "kills", "deaths", "assists", "cs", "csm", "championId", "platform", "puuid", "queueId", "season_id")
                                            VALUES (v_games, v_wins, v_losses, v_kills, v_deaths, v_assists, v_cs, v_csm, v_championId, v_platform, v_puuid, v_queueId, v_season_id)
                                            ON CONFLICT ("puuid", "platform", "championId", "season_id")
                                            DO UPDATE SET
                                            games = wrs_api_personalchampstat.games + EXCLUDED.games,
                                            wins = wrs_api_personalchampstat.wins + EXCLUDED.wins,
                                            losses = wrs_api_personalchampstat.losses + EXCLUDED.losses,
                                            kills = wrs_api_personalchampstat.kills + EXCLUDED.kills,
                                            deaths = wrs_api_personalchampstat.deaths + EXCLUDED.deaths,
                                            assists = wrs_api_personalchampstat.assists + EXCLUDED.assists,
                                            cs = wrs_api_personalchampstat.cs + EXCLUDED.cs,
                                            csm = wrs_api_personalchampstat.csm + EXCLUDED.csm;
                                    END;
                                END $$;
                                """.format(*formatted_table_names)
                            ,[game_increment, win_increment, loss_increment, participant_object["kills"], participant_object["deaths"], participant_object["assists"], total_cs, cs_per_minute, participant_object["championId"], request.query_params.get('platform'), participant_object["puuid"], match_detail["info"]["queueId"], current_season.id]) 
                            print("pass 7")

                            selected_role = participant_object["teamPosition"]
                            top_increment = 0
                            jg_increment = 0
                            mid_increment = 0
                            bot_increment = 0
                            sup_increment = 0
                            if selected_role == "TOP":
                                top_increment +=1
                            elif selected_role == "JUNGLE":
                                jg_increment +=1
                            elif selected_role == "MIDDLE":
                                mid_increment +=1
                            elif selected_role == "BOTTOM":
                                bot_increment +=1
                            elif selected_role == "UTILITY":
                                sup_increment +=1

                            partition_name = "_" + request.query_params.get('platform')
                            formatted_table_names = [partition_name] * 6
                            cursor.execute(
                                """
                                    INSERT INTO wrs_api_preferredrole ("puuid", "top", "jungle", "middle", "bottom", "support", "platform", "season_id")
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                    ON CONFLICT ("puuid", "platform", "season_id")
                                    DO UPDATE SET 
                                    top = wrs_api_preferredrole.top + EXCLUDED.top,
                                    jungle = wrs_api_preferredrole.jungle + EXCLUDED.jungle,
                                    middle = wrs_api_preferredrole.middle + EXCLUDED.middle,
                                    bottom = wrs_api_preferredrole.bottom + EXCLUDED.bottom,
                                    support = wrs_api_preferredrole.support + EXCLUDED.support;
                                """.format(*formatted_table_names)
                            ,[participant_object["puuid"], top_increment, jg_increment, mid_increment, bot_increment, sup_increment, request.query_params.get('platform'), current_season.id]) 
                            print("pass 8")                     

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
        return JsonResponse(f"Could not update databse. Error: {str(err)}", safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
    summoner_searched = Summoner.objects.get(puuid=puuid, platform=request.query_params.get('platform'))
    serialized_summoner = SummonerCustomSerializer(summoner_searched)

    return JsonResponse(serialized_summoner.data, safe=False, status=status.HTTP_202_ACCEPTED)



######################################################################################
# Get all Challenger Players for a PLATFORM and TIER (300 Challengers for NA1)
######################################################################################
@check_riot_enforced_timeout
@api_view(['GET'])
@transaction.atomic
def get_ranked_ladder(request):

    lader_key = f"{request.query_params.get('platform')}_{request.query_params.get('page')}_ladder"
    cached_ladder = cache.get(lader_key)

    if cached_ladder:
        summoners = json.loads(cached_ladder)
        http_status_code = status.HTTP_208_ALREADY_REPORTED

    else:
        try:
            platform = Platform.objects.get(code=request.query_params.get('platform'))
            start = int(request.query_params.get('page')) * 10 - 10
            end = int(request.query_params.get('page')) * 10 
            # tier = request.query_params.get("tier").upper()
            tiers = ["CHALLENGER", "GRANDMASTER", "MASTER"]
            ranked_ladder = []

            for tier in tiers:
                query_page = 1
                print("iterating!")
                while True:
                    url = f'https://{request.query_params.get("platform")}.api.riotgames.com/lol/league-exp/v4/entries/RANKED_SOLO_5x5/{tier}/I?page={query_page}'
                    print(url)
                    ladder_page = rate_limited_RIOT_get(riot_endpoint=url, request=request)
                    if len(ladder_page) == 0:
                        break
                    ranked_ladder = ranked_ladder + ladder_page
                    query_page += 1

            # challenger_page1_response = requests.get(url_page1, headers=headers, verify=True)
            # challenger_page2_response = requests.get(url_page2, headers=headers, verify=True)
            # print("Got all challenger players OK")
            # page1 = challenger_page1_response.json()
            # page2 = challenger_page2_response.json()
            # challenger_players = page1 + page2
            portion_of_ladder_to_render = ranked_ladder[start:end]

            summoners = []
            for player_overview in portion_of_ladder_to_render:
                print("attempting for player:", player_overview["summonerId"])
                try:
                    existing_high_elo_player = Summoner.objects.get(encryptedSummonerId=player_overview["summonerId"], platform=platform)
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
                        , [existing_high_elo_player.puuid, request.query_params.get('platform'), current_season.id, json.dumps(player_overview)])

                    updated_summoner = model_to_dict(existing_high_elo_player)
                    updated_summoner["metadata"] = player_overview
                    summoners.append(updated_summoner)

                except Summoner.DoesNotExist:
                    print("NOT FOUND! FETCHING DETAILS OVERVIW")
                    # GET PUUID from Encrypted summonerId / list of Challenger Players
                    encrypted_sum_id_to_puuid_url = f"https://{request.query_params.get('platform')}.api.riotgames.com/lol/summoner/v4/summoners/{player_overview['summonerId']}"            
                    puuid_details_response = rate_limited_RIOT_get(riot_endpoint=encrypted_sum_id_to_puuid_url, request=request)
                    print("success ONE")
                    puuid = puuid_details_response["puuid"]
                    profileIconId = puuid_details_response["profileIconId"]

                    
                    # Get Display Name from PUUID
                    puuid_to_display_name_url = f"https://{request.query_params.get('region')}.api.riotgames.com/riot/account/v1/accounts/by-puuid/{puuid}"
                    display_name_details = rate_limited_RIOT_get(puuid_to_display_name_url, request=request)
                    print("success TWO")
                    gameName = display_name_details["gameName"]
                    tagLine = display_name_details["tagLine"]


                    print("check here")
                    # Write New Player to database
                    new_high_elo_player = Summoner.objects.create(puuid=puuid, gameName=gameName, tagLine=tagLine, platform=platform, profileIconId=profileIconId, encryptedSummonerId=player_overview["summonerId"])
                    print(f"{player_overview['tier']} saved to db")

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
                        , [new_high_elo_player.puuid, request.query_params.get('platform'), current_season.id, json.dumps(player_overview)])
                    print("Wrote successfully")


                    updated_summoner = model_to_dict(new_high_elo_player)
                    updated_summoner["metadata"] = player_overview
                    summoners.append(updated_summoner)

            cache.set(lader_key, json.dumps(summoners), timeout=3600)
            http_status_code = status.HTTP_201_CREATED
            print(http_status_code)

        except RiotApiError as err:
            return JsonResponse(err.error_response, status=err.error_code, safe=False)
        except RiotApiRateLimitError as err:
            return JsonResponse(err.error_response, status=err.error_code, safe=False)
        except Exception as err:
            return JsonResponse(f"Could not update databse. Error: {str(err)}", safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return JsonResponse(summoners, safe=False, status=http_status_code)


def testkey(request, *args, **kwargs):
    return "abc"



@api_view(['GET'])
def test(request):
    url = f'https://na1.api.riotgames.com/lol/league-exp/v4/entries/RANKED_SOLO_5x5/CHALLENGER/I?page=1'
    print("attempt1")
    ladder_page = rate_limited_RIOT_get(riot_endpoint=url, request=request)
    url = f'https://na1.api.riotgames.com/lol/league-exp/v4/entries/RANKED_SOLO_5x5/CHALLENGER/I?page=2'
    print("attemp2")
    ladder_page = rate_limited_RIOT_get(riot_endpoint=url, request=request)

        

    return JsonResponse("no error", safe=False, status=status.HTTP_226_IM_USED)




    # {
    #   "model": "wrs_api.Summoner",
    #   "fields": {
    #     "puuid": "f649YxVWblcWTKMjnLYAZTKlbH6b3iNEZXf9-HXZhxxJRBSQ-Zws7v6jErBh0tzyVS9VNo50FHK3rA",
    #     "gameName": "vanilli vanilli",
    #     "tagLine": "VV2",
    #     "platform": "na1",
    #     "profileIconId": 3795,
    #     "encryptedSummonerId": "ZANL-az6EkuuJc27gyzq8lkb4UrkpFTAisDG82lRU855N1qnDTfKhOyW-w",
    #     "most_recent_game": "NA1_4887039076",
    #     "created_at": "2024-04-01T18:20:07Z",
    #     "updated_at": "2024-04-01T18:20:07Z"
    #   }
    # },
    # {
    #   "model": "wrs_api.Summoner",
    #   "fields": {
    #     "puuid": "aYWKw--LdXozLfm-HJ8OFiHW9vKVUZLzwnsLvJFufYsmr4Xdjnac-3-u_2lRJPQZ6Z2Eop0EbJdOwQ",
    #     "gameName": "Tallish",
    #     "tagLine": "NA1",
    #     "platform": "na1",
    #     "profileIconId": 5023,
    #     "encryptedSummonerId": "8VJm42mkBm06t3w2XuM5WRfvyQcUWnh54ew_JO979wnw3DQl",
    #     "most_recent_game": "NA1_4889736532",
    #     "created_at": "2024-04-01T18:20:07Z",
    #     "updated_at": "2024-04-01T18:20:07Z"
    #   }
    # },
    # {
    #   "model": "wrs_api.Summoner",
    #   "fields": {
    #     "puuid": "xadTQjqNKZuYdjt4vMi5hWVemmsjCZZBeVtSaJ-EXPZsZ2UaAHyYJqw_aTzXdA672f5ZyfQqCL9uqQ",
    #     "gameName": "Dark Aura",
    #     "tagLine": "EUW",
    #     "platform": "euw1",
    #     "profileIconId": 6051,
    #     "encryptedSummonerId": "wMUm2A8D3zo4qajOQ9MvI9B5zX-XUY51wQ7m6UQfDFWyHzUQ",
    #     "most_recent_game": "EUW1_6759658609",
    #     "created_at": "2024-04-01T18:20:07Z",
    #     "updated_at": "2024-04-01T18:20:07Z"
    #   }
    # }