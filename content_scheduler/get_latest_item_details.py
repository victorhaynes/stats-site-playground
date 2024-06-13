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


print("Starting item detail job...", datetime.now())



load_dotenv()


def get_and_upload_latest_item_details():
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
                    SELECT * from wrs_api_riotapiversion WHERE asset = 'items';
                """
                )
                last_saved_items_version = cursor.fetchone()[1]
            except TypeError:
                    last_saved_items_version = None
            except Exception as err:
                print(f"Error reading RiotApiVersion table: {repr(err)}")

        if update_required(latest_version=latest_version, last_saved_version=last_saved_items_version):
            print("update req")
            # Fetch (all) item(s).json from Riot Data Dragon
            url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/data/en_US/item.json"
            response = requests.get(url)
            if response.status_code == 200:
                all_items = response.json()["data"]

            # Bulk write all items
            with connection.cursor() as cursor:
                try:
                    print("Writing", len(all_items), "items...")
                    for item in all_items:
                        cursor.execute(
                        """
                            INSERT INTO wrs_api_item ("itemId", name, metadata)
                            VALUES (%s, %s, %s)
                            ON CONFLICT ("itemId") 
                            DO UPDATE SET 
                            name = EXCLUDED.name,
                            metadata = EXCLUDED.metadata;
                        """,
                        [int(item), all_items[item]["name"], json.dumps(all_items[item])])
                        print("Wrote", item, "successfully...")
                    connection.commit()
                    print("Commited items")
                except psycopg2.Error as err:
                    print(f"Error reading RiotApiVersion table: {repr(err)}")
                    connection.rollback()
                    raise


            # Update latest asset version for "items"
            with connection.cursor() as cursor:
                try:
                    cursor.execute(
                        """
                            INSERT INTO wrs_api_riotapiversion (asset, version)
                            VALUES ('items', %s)
                            ON CONFLICT (asset)
                            DO UPDATE SET
                            version = EXCLUDED.version;
                        """
                        ,[latest_version])
                    connection.commit()
                    print("Updated and committed item version")
                except psycopg2.Error as err:
                    print(f"Error reading RiotApiVersion table: {repr(err)}")
                    connection.rollback()
                    raise
        else:
            print("No update required...", datetime.now())

    except Exception as err:
        print(f"Issue attempting to check or get item details. Error: {repr(err)}")


get_and_upload_latest_item_details()