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
import json
import logging

load_dotenv()

logging.basicConfig(
    filename='/var/log/game_content/rune_details_job.log',
    level=logging.DEBUG,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

logging.debug("Starting runes detail job...")


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
                    SELECT * from wrs_api_riotapiversion WHERE asset = 'runes';
                """
                )
                last_saved_runes_version = cursor.fetchone()[1]
            except TypeError:
                    last_saved_runes_version = None
            except Exception as err:
                logging.error(f"Error reading RiotApiVersion table: {repr(err)}")

        if update_required(latest_version=latest_version, last_saved_version=last_saved_runes_version):
            # Fetch (all) runes(s).json from Riot Data Dragon
            url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/data/en_US/runesReforged.json"
            rune_response = requests.get(url)

            url = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/perks.json"
            perks_and_stat_mod_response = requests.get(url)


            if rune_response.status_code == 200 and perks_and_stat_mod_response.status_code == 200:
                # Parse all the runes
                all_runes_data = rune_response.json()
                # Extract keystones
                keystones_by_tree = [item['slots'][0]['runes'] for item in all_runes_data]

                all_keystones = [rune for sublist in keystones_by_tree for rune in sublist]
                # Extract minor runres
                minor_runes = [slot['runes'] for item in all_runes_data for slot in item['slots'][1:]]
                all_minor_runes = [rune for sublist in minor_runes for rune in sublist]

                # Parse response from Community Dragon
                all_cd_perks = perks_and_stat_mod_response.json()
                # Extract stat mods
                all_stat_mods = [d for d in all_cd_perks if "StatMods".lower() in d["iconPath"].lower()]

                # Bulk write all keystones
                with connection.cursor() as cursor:
                    try:
                        logging.info("Writing", len(all_keystones), "keystones...")
                        for keystone in all_keystones:
                            cursor.execute(
                            """
                                INSERT INTO wrs_api_keystone (keystone_id, name, metadata)
                                VALUES (%s, %s, %s)
                                ON CONFLICT ("keystone_id") 
                                DO UPDATE SET 
                                name = EXCLUDED.name,
                                metadata = EXCLUDED.metadata;
                            """,
                            [int(keystone["id"]), keystone["name"], json.dumps(keystone)])
                            logging.info("Wrote", keystone["name"], "successfully...")
                        connection.commit()
                        logging.info("Commited keystones")
                    except psycopg2.Error as err:
                        logging.error(f"Error writing to keystones table: {repr(err)}")
                        connection.rollback()
                        raise

                # Bulk write all minor runres, repeat for 
                # PrimaryPerkOne, PrimaryPerkTwo, PrimaryPerkThree
                # SecondaryPerkOne, SecondaryPerkTwo
                with connection.cursor() as cursor:
                    try:
                        logging.info("Writing", len(all_minor_runes), "minor runres (p1)...")
                        for rune in all_minor_runes:
                            cursor.execute(
                            """
                                INSERT INTO wrs_api_primaryperkone (perk_id, name, metadata)
                                VALUES (%s, %s, %s)
                                ON CONFLICT (perk_id) 
                                DO UPDATE SET 
                                name = EXCLUDED.name,
                                metadata = EXCLUDED.metadata;
                            """,
                            [int(rune["id"]), rune["name"], json.dumps(rune)])
                            logging.info("Wrote", rune["name"], "successfully...")
                        connection.commit()
                        logging.info("Commited primary perk ones")
                    except psycopg2.Error as err:
                        logging.error(f"Error writing to primary perk one table: {repr(err)}")
                        connection.rollback()
                        raise

                with connection.cursor() as cursor:
                    try:
                        logging.info("Writing", len(all_minor_runes), "minor runres (p2)...")
                        for rune in all_minor_runes:
                            cursor.execute(
                            """
                                INSERT INTO wrs_api_primaryperktwo (perk_id, name, metadata)
                                VALUES (%s, %s, %s)
                                ON CONFLICT (perk_id) 
                                DO UPDATE SET 
                                name = EXCLUDED.name,
                                metadata = EXCLUDED.metadata;
                            """,
                            [int(rune["id"]), rune["name"], json.dumps(rune)])
                            logging.info("Wrote", rune["name"], "successfully...")
                        connection.commit()
                        logging.info("Commited primary perk twos")
                    except psycopg2.Error as err:
                        logging.error(f"Error writing to primary perk two table: {repr(err)}")
                        connection.rollback()
                        raise

                with connection.cursor() as cursor:
                    try:
                        logging.info("Writing", len(all_minor_runes), "minor runres (p3)...")
                        for rune in all_minor_runes:
                            cursor.execute(
                            """
                                INSERT INTO wrs_api_primaryperkthree (perk_id, name, metadata)
                                VALUES (%s, %s, %s)
                                ON CONFLICT (perk_id) 
                                DO UPDATE SET 
                                name = EXCLUDED.name,
                                metadata = EXCLUDED.metadata;
                            """,
                            [int(rune["id"]), rune["name"], json.dumps(rune)])
                            logging.info("Wrote", rune["name"], "successfully...")
                        connection.commit()
                        logging.info("Commited primary perk threes")
                    except psycopg2.Error as err:
                        logging.error(f"Error writing to primary perk three table: {repr(err)}")
                        connection.rollback()
                        raise

                with connection.cursor() as cursor:
                    try:
                        logging.info("Writing", len(all_minor_runes), "minor runres (s1)...")
                        for rune in all_minor_runes:
                            cursor.execute(
                            """
                                INSERT INTO wrs_api_secondaryperkone (perk_id, name, metadata)
                                VALUES (%s, %s, %s)
                                ON CONFLICT (perk_id) 
                                DO UPDATE SET 
                                name = EXCLUDED.name,
                                metadata = EXCLUDED.metadata;
                            """,
                            [int(rune["id"]), rune["name"], json.dumps(rune)])
                            logging.info("Wrote", rune["name"], "successfully...")
                        connection.commit()
                        logging.info("Commited secondary perk ones")
                    except psycopg2.Error as err:
                        logging.error(f"Error writing to secondary perk two table: {repr(err)}")
                        connection.rollback()
                        raise

                with connection.cursor() as cursor:
                    try:
                        logging.info("Writing", len(all_minor_runes), "minor runres (s2)...")
                        for rune in all_minor_runes:
                            cursor.execute(
                            """
                                INSERT INTO wrs_api_secondaryperktwo (perk_id, name, metadata)
                                VALUES (%s, %s, %s)
                                ON CONFLICT (perk_id) 
                                DO UPDATE SET 
                                name = EXCLUDED.name,
                                metadata = EXCLUDED.metadata;
                            """,
                            [int(rune["id"]), rune["name"], json.dumps(rune)])
                            logging.info("Wrote", rune["name"], "successfully...")
                        connection.commit()
                        logging.info("Commited secondary perk twos")
                    except psycopg2.Error as err:
                        logging.error(f"Error writing to secondary perk two table: {repr(err)}")
                        connection.rollback()
                        raise

                # Write stat mods, repeat for StatShardOne, StatShardTwo, StatShardThree
                with connection.cursor() as cursor:
                    try:
                        logging.info("Writing", len(all_stat_mods), "stat mods (1)...")
                        for mod in all_stat_mods:
                            cursor.execute(
                            """
                                INSERT INTO wrs_api_statshardone (shard_id, name, metadata)
                                VALUES (%s, %s, %s)
                                ON CONFLICT (shard_id) 
                                DO UPDATE SET 
                                name = EXCLUDED.name,
                                metadata = EXCLUDED.metadata;
                            """,
                            [int(mod["id"]), mod["name"], json.dumps(mod)])
                            print("Wrote", mod["name"], "successfully...")
                        connection.commit()
                        logging.info("Commited stat mods (1)")
                    except psycopg2.Error as err:
                        logging.error(f"Error writing to stat mods (1) table: {repr(err)}")
                        connection.rollback()
                        raise

                with connection.cursor() as cursor:
                    try:
                        logging.info("Writing", len(all_stat_mods), "stat mods (2)...")
                        for mod in all_stat_mods:
                            cursor.execute(
                            """
                                INSERT INTO wrs_api_statshardtwo (shard_id, name, metadata)
                                VALUES (%s, %s, %s)
                                ON CONFLICT (shard_id) 
                                DO UPDATE SET 
                                name = EXCLUDED.name,
                                metadata = EXCLUDED.metadata;
                            """,
                            [int(mod["id"]), mod["name"], json.dumps(mod)])
                            print("Wrote", mod["name"], "successfully...")
                        connection.commit()
                        logging.info("Commited stat mods (2)")
                    except psycopg2.Error as err:
                        logging.error(f"Error writing to stat mods (2) table: {repr(err)}")
                        connection.rollback()
                        raise

                with connection.cursor() as cursor:
                    try:
                        logging.info("Writing", len(all_stat_mods), "stat mods (3)...")
                        for mod in all_stat_mods:
                            cursor.execute(
                            """
                                INSERT INTO wrs_api_statshardthree (shard_id, name, metadata)
                                VALUES (%s, %s, %s)
                                ON CONFLICT (shard_id) 
                                DO UPDATE SET 
                                name = EXCLUDED.name,
                                metadata = EXCLUDED.metadata;
                            """,
                            [int(mod["id"]), mod["name"], json.dumps(mod)])
                            logging.info("Wrote", mod["name"], "successfully...")
                        connection.commit()
                        logging.info("Commited stat mods (3)")
                    except psycopg2.Error as err:
                        logging.error(f"Error writing to stat mods (3) table: {repr(err)}")
                        connection.rollback()
                        raise

            # Update latest asset version for "champions"
            with connection.cursor() as cursor:
                try:
                    cursor.execute(
                        """
                            INSERT INTO wrs_api_riotapiversion (asset, version)
                            VALUES ('runes', %s)
                            ON CONFLICT (asset)
                            DO UPDATE SET
                            version = EXCLUDED.version;
                        """
                        ,[latest_version])
                    connection.commit()
                    logging.info("Updated and committed runes version")
                except psycopg2.Error as err:
                    logging.error(f"Error reading RiotApiVersion table: {repr(err)}")
                    connection.rollback()
                    raise
        else:
            logging.warning("No update required...")

    except Exception as err:
        logging.error(f"Issue attempting to check or get runes details. Error: {repr(err)}")


if __name__ == "__main__":
    main()