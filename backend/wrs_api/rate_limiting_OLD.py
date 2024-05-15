from django_ratelimit.decorators import ratelimit
import requests
import os
from django_redis import get_redis_connection
import json
from .utilities import RiotRateLimitError
from django.core.cache import cache
from .utilities import test_rate_limit_key
from rest_framework.decorators import api_view


headers = {'X-Riot-Token': os.environ["RIOT_KEY"]}
production = False if os.environ["PRODUCTION"] == 'false' else True

# Add region or platform to the key eventually
class RiotRateLimiter:
    def __init__(self, riot_endpoint, region, request):
        self.riot_endpoint = riot_endpoint
        self.region = region
        self.requests_number = None
        self.time_period = None
        self.cleaned_endpoint = None
        self.method_rate_string = None
        self.service = None
        self.application_rate_string = '10/s' # Higher in Prod
        self.request = request

        if production:
            # SUMMONER V4
            if '/lol/summoners/v4/' in self.riot_endpoint or '/fulfillment/v1/summoners/by-puuid/' in self.riot_endpoint :
                if '/lol/summoner/v4/summoners/by-account/' in self.riot_endpoint:
                    self.requests_number = '1600'
                    self.time_period = 'm'  # 1600 requests every minute
                    self.cleaned_endpoint = '/lol/summoner/v4/summoners/by-account/'
                elif '/lol/summoner/v4/summoners/by-puuid/' in self.riot_endpoint:
                    self.requests_number = '1600'
                    self.time_period = 'm'  # 1600 requests every minute
                    self.cleaned_endpoint = '/lol/summoner/v4/summoners/by-puuid/'
                elif '/lol/summoner/v4/summoners/me' in self.riot_endpoint:
                    self.requests_number = '2000'
                    self.time_period = 's'  # 20,000 requests every 10 second or 1,200,000 every 10 minutes
                    self.cleaned_endpoint = '/lol/summoner/v4/summoners/me'
                elif '/lol/summoner/v4/summoners/' in self.riot_endpoint:
                    self.requests_number = '1600'
                    self.time_period = 'm'  # 1600 requests every minute
                    self.cleaned_endpoint = '/lol/summoner/v4/summoners/'
                elif '/fulfillment/v1/summoners/by-puuid/' in self.riot_endpoint:
                    self.requests_number = '2000'
                    self.time_period = 's'  # 20,000 requests every 10 second or 1,200,000 every 10 minutes
                    self.cleaned_endpoint = '/fulfillment/v1/summoners/by-puuid/'
                self.service = 'Summoner v4'

        # LEAGUE V4
            elif '/lol/league/v4' in self.riot_endpoint:
                if '/lol/league/v4/challengerleagues/by-queue/' in self.riot_endpoint:
                    self.requests_number = '1'
                    self.time_period = 's'  # 30 requests every 10 seconds or 500 per 10 mins... < 1 /s technically but not used
                    self.cleaned_endpoint = '/lol/league/v4/challengerleagues/by-queue/'
                elif '/lol/league/v4/leagues/' in self.riot_endpoint:
                    self.requests_number = '50'
                    self.time_period = 's'  # 500 requests every 10 seconds
                    self.cleaned_endpoint = '/lol/league/v4/leagues/'
                elif '/lol/league/v4/masterleagues/by-queue/' in self.riot_endpoint:
                    self.requests_number = '1'
                    self.time_period = 's'  # 30 requests every 10 seconds or 500 per 10 mins... < 1 /s technically but not used
                    self.cleaned_endpoint = '/lol/league/v4/masterleagues/by-queue/'
                elif '/lol/league/v4/grandmasterleagues/by-queue/' in self.riot_endpoint:
                    self.requests_number = '1'
                    self.time_period = 's'  # 30 requests every 10 seconds or 500 per 10 mins... < 1 /s technically but not used
                    self.cleaned_endpoint = '/lol/league/v4/grandmasterleagues/by-queue/'
                elif '/lol/league/v4/entries/by-summoner/' in self.riot_endpoint:
                    self.requests_number = '1'
                    self.time_period = 'm'  # 100 requests every minute
                    self.cleaned_endpoint = '/lol/league/v4/entries/by-summoner/'
                elif '/lol/league/v4/entries/' in self.riot_endpoint:
                    self.requests_number = '5'
                    self.time_period = 's'  # 50 requests every 10 seconds
                    self.cleaned_endpoint = '/lol/league/v4/entries/'
                self.service = 'League v4'

            # LEAGUE EXP V4
            elif '/lol/league-exp/v4/' in self.riot_endpoint:
                if '/lol/league-exp/v4/entries/' in self.riot_endpoint:
                    self.requests_number = '3'
                    self.time_period = 'h'  # 50 requests every 10 seconds
                    self.cleaned_endpoint = '/lol/league-exp/v4/entries/'
                self.service = 'League Exp v4'

            # ACCOUNT V1
            elif '/riot/account/v1/' in self.riot_endpoint:
                if '/riot/account/v1/accounts/by-riot-id/' in self.riot_endpoint:
                    self.requests_number = '1000'
                    self.time_period = 'm'  # 1000 requests every minute
                    self.cleaned_endpoint = '/riot/account/v1/accounts/by-riot-id/'
                elif '/riot/account/v1/accounts/by-puuid/' in self.riot_endpoint:
                    self.requests_number = '1000'
                    self.time_period = 'm'  # 1000 requests every minute
                    self.cleaned_endpoint = '/riot/account/v1/accounts/by-puuid/'
                elif '/riot/account/v1/active-shards/by-game/' in self.riot_endpoint:
                    self.requests_number = '20000'
                    self.time_period = 's'  # 20000 requests every 10 seconds or 1200000 every 10 minutes
                    self.cleaned_endpoint = '/riot/account/v1/active-shards/by-game/'
                self.service = 'Account v1'

            # MATCH V5
            elif '/lol/match/v5/' in self.riot_endpoint:
                if '/lol/match/v5/matches/' in self.riot_endpoint and '/timeline' in self.riot_endpoint:
                    self.requests_number = '200'
                    self.time_period = 's'  # 2000 requests every 10 seconds
                    self.cleaned_endpoint = '/lol/match/v5/matches/'
                elif '/lol/match/v5/matches/by-puuid/' in self.riot_endpoint and '/ids' in self.riot_endpoint:
                    self.requests_number = '200'
                    self.time_period = 's'  # 2000 requests every 10 seconds
                    self.cleaned_endpoint = '/lol/match/v5/matches/by-puuid/'
                elif '/lol/match/v5/matches/' in self.riot_endpoint:
                    self.requests_number = '200'
                    self.time_period = 's'  # 2000 requests every 10 seconds
                    self.cleaned_endpoint = '/lol/match/v5/matches/'
                self.service = 'Match v5'


            # Set rate_string based on requests_number and time_period
            if self.requests_number and self.time_period:
                self.method_rate_string = f"{self.requests_number}/{self.time_period}"

        else:
            self.requests_number = '10'
            self.time_period = 's'
            self.cleaned_endpoint = os.environ["RIOT_KEY"]
            self.method_rate_string = '10/s' # 
            self.application_rate_string = '10/s'
            self.service = 'n/a'
          

    def application_rate_limit_key(self, *args, **kwargs):
        # Application wide rate limit per region
        return os.environ["RIOT_KEY"] + self.region

    def method_rate_limit_key(self, *args, **kwargs):
        # Endpoint + region specific rate limit
        return self.cleaned_endpoint + self.region
    
    # def service_rate_limit_key(self, *args, **kwargs):
    #     # Limit for an API service (group of endpoints)
    #     return self.service + self.region

    def get(self, url):
        # @ratelimit(key=self.application_rate_limit_key, rate=self.application_rate_string, method=ratelimit.ALL)
        # @ratelimit(key=self.method_rate_limit_key, rate=self.method_rate_string, method=ratelimit.ALL)
        @ratelimit(key=test_rate_limit_key, rate='2/h', method=ratelimit.ALL)
        @api_view(['GET'])
        def get_request(request, url):
            print("RATE LIMIT", self.method_rate_string)
            if not production and self.cleaned_endpoint == os.environ["RIOT_KEY"]:
                print("API KEY")
            else:
                print("REAL KEY", self.cleaned_endpoint)
            print("URL", url)

            response = requests.get(url, headers=headers)
            if response.status_code == 429:
                print("Likely Service Limited By Riot")

                ratelimit_type = response.headers.get('X-Rate-Limit-Type')
                retry_after = response.headers.get('Retry-After')
                details = json.dumps({"type": ratelimit_type, "retry_after": int(retry_after) + 1})
                cache.set("Rate Limit Received", details, timeout=int(retry_after) + 1)
                
                # if ratelimit_type == 'service':
                #     cache.set(f"service-{self.region}", details, timeout=int(retry_after) + 1)

                
                print(cache.get("Rate Limit Received"))
                # raise RiotRateLimitError(code=429, details=details, retry_after=int(retry_after) + 1)

            return response


        return get_request(self.request, url)
    

    ############ Continue working on 429 / service rate limit. 
    ############ Maybe make an app-wide request timeout if any 429 is received
    ############ But maybe I should be looking at the rate limit headers?
    ############ Currently not convinced that is necessary but the preventing of re-tries probably is
    ############ if I get a 429 or any other limit
    ### can get retry time here: https://hextechdocs.dev/rate-limiting/


