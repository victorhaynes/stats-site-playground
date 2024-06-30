import psycopg2
from dotenv import load_dotenv
import os
import requests
from utilities import update_required
import json
import logging

load_dotenv()

logging.basicConfig(
    filename='/var/log/game_content/champion_details_job.log',
    level=logging.DEBUG,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

logging.debug("Starting champion detail job...")


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
                    SELECT * from wrs_api_riotapiversion WHERE asset = 'champions';
                """
                )
                last_saved_champions_version = cursor.fetchone()[1]
            except TypeError:
                    last_saved_champions_version = None
            except Exception as err:
                logging.error(f"Error reading RiotApiVersion table: {repr(err)}")

        if update_required(latest_version=latest_version, last_saved_version=last_saved_champions_version):
            
            # Fetch (all) champion(s).json from Riot Data Dragon
            url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/data/en_US/champion.json"
            response = requests.get(url)
            if response.status_code == 200:
                all_champions = response.json()["data"]

            # Bulk write all champions
            with connection.cursor() as cursor:
                try:
                    logging.info("Writing", len(all_champions), "champions...")
                    for champ in all_champions:
                        cursor.execute(
                        """
                            INSERT INTO wrs_api_champion ("championId", name, metadata)
                            VALUES (%s, %s, %s)
                            ON CONFLICT ("championId") 
                            DO UPDATE SET 
                            name = EXCLUDED.name,
                            metadata = EXCLUDED.metadata;
                        """,
                        [int(all_champions[champ]["key"]), all_champions[champ]["name"], json.dumps(all_champions[champ])])
                        logging.error("Wrote", all_champions[champ]["name"], "successfully...")
                    connection.commit()
                    logging.info("Commited champions")
                except psycopg2.Error as err:
                    logging.error(f"Error writing to champions: {repr(err)}")
                    connection.rollback()
                    raise


            # Update latest asset version for "champions"
            with connection.cursor() as cursor:
                try:
                    cursor.execute(
                        """
                            INSERT INTO wrs_api_riotapiversion (asset, version)
                            VALUES ('champions', %s)
                            ON CONFLICT (asset)
                            DO UPDATE SET
                            version = EXCLUDED.version;
                        """
                        ,[latest_version])
                    connection.commit()
                    logging.info("Updated and committed champions version")
                except psycopg2.Error as err:
                    logging.error(f"Error reading RiotApiVersion table: {repr(err)}")
                    connection.rollback()
                    raise
        else:
            logging.warning("No update required...")

    except Exception as err:
        logging.error(f"Issue attempting to check or get champion details. Error: {repr(err)}")


if __name__ == "__main__":
    main()