puuid = "f649YxVWblcWTKMjnLYAZTKlbH6b3iNEZXf9-HXZhxxJRBSQ-Zws7v6jErBh0tzyVS9VNo50FHK3rA"
accountid = "jbAmWLq4YfgQAZKr3hEdaFgcvt5Ixr2r7zXGV154-afa4Q1odW_ge2iD"
#summoner
summonerId = "ZANL-az6EkuuJc27gyzq8lkb4UrkpFTAisDG82lRU855N1qnDTfKhOyW-w"
# get ELO
url = "https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/" + ""


most_recent_game_me = "NA1_4934431330"



# def convert_platform_to_region(func):
#     def wrapper(request, *args, **kwargs):
#         region = ""
#         if request.query_params.get('platform') == "na1" or request.query_params.get('platform') == "oc1":
#             region+= "americas"
#         elif request.query_params.get('platform') == "kr1" or request.query_params.get('platform') == "jp1":
#             region+= "asia"
#         elif request.query_params.get('platform') == "euw1" or request.query_params.get('platform') == "eun1":
#             region+= "europe"
#         return func(request, region)
#     return wrapper

# # Helper Function to check database of existing summoner overviews before hitting Riot API
# @convert_platform_to_region
# def search_db_for_summoner_overview(request, region):
#     try:
#         summoner_overview = SummonerOverview.objects.get(gameName=request.query_params.get('gameName'), tagLine=request.query_params.get('tagLine'), region=region)
#         summoner_overview_serializer = SummonerOverviewSerializer(summoner_overview)
#         return Response(summoner_overview_serializer.data['overview'], status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
#     except SummonerOverview.DoesNotExist:
#         return None