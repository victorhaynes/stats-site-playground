# import requests
import pprint
# import secret

# # # Basic Info
# summoner_name = 'Enemy Graves'
# riot_key = secret.riot_key
# player_url = f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}'
# headers = {'X-Riot-Token': riot_key}

# region = "americas"
# platform = "na1"
# gameName = "vanilli vanilli"
# tagLine = "vv2"

# # GET basic player profile
# response_player = requests.get(player_url, headers=headers, verify=True)
# puuid = response_player.json()['puuid']
# print("puuid: "+ puuid, "status: " + str(response_player.status_code))


# # GET list of matches for a player
# start = 0
# count = 100 # must be <= 100
# queue = "ranked"
# matches_url = f'https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/f649YxVWblcWTKMjnLYAZTKlbH6b3iNEZXf9-HXZhxxJRBSQ-Zws7v6jErBh0tzyVS9VNo50FHK3rA/ids?start={start}&count={count}&type={queue}'
# response_matches = requests.get(matches_url, headers=headers)
# matches = response_matches.json()
# pprint.pprint(matches)


# # GET details of a single match
# # match_id = matches[0]
# match_id = secret.ex_list_of_matches[0]
# match_url=f'https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}'
# response_match = requests.get(match_url, headers=headers)
# match_detail = response_match.json()
# # pprint.pprint(match_detail)

# # summoner_index = match_detail['metadata']['participants'].index(puuid)
# # summoner_performance = match_detail['info']['participants'][summoner_index]
# # # pprint.pp(summoner_performance)   


# # account_by_gameName_tagLine_url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}"
# # response_account_details = requests.get(account_by_gameName_tagLine_url, headers=headers, verify=True)
# # puuid = response_account_details.json()['puuid']

# # encrypted_summonerID_by_puuid_url = f"https://{platform}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
# # response_summonerID = requests.get(encrypted_summonerID_by_puuid_url, headers=headers, verify=True)
# # summonerID = response_summonerID.json()['id']

# # league_elo_by_summonerID_url = f"https://{platform}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summonerID}"
# # response_overview = requests.get(league_elo_by_summonerID_url, headers=headers, verify=True)
# # overview = response_overview.json()[0]

# # print(overview)

import requests

# Fetch JSON data from the URL
url = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/perks.json"
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Convert JSON data to a Python dictionary
    perks_data = response.json()

    # Extract id to name mapping
    id_to_name_mapping = {perk['id']: perk['name'] for perk in perks_data}

    # Print the mapping
    print(id_to_name_mapping)
else:
    print("Failed to fetch data. Status code:", response.status_code)

ans = {8369: 'First Strike', 8446: 'Demolish', 8126: 'Cheap Shot', 8321: "Future's Market", 8415: 'The Arcane Colossus', 8410: 'Approach Velocity', 8232: 'Waterwalking', 8299: 'Last Stand', 8112: 'Electrocute', 8234: 'Celerity', 8453: 'Revitalize', 8360: 'Unsealed Spellbook', 8004: 'The Brazen Perfect', 8128: 'Dark Harvest', 8220: 'The Calamity', 8016: 'The Merciless Elite', 8473: 'Bone Plating', 8339: 'Celestial Body', 8214: 'Summon Aery', 8237: 'Scorch', 8139: 'Taste of Blood', 8008: 'Lethal Tempo', 9105: 'Legend: Tenacity', 8010: 'Conqueror', 8106: 'Ultimate Hunter', 8017: 'Cut Down', 8224: 'Nullifying Orb', 8210: 'Transcendence', 8005: 'Press the Attack', 8435: 'Mirror Shell', 8115: 'The Aether Blade', 8359: 'Kleptomancy', 8352: 'Time Warp Tonic', 5003: 'Magic Resist', 8135: 'Treasure Hunter', 8120: 'Ghost Poro', 8134: 'Ingenious Hunter', 8351: 'Glacial Augment', 8242: 'Unflinching', 8401: 'Shield Bash', 9111: 'Triumph', 8105: 'Relentless Hunter', 8454: 'The Leviathan', 8275: 'Nimbus Cloak', 8207: 'The Cryptic', 5012: 'Resist Scaling', 8439: 'Aftershock', 8109: 'The Wicked Maestro ', 5002: 'Armor', 5011: 'Health', 5013: 'Tenacity and Slow Resist', 8414: 'The Behemoth', 5008: 'Adaptive Force', 8320: 'The Timeless', 8319: 'The Stargazer', 5001: 'Health Scaling', 8430: 'Iron Skin', 8014: 'Coup de Grace', 5007: 'Ability Haste', 8021: 'Fleet Footwork', 8226: 'Manaflow Band', 8451: 'Overgrowth', 8313: 'Triple Tonic', 9103: 'Legend: Bloodline', 8114: 'The Immortal Butcher', 8230: 'Phase Rush', 8318: 'The Ruthless Visionary', 8316: 'Minion Dematerializer', 8463: 'Font of Life', 7000: 'Template', 8304: 'Magical Footwear', 8236: 'Gathering Storm', 8009: 'Presence of Mind', 8006: 'The Eternal Champion', 9104: 'Legend: Alacrity', 8416: 'The Enlightened Titan', 5005: 'Attack Speed', 8306: 'Hextech Flashtraption', 8465: 'Guardian', 8138: 'Eyeball Collection', 5010: 'Move Speed', 8127: 'The Twisted Surgeon', 8143: 'Sudden Impact', 8345: 'Biscuit Delivery', 8444: 'Second Wind', 8205: 'The Incontestable Spellslinger', 8437: 'Grasp of the Undying', 9923: 'Hail of Blades', 8429: 'Conditioning', 8124: 'Predator', 8233: 'Absolute Focus', 8007: 'The Savant', 8136: 'Zombie Ward', 8208: 'The Ancient One', 8347: 'Cosmic Insight', 8472: 'Chrysalis', 8229: 'Arcane Comet', 8344: 'The Elegant Duelist ', 9101: 'Overheal'}



