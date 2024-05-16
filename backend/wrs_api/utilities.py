import json
from django.db import connection
from .models import Summoner, SummonerOverview
import os

# UTILITY METHOD TO "SERIALIZER" RAW UNMANAGED QUERY RESULTS AS A LIST OF DICTS
def dictfetchall(cursor):
    """
    Return all rows from a cursor as a dict.
    Assume the column names are unique.
    """
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


# Format string representation as JSON instead of string
def format_match_strings_as_json(match_history):
    for game in match_history:
        try:
            game["metadata"] = json.loads(game["metadata"])
        except KeyError:
            pass
    return match_history

# Format string representation as JSON instead of string
def format_overview_strings_as_json(overviews):
    for overview in overviews:
        try:
            overview["metadata"] = json.loads(overview["metadata"])
        except KeyError:
            pass
    return overviews


def ranked_badge(elo_dict: dict):
    rank = elo_dict["rank"] # Roman Numeral Integer
    tier = elo_dict["tier"][0] if elo_dict["tier"] != "GRANDMASTER" else "GM"

    roman_numeral_map = {
        "M": 1000,
        "CM": 900,
        "D": 500,
        "CD": 400,
        "C": 100,
        "XC": 90,
        "L": 50,
        "XL": 40,
        "X": 10,
        "IX": 9,
        "V": 5,
        "IV": 4,
        "I": 1,
    }

    if tier != "U": # Not an Unranked Player
        rank_number = 0
        i = 0
        while i < len(rank):
            if i + 1 < len(rank) and rank[i] in roman_numeral_map and rank[i + 1] in roman_numeral_map and roman_numeral_map[rank[i]] < roman_numeral_map[rank[i + 1]]:
                rank_number += roman_numeral_map[rank[i + 1]] - roman_numeral_map[rank[i]]
                i += 2
            else:
                rank_number += roman_numeral_map[rank[i]]
                i += 1
        badge = tier + str(rank_number)

    else:
        badge = "U"
        rank = "0"

    elo_dict["badge"] = badge

    return elo_dict

def calculate_average_elo(elos: list, queue: int):

    rank_scores = []
    ranked_tiers_map = {
        "U": 0,
        "I4": 1,
        "I3": 2,
        "I2": 3,
        "I1": 4,
        "B4": 5,
        "B3": 6,
        "B2": 7,
        "B1": 8,
        "S4": 9,
        "S3": 10,
        "S2": 11,
        "S1": 12,
        "G4": 13,
        "G3": 14,
        "G2": 15,
        "G1": 16,
        "P4": 17,
        "P3": 18,
        "P2": 19,
        "P1": 20,
        "E4": 21,
        "E3": 22,
        "E2": 23,
        "E1": 24,
        "D4": 25,
        "D3": 26,
        "D2": 27,
        "D1": 28,
        "M1": 29,
        "GM1": 30,
        "C1": 31
    }

    score_to_tier_map = {
        0: "Unranked",
        1: "Iron 4",
        2: "Iron 3",
        3: "Iron 2",
        4: "Iron 1",
        5: "Bronze 4",
        6: "Bronze 3",
        7: "Bronze 2",
        8: "Bronze 1",
        9: "Silver 4",
        10: "Silver 3",
        11: "Silver 2",
        12: "Silver 1",
        13: "Gold 4",
        14: "Gold 3",
        15: "Gold 2",
        16: "Gold 1",
        17: "Platinum 4",
        18: "Platinum 3",
        19: "Platinum 2",
        20: "Platinum 1",
        21: "Emerald 4",
        22: "Emerald 3",
        23: "Emerald 2",
        24: "Emerald 1",
        25: "Diamond 4",
        26: "Diamond 3",
        27: "Diamond 2",
        28: "Diamond 1",
        29: "Master",
        30: "Grandmaster",
        31: "Challenger"
    }

    for elo in elos:
        if elo != 0: # Ignore unranked players
            rank_scores.append(ranked_tiers_map[elo["badge"]])

    if len(elos) == 0: # If everyone is unranked return unranked
        return "Unranked"

    possible_smurf = min(rank_scores) # If a lower ranked player is placed in a much higher RANKED MODE do a lobby smurf check
    if queue == 420 and max(rank_scores) - possible_smurf >= 7:
        rank_scores.remove(possible_smurf)

    average_rank_score = round(sum(rank_scores) / len(rank_scores))
    average_tier = score_to_tier_map[average_rank_score]

    return average_tier
    




def test_rate_limit_key(self, *args, **kwargs):
    return "abc"



class RiotApiError(Exception):
    def __init__(self, error_response, error_code):
        self.error_response = error_response
        self.error_code = error_code


class RiotRateLimitApiError(Exception):
    def __init__(self, error_response, error_code):
        self.error_response = error_response
        self.error_code = error_code
        


# def get_summoner_matches(summoner: Summoner, count: int):
#     sql =   """
#                 SELECT wrs_api_summonermatch."matchId", wrs_api_match.metadata
#                 FROM wrs_api_summonermatch 
#                 JOIN wrs_api_match ON wrs_api_summonermatch."matchId" = wrs_api_match."matchId"
#                 WHERE wrs_api_summonermatch.puuid = %s AND wrs_api_summonermatch.platform = %s
#                 ORDER BY wrs_api_summonermatch."matchId" DESC
#                 LIMIT %s;
#             """
#     with connection.cursor() as cursor:
#         cursor.execute(sql,[summoner.puuid, summoner.platform.code, count])
#         results = dictfetchall(cursor)
#         return format_match_strings_as_json(results)


def refresh_overview():
# def refresh_overview(summoner, updated_overview):

    # test = summoner_overview.puuid
    # print(summoner.puuid)

    with connection.cursor() as cursor:
        cursor.execute(
            # """
            #     UPDATE wrs_api_summoneroverview
            #     SET metadata = %s
            #     WHERE puuid = %s
            #     AND platform = %s
            #     AND season_id = %s;
            # """,
            # [updated_overview, summoner_overview.puuid, summoner_overview.platform.code, summoner_overview.season_id]
        """
            UPDATE wrs_api_summoneroverview 
            SET metadata = '[9]' 
            WHERE "puuid" = 'f649YxVWblcWTKMjnLYAZTKlbH6b3iNEZXf9-HXZhxxJRBSQ-Zws7v6jErBh0tzyVS9VNo50FHK3rA' 
            RETURNING *;
        """
        )





def check_missing_items(build_list):
    # Calculate the number of elements needed to reach 6
    num_needed = 6 - len(build_list)
    
    # Add new elements and assign corresponding dummy itemId
    for i in range(num_needed):
        build_list.append(-(len(build_list) + 1))

    return build_list



