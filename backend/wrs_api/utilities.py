import json
from django.db import connection
from .models import Summoner, SummonerOverview


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


def ranked_badge(elo_dict):
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

ranked_tiers = {
    "U": 0,
    "I1": 1,
    "I2": 2,
    "I3": 3,
    "I4": 4,
    "B1": 5,
    "B2": 6,
    "B3": 7,
    "B4": 8,
    "S1": 9,
    "S2": 10,
    "S3": 11,
    "S4": 12,
    "G1": 13,
    "G2": 14,
    "G3": 15,
    "G4": 16,
    "P1": 17,
    "P2": 18,
    "P3": 19,
    "P4": 20,
    "E1": 21,
    "E2": 22,
    "E3": 23,
    "E4": 24,
    "D1": 25,
    "D2": 26,
    "D3": 27,
    "D4": 28,
    "M1": 29,
    "GM1": 30,
    "C1": 31
}




def get_summoner_matches(summoner: Summoner, count: int):
    sql =   """
                SELECT wrs_api_summonermatch."matchId", wrs_api_match.metadata
                FROM wrs_api_summonermatch 
                JOIN wrs_api_match ON wrs_api_summonermatch."matchId" = wrs_api_match."matchId"
                WHERE wrs_api_summonermatch.puuid = %s AND wrs_api_summonermatch.platform = %s
                ORDER BY wrs_api_summonermatch."matchId" DESC
                LIMIT %s;
            """
    with connection.cursor() as cursor:
        cursor.execute(sql,[summoner.puuid, summoner.platform.code, count])
        results = dictfetchall(cursor)
        return format_match_strings_as_json(results)


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







# class NestedLoopBreak(Exception):
#     pass










#     # Try to save all fetched/new match details at once & update the Summoner's most recent game. If any fail reject all.
#     # Need atomicity because match, match's join table, and summoner update must all succeed to be consistent
#     try:
#         with transaction.atomic():
#             with connection.cursor() as cursor:
#                 for match_detail in match_details_not_in_database:
#                     print("attempting to write match:", match_detail["metadata"]["matchId"])
#                     split_version = match_detail["info"]["gameVersion"].split('.',1)
#                     version = (split_version[0] + "." + split_version[1].split('.',1)[0])
#                     patch_tuple = Patch.objects.get_or_create(full_version=match_detail["info"]["gameVersion"], version=version, season_id=current_season)
#                     print("Created new patch:", patch_tuple[1])
#                     cursor.execute(
#                         """
#                             INSERT INTO wrs_api_match ("matchId", "queueId", "season_id", "patch", "platform", "metadata")
#                             VALUES (%s, %s, %s, %s, %s, %s);
#                         """
#                     ,[match_detail["metadata"]["matchId"], match_detail["info"]["queueId"], current_season.id, patch_tuple[0].full_version, request.query_params.get('platform'), json.dumps(match_detail)])
                    
#                     participants = match_detail["metadata"]["participants"]
#                     for participant_puuid in participants:
#                         # Check if participant already exists in database
#                         print("Checking existing profile for:", participant_puuid)
#                         participant_profile = Summoner.objects.filter(puuid=participant_puuid, platform=request.query_params.get('platform'))
#                         if len(participant_profile) == 0:
#                             # If not found GET Encrypted Summoner ID externally
#                             print("Getting ESID from Riot API for:", participant_puuid)
#                             encrypted_summonerID_by_puuid_url = f"https://{request.query_params.get('platform')}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{participant_puuid}"
#                             response_summonerID = requests.get(encrypted_summonerID_by_puuid_url, headers=headers, verify=True)
#                             if response_summonerID.status_code == 200:
#                                 participant_summonerID = response_summonerID.json()['id']
#                                 participant_profile_icon = response_summonerID.json()['profileIconId']
#                                 participant_stats = [d for d in match_detail["info"]["participants"] if d.get("puuid") == participant_puuid][0] 
#                                 participant_gameName = participant_stats["riotIdGameName"]
#                                 participant_tagLine = participant_stats["riotIdTagline"]
#                                 new_summoner = Summoner.objects.create(puuid=participant_puuid, gameName=participant_gameName, tagLine=participant_tagLine, platform=platform, profileIconId=participant_profile_icon, encryptedSummonerId=participant_summonerID)

#                                 # GET Summoner Overview / Ranked Stats / Elo
#                                 print("Getting ELO update for:", participant_puuid)
#                                 league_elo_by_summonerID_url = f"https://{request.query_params.get('platform')}.api.riotgames.com/lol/league/v4/entries/by-summoner/{participant_summonerID}"
#                                 response_overview = requests.get(league_elo_by_summonerID_url, headers=headers, verify=True)
                                
#                                 if response_account_details.status_code == 200:
#                                     participant_elo = {}
#                                     if response_overview.status_code == 200 and len(response_overview.json()) == 0:
#                                         participant_elo = json.dumps({"rank": "UNRANKED", "tier": "UNRANKED", "wins": 0, "losses": 0, "leaguePoints": 0})
#                                     else:
#                                         participant_elo = json.dumps(response_overview.json()[0])

#                                         print("Instering overview for:", participant_puuid)
#                                         cursor.execute(
#                                         """
#                                             INSERT INTO wrs_api_summoneroverview (puuid, platform, season_id, metadata, created_at, updated_at)
#                                             VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
#                                             ON CONFLICT (puuid, season_id, platform) 
#                                             DO UPDATE SET 
#                                             metadata = EXCLUDED.metadata,
#                                             updated_at = EXCLUDED.updated_at;
#                                         """
#                                         , [participant_puuid, platform.code, current_season.id, participant_elo])

#                             elif response_summonerID.status_code != 200:
#                                 raise HTTPError("Error Issued from Riot API")
#                             else:
#                                 raise Exception("Error fetching or creating Summoner.")
#                         cursor.execute(
#                             """
#                                 INSERT INTO wrs_api_summonermatch ("matchId", "queueId", "puuid", "season_id", "patch", "platform")
#                                 VALUES (%s, %s, %s, %s, %s, %s);
#                             """
#                         ,[match_detail["metadata"]["matchId"], match_detail["info"]["queueId"], participant_puuid, current_season.id, patch_tuple[0].full_version, request.query_params.get('platform')])

#                 cursor.execute(
#                     """
#                         SELECT "matchId" FROM wrs_api_summonermatch WHERE wrs_api_summonermatch.puuid = %s AND wrs_api_summonermatch.platform = %s
#                         ORDER BY wrs_api_summonermatch."matchId" DESC
#                         LIMIT 1;
#                     """
#                 ,[puuid, request.query_params.get('platform')])
#                 last_saved_game = cursor.fetchone()[0]
#                 if summoner_searched.most_recent_game != last_saved_game:
#                     summoner_searched.custom_update(most_recent_game=last_saved_game)
#                 print(last_saved_game)

#     except Exception as err:
#         return JsonResponse(f"Could not update databse. Error: {str(err)}", safe=False, status=status.HTTP_409_CONFLICT)


#     summoner_searched = Summoner.objects.get(puuid=puuid, platform=request.query_params.get('platform'))
#     serialized_summoner = SummonerCustomSerializer(summoner_searched)

#     return JsonResponse(serialized_summoner.data, safe=False, status=status.HTTP_202_ACCEPTED)





