from .models import Car
from .serializers import CarSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
import requests
from dotenv import load_dotenv
import os

#### SWAP RESPONSE TO JSON RESPONSE FOR PRODUCTION

### Config ###
load_dotenv()
riot_key = os.environ["RIOT_KEY"]
headers = {'X-Riot-Token': riot_key}
##############


#### utility function
def get_region(request):
    match request.query_params.get('platform'):
        case "americas":
            return "na1"



@api_view(['GET'])
def car_list(request):
    cars = Car.objects.all()
    car_serializer = CarSerializer(cars, many=True)
    return Response({"cars": car_serializer.data})

# requires "region", "gameName", "tagLine", "platform" as URL parameters
@api_view(['GET'])
def get_summoner_profile(request):
    try:
        account_by_gameName_tagLine_url = f"https://{request.query_params.get('region')}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{request.query_params.get('gameName')}/{request.query_params.get('tagLine')}"
        response_account_details = requests.get(account_by_gameName_tagLine_url, headers=headers, verify=True)
        puuid = response_account_details.json()['puuid']

        encrypted_summonerID_by_puuid_url = f"https://{request.query_params.get('platform')}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
        response_summonerID = requests.get(encrypted_summonerID_by_puuid_url, headers=headers, verify=True)
        summonerID = response_summonerID.json()['id']

        league_elo_by_summonerID_url = f"https://{request.query_params.get('platform')}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summonerID}"
        response_elo = requests.get(league_elo_by_summonerID_url, headers=headers, verify=True)
        elo = response_elo.json()[0]

    except:
        return Response("error", status=status.HTTP_404_NOT_FOUND)
    
    return Response(elo, status=status.HTTP_200_OK)



