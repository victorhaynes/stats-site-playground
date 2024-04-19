# from .models import Summoner, Season, SummonerOverview, MatchHistory, MatchDetails
# from .serializers import  SummonerSerializer, SummonerOverviewSerializer, MatchHistorySerializer, MatchDetailsSerializer, SeasonSerializer
from .models import Summoner, SummonerOverview, Platform, Season, Patch, Region, GameMode, Champion, LegendaryItem, TierTwoBoot, Match, SummonerMatch
from django.db import connection, transaction
from django.db.utils import DatabaseError
from .serializers import SummonerSerializer, SummonerCustomSerializer, SummonerOverviewSerializer
from .utilities import dictfetchall, get_summoner_matches, refresh_overview
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
            return JsonResponse({"Riot API returned error": response_account_details.status_code, "message": response_account_details.json()}, status=response_account_details.status_code)
    
    except Exception as e:
        return JsonResponse(f"error: {repr(e)}", status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION, safe=False)
    except BaseException as e:
        return JsonResponse(f"error: {repr(e)}", status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION, safe=False)
    
    # GET Summoner Overview / Ranked Stats / Elo
    league_elo_by_summonerID_url = f"https://{request.query_params.get('platform')}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summonerID}"
    response_overview = requests.get(league_elo_by_summonerID_url, headers=headers, verify=True)
    
    if response_account_details.status_code == 200:
        # print("Get Elo success.")
        summoner_elo = {}
        if response_overview.status_code == 200 and len(response_overview.json()) == 0:
            summoner_elo = json.dumps({"rank": "UNRANKED", "tier": "UNRANKED", "wins": 0, "losses": 0, "leaguePoints": 0})
        else:
            summoner_elo = json.dumps(response_overview.json()[0])
        
        # # is this performing the update? CHECK
        with connection.cursor() as cursor:
        #     cursor.execute(
        #     """
        #         UPDATE wrs_api_summoneroverview 
        #         SET metadata = %s 
        #         WHERE "puuid" = %s
        #         AND "platform" = %s
        #         ---RETURNING *;
        #     """
        #     , [summoner_elo, summoner_searched.puuid, summoner_searched.platform.code])

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
            # This returns the row(s) updated but as a tuple, we need it as an object
            # new_overviews = cursor.fetchall

    else:
        return JsonResponse({"Riot API returned error": response_account_details.status_code, "message": response_account_details.json()}, status=response_account_details.status_code)


    # GET all match IDs played for a given Summoner during this split/season
    season_split_start_epoch_seconds = season_schedule[request.query_params.get('platform')][f"season_{current_season.season}"][f"split_{current_season.split}"]["start"]
    season_split_end_epoch_seconds = season_schedule[request.query_params.get('platform')][f"season_{current_season.season}"][f"split_{current_season.split}"]["end"]


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
            return JsonResponse({"Riot API returned error": response_matches.status_code, "message": response_matches.json()}, status=response_matches.status_code)

    print("total fetched", len(all_matches_played))
    print("newest game", all_matches_played[0])
    print("oldest game", all_matches_played[-1])

    print("!!!TESTING ONLY CHECK FOR SOME MATCHES!!!")
    all_matches_played = all_matches_played[:3]

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


    match_details_not_in_database = []
    for game in all_matches_played:
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
                match_detail["timeline"] = timeline
                match_details_not_in_database.append(match_detail)
            elif response_match_detail.status_code == 429 or timeline_response.status_code == 429:
                print("STOP! HIT RIOT RATE LIMIT. MOVE ON")
                break
            else:
                return JsonResponse({"Riot API returned error": response_match_detail.status_code, "message": response_match_detail.json()}, status=response_match_detail.status_code)
        else:
            print("skipped:", game, "already found")
            pass

    print(len(match_details_not_in_database))
    for d in match_details_not_in_database:
        print(d["metadata"]["matchId"], "not in db")

    # Try to save all fetched/new match details at once & update the Summoner's most recent game. If any fail reject all.
    # Need atomicity because match, match's join table, and summoner update must all succeed to be consistent
    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                for match in match_details_not_in_database:
                    print("attempting to write match:", match["metadata"]["matchId"])
                    split_version = match["info"]["gameVersion"].split('.',1)
                    version = (split_version[0] + "." + split_version[1].split('.',1)[0])
                    patch_tuple = Patch.objects.get_or_create(full_version=match["info"]["gameVersion"], version=version, season_id=current_season)
                    print("Created new patch:", patch_tuple[1])
                    cursor.execute(
                        """
                            INSERT INTO wrs_api_match ("matchId", "queueId", "season_id", "patch", "platform", "metadata")
                            VALUES (%s, %s, %s, %s, %s, %s);
                        """
                    ,[match["metadata"]["matchId"], match["info"]["queueId"], current_season.id, patch_tuple[0].full_version, request.query_params.get('platform'), json.dumps(match)])
                    
                    participants = match["metadata"]["participants"]
                    for participant_puuid in participants:
                        # Check if participant already exists in database
                        print("Checking existing profile for:", participant_puuid)
                        participant_profile = Summoner.objects.filter(puuid=participant_puuid, platform=request.query_params.get('platform'))
                        if len(participant_profile) == 0:
                            # GET Encrypted Summoner ID externally
                            print("Getting ESID from Riot API for:", participant_puuid)
                            encrypted_summonerID_by_puuid_url = f"https://{request.query_params.get('platform')}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{participant_puuid}"
                            response_summonerID = requests.get(encrypted_summonerID_by_puuid_url, headers=headers, verify=True)
                            if response_summonerID.status_code == 200:
                                participant_summonerID = response_summonerID.json()['id']
                                participant_profile_icon = response_summonerID.json()['profileIconId']
                                participant_stats = [d for d in match["info"]["participants"] if d.get("puuid") == participant_puuid][0] 
                                participant_gameName = participant_stats["riotIdGameName"]
                                participant_tagLine = participant_stats["riotIdTagline"]
                                new_summoner = Summoner.objects.create(puuid=participant_puuid, gameName=participant_gameName, tagLine=participant_tagLine, platform=platform, profileIconId=participant_profile_icon, encryptedSummonerId=participant_summonerID)

                                # GET Summoner Overview / Ranked Stats / Elo
                                print("Getting ELO update for:", participant_puuid)
                                league_elo_by_summonerID_url = f"https://{request.query_params.get('platform')}.api.riotgames.com/lol/league/v4/entries/by-summoner/{participant_summonerID}"
                                response_overview = requests.get(league_elo_by_summonerID_url, headers=headers, verify=True)
                                
                                if response_account_details.status_code == 200:
                                    participant_elo = {}
                                    if response_overview.status_code == 200 and len(response_overview.json()) == 0:
                                        participant_elo = json.dumps({"rank": "UNRANKED", "tier": "UNRANKED", "wins": 0, "losses": 0, "leaguePoints": 0})
                                    else:
                                        participant_elo = json.dumps(response_overview.json()[0])

                                        print("Instering overview for:", participant_puuid)
                                        cursor.execute(
                                        """
                                            INSERT INTO wrs_api_summoneroverview (puuid, platform, season_id, metadata, created_at, updated_at)
                                            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                                            ON CONFLICT (puuid, season_id, platform) 
                                            DO UPDATE SET 
                                            metadata = EXCLUDED.metadata,
                                            updated_at = EXCLUDED.updated_at;
                                        """
                                        , [participant_puuid, platform.code, current_season.id, participant_elo])

                            elif response_summonerID.status_code != 200:
                                raise HTTPError("Error Issued from Riot API")
                            else:
                                raise Exception("Error fetching or creating Summoner.")
                        cursor.execute(
                            """
                                INSERT INTO wrs_api_summonermatch ("matchId", "queueId", "puuid", "season_id", "patch", "platform")
                                VALUES (%s, %s, %s, %s, %s, %s);
                            """
                        ,[match["metadata"]["matchId"], match["info"]["queueId"], participant_puuid, current_season.id, patch_tuple[0].full_version, request.query_params.get('platform')])
                # RE INDENT IF NEEDED
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

















@api_view(['GET'])
def test_all_matches(request):
    season_split_start_epoch_seconds = season_schedule[request.query_params.get('platform')][f"season_{current_season.season}"][f"split_{current_season.split}"]["start"]
    season_split_end_epoch_seconds = season_schedule[request.query_params.get('platform')][f"season_{current_season.season}"][f"split_{current_season.split}"]["end"]


    summoner_searched = Summoner.objects.get(gameName=request.query_params.get('gameName'), tagLine=request.query_params.get('tagLine'), platform=request.query_params.get('platform'))

    puuid = summoner_searched.puuid



    start = 0
    count = 100 # must be <= 100
    all_matches_played = []

    print(puuid)
    print(request.query_params.get('region'))
    while True:
        matches_url = f"https://{request.query_params.get('region')}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids/?start={start}&count={count}&startTime={season_split_start_epoch_seconds}&endTime={season_split_end_epoch_seconds}"
        response_matches = requests.get(matches_url, headers=headers, verify=True)
        if response_matches.status_code == 200:
            matches = response_matches.json()
            if len(matches) > 0 and (summoner_searched.most_recent_game not in matches):
                for match in matches:
                    all_matches_played.append(match)
                start+=len(matches)
            elif len(matches) > 0 and (summoner_searched.most_recent_game in matches):
                for match in matches:
                    if match != summoner_searched.most_recent_game:
                        all_matches_played.append(match)
                break
            else:
                break
        else:
            return JsonResponse({"Riot API returned error": response_matches.status_code, "message": response_matches.json()}, status=response_matches.status_code)


    print(len(all_matches_played))
    print(all_matches_played[0])
    print(all_matches_played[-1])

    # for match in all_matches_played:

    #     match_detail_url = f"https://{request.query_params.get('region')}.api.riotgames.com/lol/match/v5/matches/{match}"
    #     response_match_detail = requests.get(match_detail_url, headers=headers, verify=True)
    #     if response_match_detail.status_code != 200:
    #         return Response({"this was returned from Riot API": response_match_detail.json()}, status=response_match_detail.status_code)
    #     match_details.append(response_match_detail.json())


    #     try:
    #         summoner_match_details = MatchDetails.objects.get(summoner_id=summoner_searched.id)
    #         summoner_match_details.json = match_details
    #         summoner_match_details.save()
    #     except MatchDetails.DoesNotExist:
    #         summoner_match_details = MatchDetails.objects.create(summoner_id=summoner_searched.id, json=match_details)


    #     serialized_summoner = SummonerWithRelationsSerializer(summoner_searched)

    return JsonResponse(all_matches_played, safe=False, status=status.HTTP_202_ACCEPTED)


@api_view(['GET'])
def xxx(request):
    # summoner_searched = Summoner.objects.get(puuid='f649YxVWblcWTKMjnLYAZTKlbH6b3iNEZXf9-HXZhxxJRBSQ-Zws7v6jErBh0tzyVS9VNo50FHK3rA', platform=request.query_params.get('platform'))
    data = "UPDATED NO CONFLICT"
    # platform = Platform.objects.get(code=request.query_params.get('platform'))
    # season = Season.objects.last()
    # SummonerOverview.objects.create(puuid=summoner_searched, platform=platform, season_id = season, metadata=data)


    #  THIS IS HOW YOU UPDATE OR INSERT A SUMMONER OVERVIEW, FACTOR THIS INTO THE REAL UPDATE FUNCTION, AND REPLACE THE OLD VERSION THAT ONLY UPDATES
    #  THIS IS HOW YOU UPDATE OR INSERT A SUMMONER OVERVIEW, FACTOR THIS INTO THE REAL UPDATE FUNCTION, AND REPLACE THE OLD VERSION THAT ONLY UPDATES
    #  THIS IS HOW YOU UPDATE OR INSERT A SUMMONER OVERVIEW, FACTOR THIS INTO THE REAL UPDATE FUNCTION, AND REPLACE THE OLD VERSION THAT ONLY UPDATES
    #  FINISH ITERATING THROGH PARTICIPANTS, GETTING THEIR ELO, WRITING OVERVIEW, SAVING SUMMONER, MAKING SUMMONERMATCH ENTRY
    #  CALCULATING AVERAGE ELO FOR GAME
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
        , ["f649YxVWblcWTKMjnLYAZTKlbH6b3iNEZXf9-HXZhxxJRBSQ-Zws7v6jErBh0tzyVS9VNo50FHK3rA", "na1", 3, json.dumps(data)])

    # created_at | 2024-04-18 18:46:53.390509-05
    # updated_at | 2024-04-18 18:46:53.390509-05
    return JsonResponse("yes", safe=False, status=status.HTTP_200_OK)


###########################################
# takes region, gameName, tagLine, platform
@api_view(['GET'])
def old_update(request):
    try:
        # GET basic account details such as PUUID
        account_by_gameName_tagLine_url = f"https://{request.query_params.get('region')}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{request.query_params.get('gameName')}/{request.query_params.get('tagLine')}"
        response_account_details = requests.get(account_by_gameName_tagLine_url, headers=headers, verify=True)
 
        if response_account_details.status_code == 200:

            puuid = response_account_details.json()['puuid']
            # GET Encrypted Summoner ID
            encrypted_summonerID_by_puuid_url = f"https://{request.query_params.get('platform')}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
            response_summonerID = requests.get(encrypted_summonerID_by_puuid_url, headers=headers, verify=True)
            summonerID = response_summonerID.json()['id']
            profile_icon = response_summonerID.json()['profileIconId']
            
            #NEED TEST 
            try:
                summoner_searched = Summoner.objects.get(puuid=puuid, platform=request.query_params.get('platform'))
                if (request.query_params.get('region') != summoner_searched.region or request.query_params.get('gameName') != summoner_searched.gameName or request.query_params.get('tagLine') != summoner_searched.tagLine or profile_icon != summoner_searched.profileIconId or summonerID != summoner_searched.encryptedSummonerId):
                    summoner_searched.update(gameName=request.query_params.get('gameName'), tagLine=request.query_params.get('tagLine'), region=request.query_params.get('region'), profileIconId=profile_icon, encryptedSummonerId=summonerID)
                    print("FOUND AND NEW INFORMATION", summoner_searched)
            except Summoner.DoesNotExist:
                summoner_searched = Summoner.objects.create(puuid=puuid, gameName=request.query_params.get('gameName'), tagLine=request.query_params.get('tagLine'), region=request.query_params.get('region'), profileIconId=profile_icon, encryptedSummonerId=summonerID)
    
        else:
            return JsonResponse({"this was returned from Riot API": response_account_details.json()}, safe=False, status=response_account_details.status_code)
        
    except Exception as e:
        return JsonResponse(f"error: {repr(e)}", status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION, safe=False)
    return JsonResponse("ok", status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION, safe=False)

        # # GET Summoner Overview / Ranked Stats / Elo
        # league_elo_by_summonerID_url = f"https://{request.query_params.get('platform')}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summonerID}"
        # response_overview = requests.get(league_elo_by_summonerID_url, headers=headers, verify=True)
        
        # if response_account_details.status_code == 200:
        #     overview = {}
        #     if response_overview.status_code == 200 and len(response_overview.json()) == 0:
        #         overview = {"tier": "UNRANKED", "rank": "UNRANKED", "leaguePoints": 0}
        #     else:
        #         overview = response_overview.json()[0]

        #     try:

        #         players_summoner_overview = SummonerOverview.objects.get(summoner_id=summoner_searched.id)
        #         players_summoner_overview.json = overview
        #         players_summoner_overview.season = season
        #         players_summoner_overview.save()
        #     except SummonerOverview.DoesNotExist:
        #         players_summoner_overview = SummonerOverview.objects.create(summoner_id=summoner_searched.id, json=overview, season=season)
        # else:
        #     return Response({"this was returned from Riot API": response_account_details.json()}, status=response_account_details.status_code)
    
    #     # Logic to get all match history for a player
    #     # current_season = os.environ["CURRENT_SEASON"]
    #     # current_split = os.environ["CURRENT_SPLIT"]
    #     # # season_split_start_epoch_seconds = 1702898800
    #     # season_split_start_epoch_seconds = season_schedule[request.query_params.get('platform')][f"season_{current_season}"][f"split_{current_split}"]["start"]
    #     # season_split_end_epoch_seconds = season_schedule[request.query_params.get('platform')][f"season_{current_season}"][f"split_{current_split}"]["end"]


    #     # start = 0
    #     # count = 100 # must be <= 100
    #     # all_matches_played = []
    #     # while True:
    #     #     matches_url = f"https://{request.query_params.get('region')}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start={start}&count={count}&startTime={season_split_start_epoch_seconds}&endTime={season_split_end_epoch_seconds}"
    #     #     response_matches = requests.get(matches_url, headers=headers, verify=True)
    #     #     if response_matches.status_code == 200:
    #     #         matches = response_matches.json()
    #     #         if len(matches) > 0:
    #     #             for match in matches:
    #     #                 all_matches_played.append(match)
    #     #             start+=len(matches)
    #     #         else:
    #     #             break
    #     #     else:
    #     #         return Response({"this was returned from Riot API": response_account_details.json()}, status=response_account_details.status_code)


    #     # try:
    #     #     players_match_history = MatchHistory.objects.get(summoner_id=summoner_searched.id)
    #     #     players_match_history.json = all_matches_played
    #     #     players_match_history.season = season
    #     #     players_match_history.save()
    #     # except MatchHistory.DoesNotExist:
    #     #     players_match_history = MatchHistory.objects.create(summoner_id=summoner_searched.id, json=all_matches_played, season=season)


        # # logic to get recent match history
        # start = 0 # SET TO 15 in PRODUCTION
        # count = 3 # must be <= 100

        # if request.query_params.get('queue'):
        #     matches_url = f"https://{request.query_params.get('region')}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start={start}&count={count}&queue={request.query_params.get('queue')}"
        # else:
        #     matches_url = f"https://{request.query_params.get('region')}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start={start}&count={count}"

        # response_matches = requests.get(matches_url, headers=headers, verify=True)
        # matches = []
        # if response_account_details.status_code == 200:
        #     matches = response_matches.json()
        # else:
        #     return Response({"this was returned from Riot API": response_account_details.json()}, status=response_account_details.status_code)
        
        # match_details = []
        # for match in matches:
        #     match_detail_url = f"https://{request.query_params.get('region')}.api.riotgames.com/lol/match/v5/matches/{match}"
        #     response_match_detail = requests.get(match_detail_url, headers=headers, verify=True)
        #     if response_match_detail.status_code != 200:
        #         return Response({"this was returned from Riot API": response_match_detail.json()}, status=response_match_detail.status_code)
        #     match_details.append(response_match_detail.json())


        #     try:
        #         summoner_match_details = MatchDetails.objects.get(summoner_id=summoner_searched.id)
        #         summoner_match_details.json = match_details
        #         summoner_match_details.save()
        #     except MatchDetails.DoesNotExist:
        #         summoner_match_details = MatchDetails.objects.create(summoner_id=summoner_searched.id, json=match_details)


        #     serialized_summoner = SummonerWithRelationsSerializer(summoner_searched)

    # except HTTPError as error:
    #     return Response(error.response.text, status=status.HTTP_400_BAD_REQUEST)
    
    # # except:
    # #     return Response({"error": "Server error. System Admin to investigate trace log."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # return JsonResponse(serialized_summoner.data, status=status.HTTP_200_OK)


# # URL: /match-history/
# # requires "region", "gameName", "tagLine", "platform", "update" as URL parameters
# @api_view(['GET'])
# def get_more_match_details_from_riot(request):
#     if request.query_params.get('routeToRiot') == "false":
#         database_response = search_for_match_details_internally(request)
#         if database_response:
#             return database_response
        
#     try:
#         # Get recent match IDs from Riot
#         account_by_gameName_tagLine_url = f"https://{request.query_params.get('region')}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{request.query_params.get('gameName')}/{request.query_params.get('tagLine')}"
#         response_account_details = requests.get(account_by_gameName_tagLine_url, headers=headers, verify=True)
#         puuid = response_account_details.json()['puuid']

#         start = request.query_params.get('start')
#         count = request.query_params.get('count')

#         if request.query_params.get('queue'):
#             matches_url = f"https://{request.query_params.get('region')}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start={start}&count={count}&queue={request.query_params.get('queue')}"
#         else:
#             matches_url = f"https://{request.query_params.get('region')}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start={start}&count={count}"

#         response_matches = requests.get(matches_url, headers=headers, verify=True)
#         matches = response_matches.json()

#         # Get details for list of matches from Riot
#         match_details = []
#         for match in matches:
#             match_detail_url = f"https://{request.query_params.get('region')}.api.riotgames.com/lol/match/v5/matches/{match}"
#             response_match_detail = requests.get(match_detail_url, headers=headers, verify=True)
#             if response_match_detail.status_code != 200:
#                 print("ERROR!!!!!!!!!!")
#                 return Response(response_match_detail)
#             match_details.append(response_match_detail.json())
        
#         # If queue is NOT included in query parameters, update database /w Riot response to store ALL recent match details as JSON
#         if not request.query_params.get('queue'):
#             recent_details = MatchDetails.objects.get(summoner_id=request.query_params.get('summonerId'))
#             updated_recent_details = recent_details.json
#             for match in match_details:
#                 updated_recent_details.append(match)
#             recent_details.json = updated_recent_details
#             recent_details.save()
#             serialized_recent_history = MatchDetailsSerializer(recent_details)
#         # If queue IS included, pass Riot response directly to client without updating database with queue-specific JSON
#         else:
#             return JsonResponse(match_details, status=status.HTTP_200_OK, safe=False)

#     except Exception as err:
#         print(repr(err))
#         return Response({"message": "Failed to Fetch Match History."}, status=status.HTTP_400_BAD_REQUEST)

#     return JsonResponse(serialized_recent_history.data['json'], status=status.HTTP_200_OK, safe=False)


# @api_view(['GET'])
# def get_one_game(request):
#     sn = Summoner.objects.first()
#     resp = sn.match_details.json[0]
#     return JsonResponse(resp, safe=False, status=status.HTTP_200_OK)



@api_view(['GET'])
def get_one_timeline(request):

    tl = requests.get("https://americas.api.riotgames.com/lol/match/v5/matches/NA1_4976555192/timeline", headers=headers)
    if tl.status_code == 200:
        tl = tl.json()
        # participants = tl["info"]["participants"]

    participants = [
        "3JOkGbbu57W5wcLc0XmunoTnQUipWd3yW65pWE5dJElqgJKTZbogVTuubcwv1KxedgKhWp51APHZ8g",
        "_imi8FEMdLJ-AuPkm31f4bp0XKXA5RN-16o1umP7EzE2gKJWvikPnSpWbeZ6r4lj9XYmd0L0WA6rIg",
        "f649YxVWblcWTKMjnLYAZTKlbH6b3iNEZXf9-HXZhxxJRBSQ-Zws7v6jErBh0tzyVS9VNo50FHK3rA",
        "RM95DaYTI7fAb0g1V_sE-oznYW7sROIQpWY136tdkTmJQUYnjHSEtnR0sGjPsggBBiw74qiDQMyW5w",
        "Rn5wpWtVX-rDwEOrw1nB6c3k9iZMefxCfQv_-RHwh09xYk_uvzrpgAk52bsGddYNOoNKhqypYcrXgw",
        "5A61I7TFmg0-c17-BhTp216F-AOFrk7WbbcMRjqka2I-LYfPeW5dPpFPrJP2eG8hpfSVD6f7esJnrg",
        "vxi6ab_Ckyv1wxtbz7MTLDgBstE6AqQKpSp5acmqMGF89F7l1Eg9d2bnSMzmjs69pbjtdbpg4dVRYQ",
        "9P5Molij4LhUZuXju8SLUo49t9FbqcRjqDZerR-TD_fA6f_FS3h7YmJyLPIizhrSsDtylqxxGMEQJQ",
        "rEPwIMQb7D7Zz-dYAGMgP6gaAMAQPdYcoWUeHvzSEDsQk5phlCR7nKQshz3IK4NRg33JyjoiaZzZkQ",
        "R2jeUogviLmnIbTcWCRBweog2UJkLpMeIJe3aaVboCM5WUUOMtLJj4OGjVK4wgNyipVPLgKizlse_Q"
    ]

    all_item_paths = []
    for participant in participants:
        item_path = []
        # my_puuid = "f649YxVWblcWTKMjnLYAZTKlbH6b3iNEZXf9-HXZhxxJRBSQ-Zws7v6jErBh0tzyVS9VNo50FHK3rA"
        # my_puuid = participant
        # abc = participant * 2

        # Map PUUID/Participant to Participant ID
        participant_id_mapping = tl["info"]["participants"]
        summoner_participant_id = None
        for player in participant_id_mapping:
            if player["puuid"] == participant:
                summoner_participant_id = player["participantId"]
                break

        print(summoner_participant_id)
        print(participant)
            
        frames = tl["info"]["frames"]
        for frame in frames:
            events = frame["events"]

            for event in events:
                try:
                    if event["participantId"] == summoner_participant_id and event["type"] == "ITEM_PURCHASED":
                        item_path.append({"itemId": event["itemId"], "timestamp": event["timestamp"]})
                except KeyError:
                    pass

        all_item_paths.append({"puuid": participant, "build": item_path})

            # print(all_item_paths)
        
    return JsonResponse(all_item_paths, safe=False, status=200)


# @api_view(['GET'])
# def get_match_and_elo(request):
#     match_id = requests.get("https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/f649YxVWblcWTKMjnLYAZTKlbH6b3iNEZXf9-HXZhxxJRBSQ-Zws7v6jErBh0tzyVS9VNo50FHK3rA/ids?start=0&count=1", headers=headers).json()
#     match_details = requests.get("https://americas.api.riotgames.com/lol/match/v5/matches/NA1_4933511760", headers=headers).json()

#     pass