from .models import Car, SummonerOverview, MatchHistory, RankedLpHistory
from .serializers import CarSerializer, SummonerOverviewSerializer, MatchHistorySerializer, RankedLpHistorySerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
import requests
from requests.exceptions import HTTPError
from dotenv import load_dotenv
import os

#### SWAP RESPONSE TO JSON RESPONSE FOR PRODUCTION

### Config ###
load_dotenv()
riot_key = os.environ["RIOT_KEY"]
headers = {'X-Riot-Token': riot_key}
##############


def convert_platform_to_region(func):
    def wrapper(request, *args, **kwargs):
        region = ""
        if request.query_params.get('platform') == "na1" or request.query_params.get('platform') == "oc1":
            region+= "americas"
        elif request.query_params.get('platform') == "kr1" or request.query_params.get('platform') == "jp1":
            region+= "asia"
        elif request.query_params.get('platform') == "euw1" or request.query_params.get('platform') == "eun1":
            region+= "europe"
        return func(request, region)
    return wrapper

# Helper Function to check database of existing summoner overviews before hitting Riot API
@convert_platform_to_region
def search_db_for_summoner_overview(request, region):
    try:
        summoner_overview = SummonerOverview.objects.get(gameName=request.query_params.get('gameName'), tagLine=request.query_params.get('tagLine'), region=region)
        summoner_overview_serializer = SummonerOverviewSerializer(summoner_overview)
        return Response(summoner_overview_serializer.data['overview'], status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
    except SummonerOverview.DoesNotExist:
        return None


# Helper Function to check database for existing match histories before hitting Riot API
# @convert_platform_to_region
@convert_platform_to_region
def search_db_for_match_history(request, region):
    try:
        match_history = MatchHistory.objects.get(gameName=request.query_params.get('gameName'), tagLine=request.query_params.get('tagLine'), region=region)
        match_history_serializer = MatchHistorySerializer(match_history)
        return Response(match_history_serializer.data['history'], status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
    except MatchHistory.DoesNotExist:
        return None


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


# test http://localhost:8000/test/?region=americas&gameName=vanilli%20vanilli&tagLine=vv2&platform=na1&queue=420
# need season/split start and end Epoch-seconds times
@api_view(['GET'])
def basline_lp_and_ranked_history(request):
    epoch_season_start = 1689793200
    epoch_season_end = 1704873600

    account_by_gameName_tagLine_url = f"https://{request.query_params.get('region')}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{request.query_params.get('gameName')}/{request.query_params.get('tagLine')}"
    response_account_details = requests.get(account_by_gameName_tagLine_url, headers=headers, verify=True)
    puuid = response_account_details.json()['puuid']

    start = 0
    count = 100 # must be <= 100
    all_ranked_matches = []
    while True:
        matches_url = f"https://{request.query_params.get('region')}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start={start}&count={count}&startTime={epoch_season_start}&endTime={epoch_season_end}&queue={request.query_params.get('queue')}"
        response_matches = requests.get(matches_url, headers=headers, verify=True)
        if response_matches.status_code == 200:
            matches = response_matches.json()
            if len(matches) > 0:
                for match in matches:
                    all_ranked_matches.append(match)
                start+=len(matches)
            else:
                break

    encrypted_summonerID_by_puuid_url = f"https://{request.query_params.get('platform')}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
    response_summonerID = requests.get(encrypted_summonerID_by_puuid_url, headers=headers, verify=True)
    summonerID = response_summonerID.json()['id']
    summoner_icon = response_summonerID.json()['profileIconId']
    
    league_elo_by_summonerID_url = f"https://{request.query_params.get('platform')}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summonerID}"
    response_overview = requests.get(league_elo_by_summonerID_url, headers=headers, verify=True)

    # this means there is no ranked history
    if len(response_overview.json()) == 0:
            overview = {"tier": "UNRANKED", "rank": "UNRANKED", "leaguePoints": 0}
    else:
        overview = response_overview.json()[0]

    per_game_lp = []
    for match in all_ranked_matches:
        per_game_lp.append(
            {
                "matchId": match,
                "tier": overview["tier"],
                "rank": overview["rank"],
                "leaguePoints": overview["leaguePoints"],
                "delta": None
            })

    baseline_lp_history = RankedLpHistory.objects.get_or_create(puuid=puuid)[0]
    baseline_lp_history.gameName = request.query_params.get('gameName')
    baseline_lp_history.tagLine = request.query_params.get('tagLine')
    baseline_lp_history.region = request.query_params.get('region')
    baseline_lp_history.lp_history = per_game_lp
    baseline_lp_history.save()


    lp_history_serializer = RankedLpHistorySerializer(baseline_lp_history)


    return Response(lp_history_serializer.data['lp_history'], status=status.HTTP_200_OK)

