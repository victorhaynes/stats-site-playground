
from django_ratelimit.decorators import ratelimit
import requests
import os
from django_redis import get_redis_connection
import json
from .utilities import RiotRateLimitApiError
from django.core.cache import cache
from .utilities import test_rate_limit_key
from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework.response import Response
from django.db import transaction
from .utilities import RiotApiError

headers = {'X-Riot-Token': os.environ["RIOT_KEY"]}
production = False if os.environ["PRODUCTION"] == 'false' else True

def rate_limited_RIOT_get(riot_endpoint, request):
    # Method Limits can be thought of as Endpoint Limits
    # Service Limits are not known in advanced and are enforced by Riot for all 3rd party apps
    region = request.query_params.get('region')
    if not region:
        region = ""
    platform = request.query_params.get('platform')
    if not platform:
        platform = ""
    cleaned_endpoint = None
    service = None
    application_seconds_ratelimit = '20/s' # Higher in Prod
    application_minutes_ratelimit = '100/2m' # Higher in Prod
    method_seconds_ratelimit = None 
    method_minutes_ratelimit = None
    
    application_rate_limit_key = os.environ["RIOT_KEY"] + region + platform

    if production:
        # SUMMONER V4
        if '/lol/summoners/v4/' in riot_endpoint or '/fulfillment/v1/summoners/by-puuid/' in riot_endpoint :
            if '/lol/summoner/v4/summoners/by-account/' in riot_endpoint:
                method_seconds_ratelimit = '1600/m'
                cleaned_endpoint = '/lol/summoner/v4/summoners/by-account/'
            elif '/lol/summoner/v4/summoners/by-puuid/' in riot_endpoint:
                method_seconds_ratelimit = '1600/m'
                cleaned_endpoint = '/lol/summoner/v4/summoners/by-puuid/'
            elif '/lol/summoner/v4/summoners/me' in riot_endpoint:
                method_seconds_ratelimit = '20000/10s'
                method_minutes_ratelimit = '1200000/10m'
                cleaned_endpoint = '/lol/summoner/v4/summoners/me'
            elif '/lol/summoner/v4/summoners/' in riot_endpoint:
                method_seconds_ratelimit = '1600/m'
                cleaned_endpoint = '/lol/summoner/v4/summoners/'
            elif '/fulfillment/v1/summoners/by-puuid/' in riot_endpoint:
                method_seconds_ratelimit = '20000/10s'
                method_minutes_ratelimit = '1200000/10m'
                cleaned_endpoint = '/fulfillment/v1/summoners/by-puuid/'
            service = 'Summoner v4'

    # LEAGUE V4
        elif '/lol/league/v4' in riot_endpoint:
            if '/lol/league/v4/challengerleagues/by-queue/' in riot_endpoint:
                method_seconds_ratelimit = '30/10s'
                method_minutes_ratelimit = '500/10m'
                cleaned_endpoint = '/lol/league/v4/challengerleagues/by-queue/'
            elif '/lol/league/v4/leagues/' in riot_endpoint:
                method_seconds_ratelimit = '500/10s'
                cleaned_endpoint = '/lol/league/v4/leagues/'
            elif '/lol/league/v4/masterleagues/by-queue/' in riot_endpoint:
                method_seconds_ratelimit = '30/10s'
                method_minutes_ratelimit = '500/10m'
                cleaned_endpoint = '/lol/league/v4/masterleagues/by-queue/'
            elif '/lol/league/v4/grandmasterleagues/by-queue/' in riot_endpoint:
                method_seconds_ratelimit = '30/10s'
                method_minutes_ratelimit = '500/10m'
                cleaned_endpoint = '/lol/league/v4/grandmasterleagues/by-queue/'
            elif '/lol/league/v4/entries/by-summoner/' in riot_endpoint:
                method_seconds_ratelimit = '100/m'
                cleaned_endpoint = '/lol/league/v4/entries/by-summoner/'
            elif '/lol/league/v4/entries/' in riot_endpoint:
                method_seconds_ratelimit = '50/10s'
                cleaned_endpoint = '/lol/league/v4/entries/'
            service = 'League v4'

        # LEAGUE EXP V4
        elif '/lol/league-exp/v4/' in riot_endpoint:
            if '/lol/league-exp/v4/entries/' in riot_endpoint:
                method_seconds_ratelimit = '50/10s'
                cleaned_endpoint = '/lol/league-exp/v4/entries/'
            service = 'League Exp v4'

        # ACCOUNT V1
        elif '/riot/account/v1/' in riot_endpoint:
            if '/riot/account/v1/accounts/by-riot-id/' in riot_endpoint:
                method_seconds_ratelimit = '1000/1m'
                cleaned_endpoint = '/riot/account/v1/accounts/by-riot-id/'
            elif '/riot/account/v1/accounts/by-puuid/' in riot_endpoint:
                method_seconds_ratelimit = '1000/1m'
                cleaned_endpoint = '/riot/account/v1/accounts/by-puuid/'
            elif '/riot/account/v1/active-shards/by-game/' in riot_endpoint:
                method_seconds_ratelimit = '20000/10s'
                method_minutes_ratelimit = '1200000/10m'
                cleaned_endpoint = '/riot/account/v1/active-shards/by-game/'
            service = 'Account v1'

        # MATCH V5
        elif '/lol/match/v5/' in riot_endpoint:
            if '/lol/match/v5/matches/' in riot_endpoint and '/timeline' in riot_endpoint:
                method_seconds_ratelimit = '2000/10s'
                cleaned_endpoint = '/lol/match/v5/matches/'
            elif '/lol/match/v5/matches/by-puuid/' in riot_endpoint and '/ids' in riot_endpoint:
                method_seconds_ratelimit = '2000/10s'
                cleaned_endpoint = '/lol/match/v5/matches/by-puuid/'
            elif '/lol/match/v5/matches/' in riot_endpoint:
                method_seconds_ratelimit = '2000/10s'
                cleaned_endpoint = '/lol/match/v5/matches/'
            service = 'Match v5'

        method_rate_limit_key = cleaned_endpoint + region + platform

    else:
        method_seconds_ratelimit = '20/s' # DEV/PERSONAL Default limit
        method_minutes_ratelimit = '100/2m' # DEV/PERSONAL Default limit
        application_seconds_ratelimit = '20/s'# DEV/PERSONAL Default limit
        application_minutes_ratelimit = '100/2m' # DEV/PERSONAL Default limit
        service = 'n/a'
        cleaned_endpoint = os.environ["RIOT_KEY"] # Ignore method-specifics, just use API KEY
        method_rate_limit_key = cleaned_endpoint + region + platform

    def get_application_rate_limit_seconds_key(request, *args, **kwargs):
        return str(application_rate_limit_key) + "seconds" + "_application"

    def get_application_rate_limit_minutes_key(request, *args, **kwargs):
        return str(application_rate_limit_key) + "minutes" + "_application"

    def get_method_rate_limit_seconds_key(request, *args, **kwargs):
        return str(method_rate_limit_key) + "seconds" + "_method"
    
    def get_method_rate_limit_minutes_key(request, *args, **kwargs):
        return str(method_rate_limit_key) + "minutes" + "_method"

    # # @ratelimit decorator returns 403 Error, and this is being enforced by the application, not by Riot
    @ratelimit(key=get_application_rate_limit_seconds_key, rate=application_seconds_ratelimit, method=ratelimit.ALL)
    @ratelimit(key=get_application_rate_limit_minutes_key, rate=application_minutes_ratelimit, method=ratelimit.ALL)
    @ratelimit(key=get_method_rate_limit_seconds_key, rate=method_seconds_ratelimit, method=ratelimit.ALL)
    @ratelimit(key=get_method_rate_limit_minutes_key, rate=method_minutes_ratelimit, method=ratelimit.ALL)
    # @ratelimit(key=get_method_rate_limit_minutes_key, rate='99/h', method=ratelimit.ALL, block=True)
    def get_request(request, riot_endpoint): 
        # print("get_application_rate_limit_seconds_key:", get_application_rate_limit_seconds_key(request))
        # print("application_seconds_ratelimit:", application_seconds_ratelimit)
        # print("get_application_rate_limit_minutes_key:", get_application_rate_limit_minutes_key(request))
        # print("application_minutes_ratelimit:", application_minutes_ratelimit)
        # print("get_method_rate_limit_seconds_key:", get_method_rate_limit_seconds_key(request))
        # print("method_seconds_ratelimit:", method_seconds_ratelimit)
        # print("get_method_rate_limit_minutes_key:", get_method_rate_limit_minutes_key(request))
        # print("method_minutes_ratelimit:", method_minutes_ratelimit)


        response = requests.get(riot_endpoint, headers=headers)

        if response.status_code == 200:
            print("rate limiter called without issue")
            return response.json()
        elif response.status_code == 429:
            print("Likely Service Limited By Riot / App & Method Limits Not Reached")
            ratelimit_type = response.headers.get('X-Rate-Limit-Type')
            retry_after = response.headers.get('Retry-After')
            if retry_after == None:
                retry_after = 30
            details = json.dumps({"type": ratelimit_type, "retry_after": int(retry_after) + 1})
            cache.set(429, details, timeout=int(retry_after) + 1)
            raise RiotRateLimitApiError(response.json(), response.status_code)
        else: # any other status code
            print("ERRORED")
            raise RiotApiError(response.json(), response.status_code)


    return get_request(request, riot_endpoint)