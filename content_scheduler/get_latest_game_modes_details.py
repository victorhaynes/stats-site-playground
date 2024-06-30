import psycopg2
from dotenv import load_dotenv
import os
import requests
from utilities import update_required
import logging

load_dotenv()

logging.basicConfig(
    filename='/var/log/game_content/game_mode_details_job.log',
    level=logging.DEBUG,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

logging.debug("Starting game modes detail job...")


# Note: using CD dragon over official link due to lack of details
# https://static.developer.riotgames.com/docs/lol/queues.json



def main():
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
                logging.error(f"Error reading RiotApiVersion table: {repr(err)}")

        if update_required(latest_version=latest_version, last_saved_version=last_saved_game_modes_version):
            
            # Fetch (all) game modes(s).json from Community (CD) Dragon
            url = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/queues.json"
            response = requests.get(url)
            if response.status_code == 200:
                game_modes = response.json()

            # Bulk write all game modes
            with connection.cursor() as cursor:
                try:
                    logging.info("Writing", len(game_modes), "game modes...")
                    for mode in game_modes:
                        cursor.execute(
                        """
                            INSERT INTO wrs_api_gamemode ("queueId", name)
                            VALUES (%s, %s)
                            ON CONFLICT ("queueId") 
                            DO UPDATE SET 
                            name = EXCLUDED.name;
                        """,
                        [int(mode["id"]), mode["shortName"]])
                        logging.info("Wrote", mode["shortName"], "successfully...")
                    connection.commit()
                    logging.info("Commited game modes")
                except psycopg2.Error as err:
                    logging.error(f"Error writing to game modes: {repr(err)}")
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
                    logging.info("Updated and committed game modes version")
                except psycopg2.Error as err:
                    print(f"Error reading RiotApiVersion table: {repr(err)}")
                    connection.rollback()
                    raise
        else:
            logging.warning("No update required...")

    except Exception as err:
        logging.error(f"Issue attempting to check or get game modes details. Error: {repr(err)}")


if __name__ == "__main__":
    main()