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







    # START OVER WITH UPDATING OVERVIEW FUNCTION. SUPER WEIRD BEHAVIOR







    # # GET Summoner Overview / Ranked Stats / Elo
    # league_elo_by_summonerID_url = f"https://{request.query_params.get('platform')}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summonerID}"
    # response_overview = requests.get(league_elo_by_summonerID_url, headers=headers, verify=True)
    
    # # Handle case where there is no ranked history, json returned will be an empty list []
    # if response_account_details.status_code == 200:
    #     if response_overview.status_code == 200 and len(response_overview.json()) == 0:
    #         new_overview = {"tier": "UNRANKED", "rank": "UNRANKED", "leaguePoints": 0}
    #     else:
    #         new_overview = response_overview.json()[0]

    #     try:
    #         summoner_overviews = SummonerOverview.objects.raw(
    #             """
    #                 SELECT * FROM wrs_api_summoneroverview WHERE puuid = %s AND platform = %s AND season_id = %s;
    #                 ---UPDATE wrs_api_summoneroverview 
    #                 ---SET meta = '[99]' 
    #                 ---WHERE puuid = %s 
    #                 ---AND platform = %s 
    #                 ---AND season_id = %s
    #                 ---RETURNING *;
    #             """
    #         ,[summoner_searched.puuid, summoner_searched.platform.code, current_season.id])
            

    #         print(type(summoner_overviews[0]))

    #         # print(summoner_overviews[0])
    #         # current_season_overview.update_overview(new_overview)
    #         # refresh_overview(summoner_searched, new_overview)


    #         # return JsonResponse(serialized_overview.data, safe=False, status=status.HTTP_206_PARTIAL_CONTENT)
    #         return JsonResponse("hello", safe=False, status=status.HTTP_206_PARTIAL_CONTENT)

    #     except SummonerOverview.DoesNotExist:
    #         # summoner_overview = SummonerOverview.objects.create(puuid=summoner_searched.puuid, platform=platform, season_id=current_season, metadata=new_overview)
    #         pass
    # else:
    #     return Response({"this was returned from Riot API": response_account_details.json()}, status=response_account_details.status_code)





















    # updated_summonver_overview = SummonerOverview.objects.raw(
    #     """"
    #             UPDATE wrs_api_summoneroverview
    #             SET metadata = %s
    #             WHERE puuid = %s
    #             AND platform = %s
    #             AND season_id = %s
    #             RETURNING *;
    #     """, [updated_overview, summoner_overview.puuid, summoner_overview.platform.code, summoner_overview.season_id])[0]
    
    # return updated_summonver_overview

# # Consider ordering the table
# # apparently django will what partition to look at
# # : https://github.com/maxtepkeev/architect/issues/34
# # see if you can figure out how to view the SQL generated from the ORM methods
# # check on the speed of this, am I going directly to partitions? or am I doing something jank
# # if my queries aren't getting routed automatically-well, then use params to figure out what partition to query directly
# # https://docs.djangoproject.com/en/5.0/topics/db/sql/#:~:text=If%20you%20use%20string%20interpolation,at%20risk%20for%20SQL%20injection.
# @api_view(['GET'])
# def test_func(request):
#     players = Summoner.objects.first()
#     print(players.summoner_overviews)
#     # print(players.query)
#     # print(players.explain())
#     serialized_players = SummonerWithOverviewSerializer(players)

#     puuid = 'abc123'
#     sql = """
#             EXPLAIN SELECT *  FROM wrs_api_summoneroverview WHERE puuid = %s and platform = 'na1';
#         """
#     with connection.cursor() as cursor:
#         cursor.execute(sql,[puuid])
#         query_plan = cursor.fetchall()
#         pprint.pprint(query_plan)
#         test = dictfetchall(cursor)


#     # test = test[0]
#     # pprint.pprint(test)
#     # serialized_overview = SummonerOverviewSerializer(test)
#     # return Response(test, status=status.HTTP_202_ACCEPTED)
#     return Response("It worked!!!", status=status.HTTP_200_OK)

#     # return Response(serialized_players.data, status=status.HTTP_202_ACCEPTED)
#     try:
#         Summoner.objects.create(puuid=request.query_params.get('puuid'), gameName=request.query_params.get('gameName'), tagLine=request.query_params.get('tagLine'), region=request.query_params.get('region'), profileIconId=request.query_params.get('profileIconId'), encryptedSummonerId=request.query_params.get('encryptedSummonerId'))
#         return JsonResponse("It worked!!!", safe=False, status=status.HTTP_200_OK)
#     except error:
#         return JsonResponse(repr(error), safe=False, status=status.HTTP_400_BAD_REQUEST)
