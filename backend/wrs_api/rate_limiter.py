from django_ratelimit.decorators import ratelimit
import requests
import os

headers = {'X-Riot-Token': os.environ["RIOT_KEY"]}
production = False if os.environ["PRODUCTION"] == 'false' else True

# Add region or platform to the key eventually
class RiotRateLimiter:
    def __init__(self, riot_endpoint):
        self.riot_endpoint = riot_endpoint
        self.requests_number = None
        self.time_period = None
        self.cleaned_endpoint = None
        self.rate_string = None

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

            # LEAGUE EXP V4
            elif '/lol/league-exp/v4/' in self.riot_endpoint:
                if '/lol/league-exp/v4/entries/' in self.riot_endpoint:
                    self.requests_number = '3'
                    self.time_period = 'h'  # 50 requests every 10 seconds
                    self.cleaned_endpoint = '/lol/league-exp/v4/entries/'

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


            # Set rate_string based on requests_number and time_period
            if self.requests_number and self.time_period:
                self.rate_string = f"{self.requests_number}/{self.time_period}"

        else:
            self.requests_number = '10'
            self.time_period = 's'
            self.cleaned_endpoint = os.environ["RIOT_KEY"]
            self.rate_string = '10/s'           

    def rate_limit_key(self, *args, **kwargs):
        # should this be a concatenation including region & platform?
        return self.cleaned_endpoint

    def get(self, url):
        @ratelimit(key=self.rate_limit_key, rate=self.rate_string, method=ratelimit.ALL)
        def get_request(request, url):
            print("RATE LIMIT", self.rate_string)
            if not production and self.cleaned_endpoint == os.environ["RIOT_KEY"]:
                print("API KEY")
            else:
                print("REAL KEY", self.cleaned_endpoint)
            print("URL", url)
            return requests.get(url, headers=headers)
        
        return get_request(requests, url)