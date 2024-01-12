from .models import Summoner, Season, SummonerOverview, MatchHistory
from .serializers import  SummonerSerializer, SummonerOverviewSerializer, MatchHistorySerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
import requests
from requests.exceptions import HTTPError
from dotenv import load_dotenv
import os
import httpx
import asyncio
#### SWAP RESPONSE TO JSON RESPONSE FOR PRODUCTION

### Config ###
load_dotenv()
riot_key = os.environ["RIOT_KEY"]
headers = {'X-Riot-Token': riot_key}
##############

# puuid: f649YxVWblcWTKMjnLYAZTKlbH6b3iNEZXf9-HXZhxxJRBSQ-Zws7v6jErBh0tzyVS9VNo50FHK3rA
# encryptedSummonerId: 

# If you want to use this decorator on a function, add the below and include "region" has a parameter in func def
# @convert_platform_to_region
# def convert_platform_to_region(func):
#     def wrapper(request, *args, **kwargs):
#         region = ""
#         if request.query_params.get('platform') == "na1" or request.query_params.get('platform') == "oc1":
#             region+= "americas"
#         elif request.query_params.get('platform') == "kr1" or request.query_params.get('platform') == "jp1":
#             region+= "asia"
#         elif request.query_params.get('platform') == "euw1" or request.query_params.get('platform') == "eun1":
#             region+= "europe"
#         return func(request, region)
#     return wrapper

# Helper Function to check database of existing summoner overviews before hitting Riot API
def search_db_for_summoner_overview(request):
    try:
        summoner_overview = SummonerOverview.objects.get(gameName=request.query_params.get('gameName'), tagLine=request.query_params.get('tagLine'), region=request.query_params.get('tagLine'))
        summoner_overview_serializer = SummonerOverviewSerializer(summoner_overview)
        return Response(summoner_overview_serializer.data['overview'], status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
    except SummonerOverview.DoesNotExist:
        return None


# Helper Function to check database for existing match histories before hitting Riot API
def search_db_for_match_history(request):
    try:
        match_history = MatchHistory.objects.get(gameName=request.query_params.get('gameName'), tagLine=request.query_params.get('tagLine'), region=request.query_params.get('tagLine'))
        match_history_serializer = MatchHistorySerializer(match_history)
        return Response(match_history_serializer.data['history'], status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
    except MatchHistory.DoesNotExist:
        return None


@api_view(['GET'])
def get_summoner_externally(request):
    try:
        account_by_gameName_tagLine_url = f"https://{request.query_params.get('region')}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{request.query_params.get('gameName')}/{request.query_params.get('tagLine')}"
        response_account_details = requests.get(account_by_gameName_tagLine_url, headers=headers, verify=True)
        puuid = response_account_details.json()['puuid']

        encrypted_summonerID_by_puuid_url = f"https://{request.query_params.get('platform')}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
        response_summonerID = requests.get(encrypted_summonerID_by_puuid_url, headers=headers, verify=True)
        summonerID = response_summonerID.json()['id']
        profile_icon = response_summonerID.json()['profileIconId']


        summoner_searched = Summoner.objects.filter(puuid=puuid).first()
        if (summoner_searched and (request.query_params.get('region') != summoner_searched.region or request.query_params.get('gameName') != summoner_searched.gameName or request.query_params.get('tagLine') != summoner_searched.tagLine or profile_icon != summoner_searched.profileIconId or summonerID != summoner_searched.encryptedSummonerId)):
            summoner_searched.update(gameName=request.query_params.get('gameName'), tagLine=request.query_params.get('tagLine'), region=request.query_params.get('region'), profileIconId=profile_icon, encryptedSummonerId=summonerID)
            print("FOUND AND NEW INFORMATION", summoner_searched)
        elif(not summoner_searched):
             summoner_searched = Summoner.objects.create(puuid=puuid, gameName=request.query_params.get('gameName'), tagLine=request.query_params.get('tagLine'), region=request.query_params.get('region'), profileIconId=profile_icon, encryptedSummonerId=summonerID)

        serialized_summoner = SummonerSerializer(summoner_searched)
        

    except HTTPError as error:
        return Response(error.response.text, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serialized_summoner.data, status=status.HTTP_200_OK)


# URL: /summoner-overview/
# requires "region", "gameName", "tagLine", "platform", "update" as URL parameters
@api_view(['GET'])
def get_summoner_overview(request):
    if request.query_params.get('update') == "false":
        database_response = search_db_for_summoner_overview(request)
        if database_response:
            return database_response

    try:
        account_by_gameName_tagLine_url = f"https://{request.query_params.get('region')}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{request.query_params.get('gameName')}/{request.query_params.get('tagLine')}"
        response_account_details = requests.get(account_by_gameName_tagLine_url, headers=headers, verify=True)
        puuid = response_account_details.json()['puuid']

        encrypted_summonerID_by_puuid_url = f"https://{request.query_params.get('platform')}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
        response_summonerID = requests.get(encrypted_summonerID_by_puuid_url, headers=headers, verify=True)
        summonerID = response_summonerID.json()['id']
        summoner_icon = response_summonerID.json()['profileIconId']
        
        league_elo_by_summonerID_url = f"https://{request.query_params.get('platform')}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summonerID}"
        response_overview = requests.get(league_elo_by_summonerID_url, headers=headers, verify=True)

        if len(response_overview.json()) == 0:
                overview = {"tier": "UNRANKED", "rank": "UNRANKED", "leaguePoints": 0}
        else:
            overview = response_overview.json()[0]

        overview["puuid"] = puuid
        overview["profileIcon"] = summoner_icon
        overview["gameName"] = request.query_params.get('gameName')
        overview["tagLine"] = request.query_params.get('tagLine')
        overview["region"] = request.query_params.get('region')

        # .updated_or_create() returns a tuple
        # .update() only works on QuerySets
        updated_sum_overview = SummonerOverview.objects.get_or_create(puuid=puuid)[0]
        updated_sum_overview.gameName = request.query_params.get('gameName')
        updated_sum_overview.tagLine = request.query_params.get('tagLine')
        updated_sum_overview.region = request.query_params.get('region')
        updated_sum_overview.overview = overview
        updated_sum_overview.save()
        summoner_overview_serializer = SummonerOverviewSerializer(updated_sum_overview)

    except HTTPError as error:
        return Response(error.response.text, status=status.HTTP_400_BAD_REQUEST)
    # except:
    #     return Response({"message": "Server Error. Failed to Fetch Summoner Overview."}, status=status.HTTP_400_BAD_REQUEST)

    return Response(summoner_overview_serializer.data['overview'], status=status.HTTP_200_OK)


# URL: /match-history/
# requires "region", "gameName", "tagLine", "platform", "update" as URL parameters
@api_view(['GET'])
def get_match_history(request):
    if request.query_params.get('update') == "false":
        database_response = search_db_for_match_history(request)
        if database_response:
            return database_response
    try:
        account_by_gameName_tagLine_url = f"https://{request.query_params.get('region')}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{request.query_params.get('gameName')}/{request.query_params.get('tagLine')}"
        response_account_details = requests.get(account_by_gameName_tagLine_url, headers=headers, verify=True)
        puuid = response_account_details.json()['puuid']

        start = 0
        count = 3 # must be <= 100

        if request.query_params.get('queue'):
            matches_url = f"https://{request.query_params.get('region')}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start={start}&count={count}&queue={request.query_params.get('queue')}"
        else:
            matches_url = f"https://{request.query_params.get('region')}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start={start}&count={count}"

        response_matches = requests.get(matches_url, headers=headers, verify=True)
        matches = response_matches.json()
        
        match_history = []
        for match in matches:
            match_detail_url = f"https://{request.query_params.get('region')}.api.riotgames.com/lol/match/v5/matches/{match}"
            response_match_detail = requests.get(match_detail_url, headers=headers, verify=True)
            if response_match_detail.status_code != 200:
                return Response(response_match_detail)
            match_history.append(response_match_detail.json())
        
        # # .updated_or_create() returns a tuple
        # updated_match_history = MatchHistory.objects.update_or_create(history=match_history, gameName=request.query_params.get('gameName'), tagLine=request.query_params.get('tagLine'), region=request.query_params.get('region'))[0]
        # updated_match_history.puuid = puuid
        # updated_match_history.save()
        # match_history_serializer = MatchHistorySerializer(updated_match_history)

        # .updated_or_create() returns a tuple
        updated_match_history = MatchHistory.objects.get_or_create(puuid=puuid)[0]
        updated_match_history.history = match_history
        updated_match_history.gameName = request.query_params.get('gameName')
        updated_match_history.tagLine = request.query_params.get('tagLine')
        updated_match_history.region = request.query_params.get('region')
        updated_match_history.history = match_history
        updated_match_history.save()
        match_history_serializer = MatchHistorySerializer(updated_match_history)
        
    except:
        return Response({"message": "Failed to Fetch Match History."}, status=status.HTTP_400_BAD_REQUEST)

    return Response(match_history_serializer.data['history'], status=status.HTTP_200_OK)

