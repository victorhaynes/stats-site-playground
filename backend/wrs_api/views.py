from .models import Car, SummonerOverview
from .serializers import CarSerializer, SummonerOverviewSerializer
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


# #### utility function
# def get_region(request):
#     match request.query_params.get('platform'):
#         case "americas":
#             return "na1"


@api_view(['GET'])
def car_list(request):
    cars = Car.objects.all()
    car_serializer = CarSerializer(cars, many=True)
    return Response({"cars": car_serializer.data})


@api_view(['GET'])
def testing(request):
    match_id = ['NA1_4809070423'][0]
    match_url=f'https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}'
    response_match = requests.get(match_url, headers=headers)
    match_detail = response_match.json()
    # pprint.pprint(match_detail)
    return JsonResponse(match_detail)

@api_view(['GET'])
def testing2(request):
    match_id = "NA1_4828761378"
    match_url=f'https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}'
    response_match = requests.get(match_url, headers=headers)
    match_detail = response_match.json()
    # pprint.pprint(match_detail)
    return JsonResponse(match_detail)


# Helper Function to check database of summoner overviews before hitting Riot API
def search_db_for_summoner_overview(request):
    try:
        summoner_overview = SummonerOverview.objects.get(gameName=request.query_params.get('gameName'), tagLine=request.query_params.get('tagLine'))
        summoner_overview_serializer = SummonerOverviewSerializer(summoner_overview)
        return Response(summoner_overview_serializer.data, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
    except SummonerOverview.DoesNotExist:
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
        summonerID, summoner_icon = response_summonerID.json()['id'], response_summonerID.json()['profileIconId']

        league_elo_by_summonerID_url = f"https://{request.query_params.get('platform')}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summonerID}"
        response_overview = requests.get(league_elo_by_summonerID_url, headers=headers, verify=True)
        overview = response_overview.json()[0]
        overview["puuid"] = puuid
        overview["profileIcon"] = summoner_icon
        overview["gameName"] = request.query_params.get('gameName')
        overview["tagLine"] = request.query_params.get('tagLine')

        # .updated_or_create() returns a tuple
        updated_sum_overview = SummonerOverview.objects.update_or_create(overview)[0]
        summoner_overview_serializer = SummonerOverviewSerializer(updated_sum_overview)



    except HTTPError as e:
        return Response(e.response.text, status=status.HTTP_400_BAD_REQUEST)
    except IndexError:
        # This means that the player has no Ranked match history
        overview = {}
        overview["puuid"] = puuid
        overview["profileIcon"] = summoner_icon
        return Response(overview, status=status.HTTP_200_OK)
    # except:
    #     return Response({"message": "Server Error. Failed to Fetch Summoner Overview."}, status=status.HTTP_400_BAD_REQUEST)

    return Response(summoner_overview_serializer.data, status=status.HTTP_200_OK)

# URL: /match-history/
# requires "region", "gameName", "tagLine", "platform", "update" as URL parameters
@api_view(['GET'])
def get_match_history(request):
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
        
        return Response(match_history)

    except:
        return Response({"message": "Failed to Fetch Match History."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def test_puuid(request):
    try:
        # account_by_gameName_tagLine_url = f"https://{request.query_params.get('region')}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{request.query_params.get('gameName')}/{request.query_params.get('tagLine')}"
        url = "https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/vanilli%20vanilli/vv2"
        response_account_details = requests.get(url, headers=headers, verify=True)
        puuid = response_account_details.json()['puuid']
    except:
        # return Response(response_account_details.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(requests.get(url, headers=headers, verify=True))
    return Response(puuid, status=status.HTTP_200_OK)


@api_view(['GET'])
def test1(request):
    match_id = ['NA1_4844473260'][0]
    match_url=f'https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}'
    response_match = requests.get(match_url, headers=headers)
    match_detail = response_match.json()
    # pprint.pprint(match_detail)
    return JsonResponse(match_detail)

@api_view(['GET'])
def test2(request):
    match_id = ['NA1_4841859405'][0]
    match_url=f'https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}'
    response_match = requests.get(match_url, headers=headers)
    match_detail = response_match.json()
    # pprint.pprint(match_detail)
    return JsonResponse(match_detail)

@api_view(['GET'])
def test3(request):
    match_id = ['NA1_4828480152'][0]
    match_url=f'https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}'
    response_match = requests.get(match_url, headers=headers)
    match_detail = response_match.json()
    # pprint.pprint(match_detail)
    return JsonResponse(match_detail)