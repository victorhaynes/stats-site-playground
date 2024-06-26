from django.db import connection

def create_summoner_partitions_and_indexes(apps, schema_editor):
    with connection.cursor() as cursor:
        platform_codes = ('tr1', 'ph2', 'la1', 'tw2', 'la2', 'eun1', 'vn2', 'kr', 'oc1', 'na1', 'jp1', 'euw1', 'sg2', 'ru', 'th2', 'br1')

        print(f"\033[93mCreating partitions and indexes for Summoner table... \033[0m\n")

        for platform in platform_codes:
            cursor.execute("""      
                -- Create partition table
                CREATE TABLE wrs_api_summoner_{0} PARTITION OF wrs_api_summoner FOR VALUES IN (%s);
            """.format(platform), [platform])

def drop_summoner_partitions_and_indexes(apps, schema_editor):
    with connection.cursor() as cursor:
        platform_codes = ('tr1', 'ph2', 'la1', 'tw2', 'la2', 'eun1', 'vn2', 'kr', 'oc1', 'na1', 'jp1', 'euw1', 'sg2', 'ru', 'th2', 'br1')

        print(f"\033[93mDropping partitions and indexes for Summoner table... \033[0m\n")


        for platform in platform_codes:
            cursor.execute("""
                -- Drop partitions table
                DROP TABLE IF EXISTS wrs_api_summoner_{0} CASCADE;
            """.format(platform))