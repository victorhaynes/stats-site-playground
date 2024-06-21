# Need items, champions, sum spells, runes (major, minor, mod)

# need to insert into riotapi version an old version of the riot api then similar to s3 logic,
# get and write to database if version is out of date

# break out riotapiversion into assetversion for each of the above categories
# also do the same for GameMode, get official/up to date game modes from riot
# consider giving them metadata

import psycopg2
from dotenv import load_dotenv
import os
import requests
from utilities import update_required
from datetime import datetime




# Note: using CD dragon over official link due to lack of details
# https://static.developer.riotgames.com/docs/lol/queues.json


print("Starting game modes detail job...", datetime.now())




load_dotenv()


def get_and_upload_latest_game_modes_details():
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
                    SELECT * from wrs_api_riotapiversion WHERE asset = 'game modes';
                """
                )
                last_saved_game_modes_version = cursor.fetchone()[1]
            except TypeError:
                    last_saved_game_modes_version = None
            except Exception as err:
                print(f"Error reading RiotApiVersion table: {repr(err)}")

        if update_required(latest_version=latest_version, last_saved_version=last_saved_game_modes_version):
            
            # Fetch (all) game modes(s).json from Community (CD) Dragon
            url = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/queues.json"
            response = requests.get(url)
            if response.status_code == 200:
                game_modes = response.json()

            # Bulk write all game modes
            with connection.cursor() as cursor:
                try:
                    print("Writing", len(game_modes), "game modes...")
                    for mode in game_modes:
                        cursor.execute(
                        """
                            INSERT INTO wrs_api_gamemode ("queueId", name)
                            VALUES (%s, %s)
                            ON CONFLICT ("queueId") 
                            DO UPDATE SET 
                            name = EXCLUDED.name;
                        """,
                        [int(mode), game_modes[mode]["shortName"]])
                        print("Wrote", game_modes[mode]["shortName"], "successfully...")
                    connection.commit()
                    print("Commited game modes")
                except psycopg2.Error as err:
                    print(f"Error writing to game modes: {repr(err)}")
                    connection.rollback()
                    raise


            # Update latest asset version for "game modes"
            with connection.cursor() as cursor:
                try:
                    cursor.execute(
                        """
                            INSERT INTO wrs_api_riotapiversion (asset, version)
                            VALUES ('game modes', %s)
                            ON CONFLICT (asset)
                            DO UPDATE SET
                            version = EXCLUDED.version;
                        """
                        ,[latest_version])
                    connection.commit()
                    print("Updated and committed game modes version")
                except psycopg2.Error as err:
                    print(f"Error reading RiotApiVersion table: {repr(err)}")
                    connection.rollback()
                    raise
        else:
            print("No update required...", datetime.now())

    except Exception as err:
        print(f"Issue attempting to check or get game modes details. Error: {repr(err)}")


get_and_upload_latest_game_modes_details()