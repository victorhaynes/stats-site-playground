# Need items, champions, sum spells, runes (major, minor, mod)

# need to insert into riotapi version an old version of the riot api then similar to s3 logic,
# get and write to database if version is out of date

# break out riotapiversion into assetversion for each of the above categories
# also do the same for GameMode, get official/up to date game modes from riot
# consider giving them metadata

import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os
import requests
from utilities import update_required
import json
from datetime import datetime


print("Starting summoner spell detail job...", datetime.now())



load_dotenv()


def get_and_upload_latest_summoner_spells_details():
    try:
        connection = psycopg2.connect(
            dbname=os.environ["DB_NAME"],
            user=os.environ["DB_USERNAME"],
            password=os.environ["DB_PASSWORD"],
            host=os.environ["DB_ADDRESS"],
            port=os.environ["DB_PORT"]
        )

        url = "https://ddragon.leagueoflegends.com/api/versions.json"
        response = requests.get(url)
        if response.status_code == 200:
            latest_version = response.json()[0]



        with connection.cursor() as cursor:
            try:
                cursor.execute(
                """
                    SELECT * from wrs_api_riotapiversion WHERE asset = 'summoner spells';
                """
                )
                last_saved_summoner_spells_version = cursor.fetchone()[1]
            except TypeError:
                    last_saved_summoner_spells_version = None
            except Exception as err:
                print(f"Error reading RiotApiVersion table: {repr(err)}")

        if update_required(latest_version=latest_version, last_saved_version=last_saved_summoner_spells_version):
            
            # Fetch (all) champion(s).json from Riot Data Dragon
            url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/data/en_US/summoner.json"
            response = requests.get(url)
            if response.status_code == 200:
                all_sums = response.json()["data"]

            # Bulk write all summoner spells
            with connection.cursor() as cursor:
                try:
                    print("Writing", len(all_sums), "summoner spells...")
                    for sum_spell in all_sums:
                        cursor.execute(
                        """
                            INSERT INTO wrs_api_summonerspell ("spellId", name, metadata)
                            VALUES (%s, %s, %s)
                            ON CONFLICT ("spellId") 
                            DO UPDATE SET 
                            name = EXCLUDED.name,
                            metadata = EXCLUDED.metadata;
                        """,
                        [int(all_sums[sum_spell]["key"]), all_sums[sum_spell]["name"], json.dumps(all_sums[sum_spell])])
                        print("Wrote", all_sums[sum_spell]["name"], "successfully...")
                    connection.commit()
                    print("Commited summoner spells")
                except psycopg2.Error as err:
                    print(f"Error writing to summoenr spells: {repr(err)}")
                    connection.rollback()
                    raise


            # Update latest asset version for "summoner spells"
            with connection.cursor() as cursor:
                try:
                    cursor.execute(
                        """
                            INSERT INTO wrs_api_riotapiversion (asset, version)
                            VALUES ('summoner spells', %s)
                            ON CONFLICT (asset)
                            DO UPDATE SET
                            version = EXCLUDED.version;
                        """
                        ,[latest_version])
                    connection.commit()
                    print("Updated and committed summoner spells version")
                except psycopg2.Error as err:
                    print(f"Error reading RiotApiVersion table: {repr(err)}")
                    connection.rollback()
                    raise
        else:
            print("No update required...", datetime.now())

    except Exception as err:
        print(f"Issue attempting to check or get summoner spells details. Error: {repr(err)}")


get_and_upload_latest_summoner_spells_details()