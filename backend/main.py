import requests
import pprint

# Basic Info
summoner_name = 'Enemy Graves'
riot_key = 'RGAPI-bd171f51-9070-4067-af73-a6f888faff55'
player_url = f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}'
headers = {'X-Riot-Token': riot_key}


# GET basic player profile
response_player = requests.get(player_url, headers=headers)
puuid = response_player.json()['puuid']
print("puuid: "+ puuid, "status: " + str(response_player.status_code))


# GET list of matches for a player
start = 0
count = 100 # must be <= 100
queue = "ranked"
matches_url = f'https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/f649YxVWblcWTKMjnLYAZTKlbH6b3iNEZXf9-HXZhxxJRBSQ-Zws7v6jErBh0tzyVS9VNo50FHK3rA/ids?start={start}&count={count}&type={queue}'
response_matches = requests.get(matches_url, headers=headers)
matches = response_matches.json()
# pprint.pprint(matches)


# GET details of a single match
match_id = matches[0]    
match_url=f'https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}'
response_match = requests.get(match_url, headers=headers)
match_detail = response_match.json()
# pprint.pprint(match_detail)

summoner_index = match_detail['metadata']['participants'].index(puuid)
summoner_performance = match_detail['info']['participants'][summoner_index]
# pprint.pp(summoner_performance)   