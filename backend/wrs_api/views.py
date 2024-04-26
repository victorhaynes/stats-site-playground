# from .models import Summoner, Season, SummonerOverview, MatchHistory, MatchDetails
# from .serializers import  SummonerSerializer, SummonerOverviewSerializer, MatchHistorySerializer, MatchDetailsSerializer, SeasonSerializer
from .models import Summoner, SummonerOverview, Platform, Season, Patch, Region, GameMode, Champion, LegendaryItem, TierTwoBoot, Match, SummonerMatch
from django.db import connection, transaction
from django.db.utils import DatabaseError
from .serializers import SummonerSerializer, SummonerCustomSerializer, SummonerOverviewSerializer
from .utilities import dictfetchall, get_summoner_matches, format_overview_strings_as_json, refresh_overview, ranked_badge
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
import httpx
import asyncio
#### SWAP RESPONSE TO JSON RESPONSE FOR PRODUCTION

#################################################################################
################################################################################
### Config #####################################################################
load_dotenv()
riot_key = os.environ["RIOT_KEY"]
headers = {'X-Riot-Token': riot_key}
try:
    current_season = Season.objects.get(season=os.environ["CURRENT_SEASON"], split=os.environ["CURRENT_SPLIT"])
except Exception as error:
    print("Admin must create season records in database." + repr(error))
season_schedule = json.loads(os.environ["SEASON_SCHEDULE"])
#################################################################################
#################################################################################
#################################################################################



#####################################################################################
# Helper Function to check database for existing summoner data before hitting Riot API
#####################################################################################
@api_view(['GET'])
def get_summoner(request):
    try:
        summoner = Summoner.objects.get(gameName=request.query_params.get('gameName'), tagLine=request.query_params.get('tagLine'), platform=request.query_params.get('platform'))
        serialized_summoner = SummonerCustomSerializer(summoner)
        return JsonResponse(serialized_summoner.data, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION, safe=False)
    except Summoner.DoesNotExist:
        return JsonResponse({"message": "There was an issue searching for summoner. Please try again.", "detail": repr(e)}, status=status.HTTP_404_NOT_FOUND, safe=False)
    except Exception as e:
        return JsonResponse({"message": "There was an issue searching for summoner. Please try again.", "detail": repr(e)}, status=status.HTTP_404_NOT_FOUND, safe=False)


########################################################################################
# # Helper Function to check database for existing match details before hitting Riot API
#####################################################################################
@api_view(['GET'])
def get_match_history(request):
    try:
        summoner = Summoner.objects.get(gameName=request.query_params.get('gameName'), tagLine=request.query_params.get('tagLine'), platform=request.query_params.get('platform'))
        print("player:", summoner)
        summoner_matches = get_summoner_matches(summoner, 5)
        print("my matches:", summoner_matches)
        return JsonResponse(summoner_matches, safe=False, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
    except Summoner.DoesNotExist:
        return JsonResponse({"message": "There was an issue searching for summoner. Please try again.", "detail": repr(e)}, status=status.HTTP_404_NOT_FOUND, safe=False)
    except Exception as e:
        return JsonResponse({"message": "There was an issue searching for summoner. Please try again.", "detail": repr(e)}, status=status.HTTP_404_NOT_FOUND, safe=False)


###########################################
# Takes region, gameName, tagLine, platform
###########################################
@api_view(['GET'])
def get_summoner_update(request):
    platform = Platform.objects.get(code=request.query_params.get('platform'))


    # Also eventually fix Flex Queue for Overview, it will be the 1st element in the json resposne if flex history exists
    # Atomically Create/Update: Summoner & SummonerOverview
    with transaction.atomic():
        try:
            # GET Basic Account Details
            account_by_gameName_tagLine_url = f"https://{request.query_params.get('region')}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{request.query_params.get('gameName')}/{request.query_params.get('tagLine')}"
            response_account_details = requests.get(account_by_gameName_tagLine_url, headers=headers, verify=True)

            if response_account_details.status_code == 200:
                # print("Get puuid success")
                puuid = response_account_details.json()['puuid']
                # GET Encrypted Summoner ID
                encrypted_summonerID_by_puuid_url = f"https://{request.query_params.get('platform')}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
                response_summonerID = requests.get(encrypted_summonerID_by_puuid_url, headers=headers, verify=True)
                summonerID = response_summonerID.json()['id']
                profile_icon = response_summonerID.json()['profileIconId']
                # Check if Summoner with this `puuid` and `platform` already exists in database, If exists and different update. Else create.
                try:
                    summoner_searched = Summoner.objects.get(puuid=puuid, platform=request.query_params.get('platform'))
                    if (request.query_params.get('platform').lower() != summoner_searched.platform.code.lower() or request.query_params.get('gameName').lower() != summoner_searched.gameName.lower() or request.query_params.get('tagLine').lower() != summoner_searched.tagLine.lower() or profile_icon != summoner_searched.profileIconId or summonerID != summoner_searched.encryptedSummonerId):
                        summoner_searched.custom_update(gameName=request.query_params.get('gameName'), tagLine=request.query_params.get('tagLine'), platform=platform, profileIconId=profile_icon, encryptedSummonerId=summonerID)
                
                except Summoner.DoesNotExist:
                    summoner_searched = Summoner.objects.create(puuid=puuid, gameName=request.query_params.get('gameName'), tagLine=request.query_params.get('tagLine'), platform=platform, profileIconId=profile_icon, encryptedSummonerId=summonerID)
            else:
                return JsonResponse({"Riot API returned error": response_account_details.status_code, "message": response_account_details.json(), "meta": 108}, status=response_account_details.status_code)
        
        except Exception as e:
            return JsonResponse(f"error: {repr(e)}", status=status.HTTP_500_INTERNAL_SERVER_ERROR, safe=False)
        except BaseException as e:
            return JsonResponse(f"error: {repr(e)}", status=status.HTTP_500_INTERNAL_SERVER_ERROR, safe=False)
        
        # GET Summoner Overview / Ranked Stats / Elo
        league_elo_by_summonerID_url = f"https://{request.query_params.get('platform')}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summonerID}"
        response_overview = requests.get(league_elo_by_summonerID_url, headers=headers, verify=True)
        
        # if response_account_details.status_code == 200:
        if response_overview.status_code == 200:
            summoner_elo = {}
            if response_overview.status_code == 200 and len(response_overview.json()) == 0:
                summoner_elo = json.dumps({"rank": "UNRANKED", "tier": "UNRANKED", "wins": 0, "losses": 0, "leaguePoints": 0})
            else:
                summoner_elo = json.dumps([d for d in response_overview.json() if d["queueType"] == "RANKED_SOLO_5x5"][0])
            
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
                , [summoner_searched.puuid, platform.code, current_season.id, summoner_elo])
        else:
            return JsonResponse({"Riot API returned error": response_account_details.status_code, "message": response_account_details.json(), "meta": 143}, status=response_account_details.status_code)


    # GET all match IDs played for a given Summoner during this split/season
    season_split_start_epoch_seconds = season_schedule[request.query_params.get('platform')][f"season_{current_season.season}"][f"split_{current_season.split}"]["start"]
    season_split_end_epoch_seconds = season_schedule[request.query_params.get('platform')][f"season_{current_season.season}"][f"split_{current_season.split}"]["end"]

    # Look at this, one too many requests?
    start = 0
    count = 100 # must be <= 100
    all_matches_played = []
    while True:
        matches_url = f"https://{request.query_params.get('region')}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids/?start={start}&count={count}&startTime={season_split_start_epoch_seconds}&endTime={season_split_end_epoch_seconds}"
        response_matches = requests.get(matches_url, headers=headers, verify=True)
        if response_matches.status_code == 200:
            print("Got 100 Matches Successfully:", matches_url)
            matches = response_matches.json()
            if len(matches) > 0:
                for match in matches:
                    all_matches_played.append(match)
                start+=len(matches)
            else:
                break
        else:
            return JsonResponse({"Riot API returned error": response_matches.status_code, "message": response_matches.json(), "meta": 167}, status=response_matches.status_code)

    print("total fetched", len(all_matches_played))
    print("newest game", all_matches_played[0])
    print("oldest game", all_matches_played[-1])

    print("!!!TESTING ONLY CHECK FOR SOME MATCHES!!!")
    # all_matches_played = all_matches_played[:2]
    all_matches_played = all_matches_played

    # GET details for all matches fetched that are not already in database
    with connection.cursor() as cursor:
        cursor.execute(
            """
                SELECT "matchId" FROM wrs_api_summonermatch WHERE platform = %s AND puuid = %s;
            """
        , [request.query_params.get('platform'), puuid])
        rows = cursor.fetchall()

    my_existing_matches = []
    for row in rows:
        my_existing_matches.append(row[0])

    participant_loop_broken = False # Keep track of if the inner loop breaks
    match_details_not_in_database = []
    for game in all_matches_played:
        if participant_loop_broken == True: # If inner loop breaks, break this outer loop
            break
        if game not in my_existing_matches:
            match_detail_url = f"https://{request.query_params.get('region')}.api.riotgames.com/lol/match/v5/matches/{game}"
            response_match_detail = requests.get(match_detail_url, headers=headers, verify=True)
            timeline_url = f"https://{request.query_params.get('region')}.api.riotgames.com/lol/match/v5/matches/{game}/timeline"
            timeline_response = requests.get(timeline_url, headers=headers)
            if response_match_detail.status_code == 200 and timeline_response.status_code == 200:
                print("successfully got details for:", game)
                print("successfully got timeline for:", game)
                match_detail = response_match_detail.json()
                timeline = timeline_response.json()

                
                participant_elos = {}
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
                        response_summonerID = requests.get(encrypted_summonerID_by_puuid_url, headers=headers, verify=True)
                        print("ESID STATUS CODE:", response_summonerID.status_code)
                        if response_summonerID.status_code == 200:
                            participant_summonerID = response_summonerID.json()['id']
                            participant_profile_icon = response_summonerID.json()['profileIconId']
                            participant_stats = [d for d in match_detail["info"]["participants"] if d.get("puuid") == participant_data["puuid"]][0] 
                            participant_gameName = participant_stats["riotIdGameName"]
                            participant_tagLine = participant_stats["riotIdTagline"]
                            new_summoner = Summoner.objects.create(puuid=participant_data["puuid"], gameName=participant_gameName, tagLine=participant_tagLine, platform=platform, profileIconId=participant_profile_icon, encryptedSummonerId=participant_summonerID)

                            # GET Summoner Overview / Ranked Stats / Elo
                            print("Getting ELO update for:", participant_data["puuid"])
                            league_elo_by_summonerID_url = f"https://{request.query_params.get('platform')}.api.riotgames.com/lol/league/v4/entries/by-summoner/{participant_summonerID}"
                            response_overview = requests.get(league_elo_by_summonerID_url, headers=headers, verify=True)
                            print("RANKED ELO STATUS CODE:", response_overview.status_code)

                            # if response_account_details.status_code == 200:
                            if response_overview.status_code == 200:
                                participant_elo = {}
                                if len(response_overview.json()) == 0:
                                    participant_elo = json.dumps({"rank": "UNRANKED", "tier": "UNRANKED", "wins": 0, "losses": 0, "leaguePoints": 0})
                                    # new_overviews[participant_data["puuid"]] = participant_elo
                                else:
                                    try:
                                        participant_elo = json.dumps([d for d in response_overview.json() if d["queueType"] == "RANKED_SOLO_5x5"][0])
                                    except IndexError: # Only plays flex queue and never ranked
                                    # new_overviews[participant_data["puuid"]] = participant_elo
                                        participant_elo = json.dumps({"rank": "UNRANKED", "tier": "UNRANKED", "wins": 0, "losses": 0, "leaguePoints": 0})


                                elo = {"tier": json.loads(participant_elo)["tier"], "rank": json.loads(participant_elo)["rank"]}
                                elo = ranked_badge(elo)
                                participant_elos[participant_data["puuid"]] = elo
                                participant_data["summonerElo"] = elo
                                with connection.cursor() as cursor:
                                    print("Inserting overview for:", participant_data["puuid"])
                                    cursor.execute(
                                    """
                                        INSERT INTO wrs_api_summoneroverview (puuid, platform, season_id, metadata, created_at, updated_at)
                                        VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                                        ON CONFLICT (puuid, season_id, platform) 
                                        DO UPDATE SET 
                                        metadata = EXCLUDED.metadata,
                                        updated_at = EXCLUDED.updated_at;
                                    """
                                    , [participant_data["puuid"], platform.code, current_season.id, participant_elo])
                            else:
                                if len(match_details_not_in_database) == 0:
                                    return JsonResponse({"Riot API returned error": response_overview.status_code, "message": response_overview.json(), "meta": 284}, status=response_overview.status_code)
                                # removed = match_details_not_in_database.pop() # Remove the last element which casued the error and continue with complete records
                                # print("REMOVING THE LAST GAME BC OF ERROR ABOVE", removed["metadata"]["matchId"])
                                # if len(match_details_not_in_database) == 0:
                                #     return JsonResponse({"message": "Forced to stop. Timeout received with partial data, try again.", "meta": 287}, status=429)
                                participant_loop_broken = True
                                break
                        else:
                            if len(match_details_not_in_database) == 0:
                                return JsonResponse({"Riot API returned error": response_summonerID.status_code, "message": response_summonerID.json(), "meta": 291}, status=response_summonerID.status_code)
                            # removed = match_details_not_in_database.pop() # Remove the last element which casued the error and continue with complete records
                            # print("REMOVING THE LAST GAME BC OF ERROR ABOVE", removed["metadata"]["matchId"])
                            # if len(match_details_not_in_database) == 0:
                            #     return JsonResponse({"message": "Forced to stop. Timeout received with partial data, try again.", "meta": 295}, status=429)
                            participant_loop_broken = True
                            break
                        
                    # If summoner exists, get current elo from database
                    else:
                        with connection.cursor() as cursor:
                            cursor.execute(
                                """
                                    SELECT * FROM wrs_api_summoneroverview WHERE puuid = %s AND platform = %s
                                    ORDER BY id DESC;
                                """,[participant_data["puuid"], request.query_params.get('platform')])
                            results = dictfetchall(cursor)
                        ov = json.loads(results[0]["metadata"])

                        elo = {"tier": ov["tier"], "rank": ov["rank"]}
                        elo = ranked_badge(elo)
                        participant_elos[participant_data["puuid"]] = elo
                        participant_data["summonerElo"] = elo
                        
                if participant_loop_broken == False:
                    match_detail["averageElo"] = participant_elos
                    match_details_not_in_database.append(match_detail)
                    
            elif response_match_detail.status_code == 429:
                print("STOP! HIT RIOT RATE LIMIT. MOVE ON")
                if len(match_details_not_in_database) == 0:
                    return JsonResponse({"Riot API returned error": response_match_detail.status_code, "message": response_match_detail.json(), "meta": 313}, status=response_match_detail.status_code)
                break
            elif timeline_response.status_code == 429:
                print("STOP! HIT RIOT RATE LIMIT. MOVE ON")
                if len(match_details_not_in_database) == 0:
                    return JsonResponse({"Riot API returned error": timeline_response.status_code, "message": timeline_response.json(), "meta": 317}, status=timeline_response.status_code)
                break
            else:
                return JsonResponse({"Riot API returned error": response_match_detail.status_code, "message": response_match_detail.json(), "meta": 320}, status=response_match_detail.status_code)
        else:
            print("skipped:", game, "already found")
            pass

## FROM TRY TO SKIPPED UN-UNDENT IF YOU REMOVE ATOMIC
## FROM TRY TO SKIPPED UN-UNDENT IF YOU REMOVE ATOMIC
## FROM TRY TO SKIPPED UN-UNDENT IF YOU REMOVE ATOMIC

    print(len(match_details_not_in_database))
    for d in match_details_not_in_database:
        print(d["metadata"]["matchId"], "not in db")

    # Try to save all fetched/new match details at once & update the Summoner's most recent game. If any fail reject all.
    # Need atomicity because match, match's join table, and summoner update must all succeed to be consistent
    try:
        # with transaction.atomic():
        #     with connection.cursor() as cursor:
                for match_detail in match_details_not_in_database:
                    with transaction.atomic():
                        with connection.cursor() as cursor:
                            print("attempting to write match:", match_detail["metadata"]["matchId"])
                            split_version = match_detail["info"]["gameVersion"].split('.',1)
                            version = (split_version[0] + "." + split_version[1].split('.',1)[0])
                            patch_tuple = Patch.objects.get_or_create(full_version=match_detail["info"]["gameVersion"], version=version, season_id=current_season)
                            print("Created new patch:", patch_tuple[1])
                            cursor.execute(
                                """
                                    INSERT INTO wrs_api_match ("matchId", "queueId", "season_id", "patch", "platform", "metadata")
                                    VALUES (%s, %s, %s, %s, %s, %s);
                                """
                            ,[match_detail["metadata"]["matchId"], match_detail["info"]["queueId"], current_season.id, patch_tuple[0].full_version, request.query_params.get('platform'), json.dumps(match_detail)])
                            
                            participants = match_detail["metadata"]["participants"]
                            for participant_puuid in participants:
                                cursor.execute(
                                    """
                                        INSERT INTO wrs_api_summonermatch ("matchId", "queueId", "puuid", "season_id", "patch", "platform")
                                        VALUES (%s, %s, %s, %s, %s, %s);
                                    """
                                ,[match_detail["metadata"]["matchId"], match_detail["info"]["queueId"], participant_puuid, current_season.id, patch_tuple[0].full_version, request.query_params.get('platform')])

                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                            SELECT "matchId" FROM wrs_api_summonermatch WHERE wrs_api_summonermatch.puuid = %s AND wrs_api_summonermatch.platform = %s
                            ORDER BY wrs_api_summonermatch."matchId" DESC
                            LIMIT 1;
                        """
                    ,[puuid, request.query_params.get('platform')])
                    last_saved_game = cursor.fetchone()[0]
                    if summoner_searched.most_recent_game != last_saved_game:
                        summoner_searched.custom_update(most_recent_game=last_saved_game)
                    print(last_saved_game)

    except Exception as err:
        return JsonResponse(f"Could not update databse. Error: {str(err)}", safe=False, status=status.HTTP_409_CONFLICT)


    summoner_searched = Summoner.objects.get(puuid=puuid, platform=request.query_params.get('platform'))
    serialized_summoner = SummonerCustomSerializer(summoner_searched)

    return JsonResponse(serialized_summoner.data, safe=False, status=status.HTTP_202_ACCEPTED)