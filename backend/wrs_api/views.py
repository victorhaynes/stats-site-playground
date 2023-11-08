from .models import Car
from .serializers import CarSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
import requests
from dotenv import load_dotenv
import os
# SWAP RESPONSE TO JSON RESPONSE FOR PRODUCTION

### Config ###
load_dotenv()
##############

testing = os.environ["RIOT_KEY"]



@api_view(['GET'])
def car_list(request):
    cars = Car.objects.all()
    car_serializer = CarSerializer(cars, many=True)
    return Response({"cars": car_serializer.data})

@api_view(['GET'])
def deprecated_get(request):
    summoner_name = 'Enemy Graves'
    riot_key = os.environ["RIOT_KEY"]
    player_url = f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}'
    headers = {'X-Riot-Token': riot_key}
    response_player = requests.get(player_url, headers=headers, verify=True)
    puuid = response_player.json()['puuid']
    return Response("puuid: "+ puuid)
