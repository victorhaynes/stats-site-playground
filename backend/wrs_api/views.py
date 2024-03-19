# from .models import Summoner, Season, SummonerOverview, MatchHistory, MatchDetails
# from .serializers import  SummonerSerializer, SummonerOverviewSerializer, MatchHistorySerializer, MatchDetailsSerializer, SeasonSerializer
from .models import Summoner
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
import requests
from requests.exceptions import HTTPError
from dotenv import load_dotenv
import os
import ast
import json
import httpx
import asyncio
#### SWAP RESPONSE TO JSON RESPONSE FOR PRODUCTION

### Config #####################################################################
load_dotenv()
riot_key = os.environ["RIOT_KEY"]
headers = {'X-Riot-Token': riot_key}
try:
    # season = Season.objects.get(season=os.environ["CURRENT_SEASON"], split=os.environ["CURRENT_SPLIT"])
    print("hello")
except Exception as error:
    print("Admin must create season records in database." + repr(error))
season_schedule = json.loads(os.environ["SEASON_SCHEDULE"])
#################################################################################


@api_view(['POST'])
def create_sum(request):
    try:
        Summoner.objects.create(puuid=request.query_params.get('puuid'), gameName=request.query_params.get('gameName'), tagLine=request.query_params.get('tagLine'), region=request.query_params.get('region'), profileIconId=request.query_params.get('profileIconId'), encryptedSummonerId=request.query_params.get('encryptedSummonerId'))
        return JsonResponse("It worked!!!", safe=False, status=status.HTTP_200_OK)
    except error:
        return JsonResponse(repr(error), safe=False, status=status.HTTP_400_BAD_REQUEST)

# Helper Function to check database for existing summoner data before hitting Riot API
# def search_for_summoner_data_internally(request):
#     try:
#         summoner = Summoner.objects.get(gameName=request.query_params.get('gameName'), tagLine=request.query_params.get('tagLine'), region=request.query_params.get('region'))
#         serialized_summoner = SummonerSerializer(summoner)
#         return JsonResponse(serialized_summoner.data, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
#     except Summoner.DoesNotExist:
#         return None

# # Helper Function to check database for existing match details before hitting Riot API
# def search_for_match_details_internally(request):
#     try:
#         summoner = Summoner.objects.get(gameName=request.query_params.get('gameName'), tagLine=request.query_params.get('tagLine'), region=request.query_params.get('region'))
#         match_details = summoner.match_details
#         serialized_match_details = MatchDetailsSerializer(match_details)
#         return Response(serialized_match_details.data['json'], status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
#     except SummonerOverview.DoesNotExist or MatchDetails.DoesNotExist:
#         return None


# # takes region, gameName, tagLine, platform
# @api_view(['GET'])
# def get_summoner_details_from_riot(request):
#     if request.query_params.get('routeToRiot') == "false":
#         database_response = search_for_summoner_data_internally(request)
#         if database_response:
#             return database_response
        
#     try:
#         # GET basic account details such as PUUID
#         account_by_gameName_tagLine_url = f"https://{request.query_params.get('region')}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{request.query_params.get('gameName')}/{request.query_params.get('tagLine')}"
#         response_account_details = requests.get(account_by_gameName_tagLine_url, headers=headers, verify=True)

#         if response_account_details.status_code == 200:

#             puuid = response_account_details.json()['puuid']
#             # GET Encrypted Summoner ID
#             encrypted_summonerID_by_puuid_url = f"https://{request.query_params.get('platform')}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
#             response_summonerID = requests.get(encrypted_summonerID_by_puuid_url, headers=headers, verify=True)
#             summonerID = response_summonerID.json()['id']
#             profile_icon = response_summonerID.json()['profileIconId']
            
#             #NEED TEST 
#             try:
#                 summoner_searched = Summoner.objects.get(puuid=puuid)
#                 if (request.query_params.get('region') != summoner_searched.region or request.query_params.get('gameName') != summoner_searched.gameName or request.query_params.get('tagLine') != summoner_searched.tagLine or profile_icon != summoner_searched.profileIconId or summonerID != summoner_searched.encryptedSummonerId):
#                     summoner_searched.update(gameName=request.query_params.get('gameName'), tagLine=request.query_params.get('tagLine'), region=request.query_params.get('region'), profileIconId=profile_icon, encryptedSummonerId=summonerID)
#                     print("FOUND AND NEW INFORMATION", summoner_searched)
#             except Summoner.DoesNotExist:
#                 summoner_searched = Summoner.objects.create(puuid=puuid, gameName=request.query_params.get('gameName'), tagLine=request.query_params.get('tagLine'), region=request.query_params.get('region'), profileIconId=profile_icon, encryptedSummonerId=summonerID)
        
#             serialized_summoner = SummonerSerializer(summoner_searched)
        
#         else:
#             return Response({"this was returned from Riot API": response_account_details.json()}, status=response_account_details.status_code)
        
#         # GET Summoner Overview / Ranked Stats / Elo
#         league_elo_by_summonerID_url = f"https://{request.query_params.get('platform')}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summonerID}"
#         response_overview = requests.get(league_elo_by_summonerID_url, headers=headers, verify=True)
        
#         if response_account_details.status_code == 200:
#             overview = {}
#             if response_overview.status_code == 200 and len(response_overview.json()) == 0:
#                 overview = {"tier": "UNRANKED", "rank": "UNRANKED", "leaguePoints": 0}
#             else:
#                 overview = response_overview.json()[0]

#             try:

#                 players_summoner_overview = SummonerOverview.objects.get(summoner_id=summoner_searched.id)
#                 players_summoner_overview.json = overview
#                 players_summoner_overview.season = season
#                 players_summoner_overview.save()
#             except SummonerOverview.DoesNotExist:
#                 players_summoner_overview = SummonerOverview.objects.create(summoner_id=summoner_searched.id, json=overview, season=season)
#         else:
#             return Response({"this was returned from Riot API": response_account_details.json()}, status=response_account_details.status_code)
    
#         # Logic to get all match history for a player
#         # current_season = os.environ["CURRENT_SEASON"]
#         # current_split = os.environ["CURRENT_SPLIT"]
#         # # season_split_start_epoch_seconds = 1702898800
#         # season_split_start_epoch_seconds = season_schedule[request.query_params.get('platform')][f"season_{current_season}"][f"split_{current_split}"]["start"]
#         # season_split_end_epoch_seconds = season_schedule[request.query_params.get('platform')][f"season_{current_season}"][f"split_{current_split}"]["end"]


#         # start = 0
#         # count = 100 # must be <= 100
#         # all_matches_played = []
#         # while True:
#         #     matches_url = f"https://{request.query_params.get('region')}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start={start}&count={count}&startTime={season_split_start_epoch_seconds}&endTime={season_split_end_epoch_seconds}"
#         #     response_matches = requests.get(matches_url, headers=headers, verify=True)
#         #     if response_matches.status_code == 200:
#         #         matches = response_matches.json()
#         #         if len(matches) > 0:
#         #             for match in matches:
#         #                 all_matches_played.append(match)
#         #             start+=len(matches)
#         #         else:
#         #             break
#         #     else:
#         #         return Response({"this was returned from Riot API": response_account_details.json()}, status=response_account_details.status_code)


#         # try:
#         #     players_match_history = MatchHistory.objects.get(summoner_id=summoner_searched.id)
#         #     players_match_history.json = all_matches_played
#         #     players_match_history.season = season
#         #     players_match_history.save()
#         # except MatchHistory.DoesNotExist:
#         #     players_match_history = MatchHistory.objects.create(summoner_id=summoner_searched.id, json=all_matches_played, season=season)


#         # logic to get recent match history
#         start = 0 # SET TO 15 in PRODUCTION
#         count = 3 # must be <= 100

#         if request.query_params.get('queue'):
#             matches_url = f"https://{request.query_params.get('region')}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start={start}&count={count}&queue={request.query_params.get('queue')}"
#         else:
#             matches_url = f"https://{request.query_params.get('region')}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start={start}&count={count}"

#         response_matches = requests.get(matches_url, headers=headers, verify=True)
#         matches = []
#         if response_account_details.status_code == 200:
#             matches = response_matches.json()
#         else:
#             return Response({"this was returned from Riot API": response_account_details.json()}, status=response_account_details.status_code)
        
#         match_details = []
#         for match in matches:
#             match_detail_url = f"https://{request.query_params.get('region')}.api.riotgames.com/lol/match/v5/matches/{match}"
#             response_match_detail = requests.get(match_detail_url, headers=headers, verify=True)
#             if response_match_detail.status_code != 200:
#                 return Response({"this was returned from Riot API": response_match_detail.json()}, status=response_match_detail.status_code)
#             match_details.append(response_match_detail.json())


#             try:
#                 summoner_match_details = MatchDetails.objects.get(summoner_id=summoner_searched.id)
#                 summoner_match_details.json = match_details
#                 summoner_match_details.save()
#             except MatchDetails.DoesNotExist:
#                 summoner_match_details = MatchDetails.objects.create(summoner_id=summoner_searched.id, json=match_details)


#             serialized_summoner = SummonerSerializer(summoner_searched)

#     except HTTPError as error:
#         return Response(error.response.text, status=status.HTTP_400_BAD_REQUEST)
    
#     # except:
#     #     return Response({"error": "Server error. System Admin to investigate trace log."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
#     return JsonResponse(serialized_summoner.data, status=status.HTTP_200_OK)


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

# @api_view(['GET'])
# def get_one_timeline(request):

#     item_path = []
#     my_puuid = "f649YxVWblcWTKMjnLYAZTKlbH6b3iNEZXf9-HXZhxxJRBSQ-Zws7v6jErBh0tzyVS9VNo50FHK3rA"

#     tl = requests.get("https://americas.api.riotgames.com/lol/match/v5/matches/NA1_4934431330/timeline", headers=headers)
#     if tl.status_code == 200:
#         print("HELLO")
#         tl = tl.json()
#         participants = tl["info"]["participants"]

#         my_id = None

#         for participant in participants:
#             if participant["puuid"] == my_puuid:
#                 my_id = participant["participantId"]
#                 break
        
#         frames = tl["info"]["frames"]
#         for frame in frames:
#             events = frame["events"]

#             for event in events:
#                 try:
#                     if event["participantId"] == my_id and event["type"] == "ITEM_PURCHASED":
#                         item_path.append({"itemId": event["itemId"], "timestamp": event["timestamp"]})
#                 except KeyError:
#                     pass
        
#     print("SECOND")
#     return JsonResponse(item_path, safe=False, status=200)


# @api_view(['GET'])
# def get_match_and_elo(request):
#     match_id = requests.get("https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/f649YxVWblcWTKMjnLYAZTKlbH6b3iNEZXf9-HXZhxxJRBSQ-Zws7v6jErBh0tzyVS9VNo50FHK3rA/ids?start=0&count=1", headers=headers).json()
#     match_details = requests.get("https://americas.api.riotgames.com/lol/match/v5/matches/NA1_4933511760", headers=headers).json()

#     pass