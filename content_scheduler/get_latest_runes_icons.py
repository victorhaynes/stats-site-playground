import json
import boto3
import os
import requests
import tarfile
import io
from dotenv import load_dotenv
from utilities import update_required
import logging

load_dotenv()

logging.basicConfig(
    filename='/var/log/icons/rune_icons_job.log',
    level=logging.DEBUG,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

logging.debug("Starting rune & stat mod icon job...")


def main():
    try:
        s3 = boto3.client(
            's3',
            region_name='us-east-2',
            aws_access_key_id=os.environ["AWS_IAM_ACCESS_KEY"],
            aws_secret_access_key=os.environ["AWS_IAM_SECRET_ACCESS_KEY"]
        )
        
        bucket = 'wr-gg-images-bucket'
        patch_key = 'major_and_minor_rune_icons/latestPatch.json'
        

        # try:
        # GET latest game version from Riot Data Dragon
        url = "https://ddragon.leagueoflegends.com/api/versions.json"
        version_response = requests.get(url)
        if version_response.status_code == 200:
            latest_version = version_response.json()[0]

            # GET last saved game version from S3            
            last_saved_patch_response = s3.get_object(Bucket=bucket, Key=patch_key)
            file_content = last_saved_patch_response['Body'].read().decode('utf-8')
            last_saved_game_version = json.loads(file_content)['version']

            # Compare Latest Version to Last Saved Version
            if update_required(latest_version, last_saved_game_version):
                # Download the tarball
                url = f"https://ddragon.leagueoflegends.com/cdn/dragontail-{latest_version}.tgz"
                logging.info("Getting tarbal")
                tgz_response = requests.get(url)
                if tgz_response.status_code == 200:

                    # Major and Minor Runes
                    # Note: rune ids are not available in the data dragon .tgz file, must look them up with Community Dragon 
                    url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/data/en_US/runesReforged.json"
                    runes_response = requests.get(url)

                    url = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/perks.json"
                    perks_and_stat_mod_response = requests.get(url)

                    if runes_response.status_code == 200 and perks_and_stat_mod_response.status_code == 200:
                        logging.info("Got runes and stat mods json")
                        all_runes_data = runes_response.json()

                        rune_icon_name_to_id_filename_map = {}
                        for category in all_runes_data:
                            for slot in category['slots']:
                                for rune in slot['runes']:
                                    rune_key = rune['key']
                                    rune_id = rune['id']
                                    rune_icon_name_to_id_filename_map[rune_key] = rune_id


                        all_cd_perks = perks_and_stat_mod_response.json()
                        all_stat_mods = [d for d in all_cd_perks if "StatMods".lower() in d["iconPath"].lower()]
                        stat_mod_icon_name_to_id_filename_map = {}
                        for mod in all_stat_mods:
                            stat_mod_name_with_file_extension = mod["iconPath"].split("/StatMods/")[-1].lower()
                            stat_mod_icon_name_to_id_filename_map[stat_mod_name_with_file_extension] = mod["id"]

                        with tarfile.open(fileobj=io.BytesIO(tgz_response.content)) as tar:
                            for member in tar.getmembers():
                                if member.name.startswith(f"img/perk-images/Styles") and member.name.endswith('.png'):
                                    file_obj = tar.extractfile(member)
                                    if file_obj is not None:
                                        file_name = os.path.basename(member.name)

                                        rune_name_no_file_extension = file_name.split('.')[0]

                                        try:
                                            rune_id_for_key = rune_icon_name_to_id_filename_map[rune_name_no_file_extension]
                                        except KeyError:
                                            rune_id_for_key = rune_name_no_file_extension

                                        s3_rune_key = f"major_and_minor_rune_icons/{rune_id_for_key}.png"
                                        s3.put_object(Bucket=bucket, Key=s3_rune_key, Body=file_obj.read())
                                        logging.info(f"Uploaded {s3_rune_key} to S3 _")

                                if member.name.startswith(f"img/perk-images/StatMods") and member.name.endswith('.png'):

                                    stat_mod_icon_name = member.name.split("/StatMods/")[-1].lower()
                                    file_obj = tar.extractfile(member)
                                    if file_obj is not None:                                        
                                        stat_mod_file_name_for_key = stat_mod_icon_name_to_id_filename_map[stat_mod_icon_name]


                                        s3_mod_key = f"major_and_minor_rune_icons/{stat_mod_file_name_for_key}.png"
                                        s3.put_object(Bucket=bucket, Key=s3_mod_key, Body=file_obj.read())
                                        logging.info(f"Uploaded {s3_mod_key} to S3 _")




                        s3.put_object(Bucket=bucket, Key=patch_key, Body=json.dumps({'version': latest_version}))
                        logging.info("Updated latest patch to:", latest_version, "_")

                    else:
                        logging.error("Error fetching runes json from Data Dragon or stat mods from Community Dragon")

                else:
                    logging.error("Error Downloading .tgz file from Data Dragon")

            else:
                logging.warning("No rune icons update performed")

        else:
            logging.error("Error getting latest API version from Data Dragon.")
        
    except Exception as error:
        logging.info(f"An error occured: {repr(error)}")



if __name__ == "__main__":
    main()



