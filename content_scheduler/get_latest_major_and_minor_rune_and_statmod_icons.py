import json
import boto3
import os
import requests
import tarfile
import io
from dotenv import load_dotenv
from datetime import datetime
from utilities import compare_latest_version_to_last_saved_version
# requests provided by ARN arn:aws:lambda:us-east-2:770693421928:layer:Klayers-p310-arm64-requests:10
# https://github.com/keithrozario/Klayers?tab=readme-ov-file#list-of-arns

print("Starting rune & stat mod icon job...", datetime.now())


load_dotenv()




def get_and_uploadlatest_major_rune_minor_rune_stat_mod_icons():
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
            if compare_latest_version_to_last_saved_version(latest_version, last_saved_game_version):
                # Download the tarball
                url = f"https://ddragon.leagueoflegends.com/cdn/dragontail-{latest_version}.tgz"
                print("Getting tarbal")
                tgz_response = requests.get(url)
                if tgz_response.status_code == 200:

                    # Major and Minor Runes
                    # Note: rune ids are not available in the data dragon .tgz file, must look them up directly form Riot 
                    url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/data/en_US/runesReforged.json"
                    runes_response = requests.get(url)

                    url = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/perks.json"
                    perks_and_stat_mod_response = requests.get(url)

                    if runes_response.status_code == 200 and perks_and_stat_mod_response.status_code == 200:
                        print("Got runes and stat mods json")
                        all_runes_data = runes_response.json()

                        rune_icon_name_to_id_filename_map = {}
                        for category in all_runes_data:
                            for slot in category['slots']:
                                for rune in slot['runes']:
                                    rune_key = rune['key']
                                    rune_id = rune['id']
                                    rune_icon_name_to_id_filename_map[rune_key] = rune_id


                        all_cd_perks = perks_and_stat_mod_response.json()
                        print("here", all_cd_perks[0:2])

                        all_stat_mods = [d for d in all_cd_perks if "StatMods".lower() in d["iconPath"].lower()]
                        print("here", all_stat_mods)
                        stat_mod_icon_name_to_id_filename_map = {}
                        for mod in all_stat_mods:
                            stat_mod_name_with_file_extension = mod["iconPath"].split("/StatMods/")[-1].lower()
                            stat_mod_icon_name_to_id_filename_map[stat_mod_name_with_file_extension] = mod["id"]

                        with tarfile.open(fileobj=io.BytesIO(tgz_response.content)) as tar:
                            for member in tar.getmembers():
                                if member.name.startswith(f"img/perk-images/Styles") and member.name.endswith('.png'):
                                    print("inside", member.name)
                                    file_obj = tar.extractfile(member)
                                    if file_obj is not None:
                                        file_name = os.path.basename(member.name)

                                        rune_name_no_file_extension = file_name.split('.')[0]

                                        try:
                                            rune_id_for_key = rune_icon_name_to_id_filename_map[rune_name_no_file_extension]
                                        except KeyError:
                                            rune_id_for_key = rune_name_no_file_extension

                                        s3_rune_key = f"major_and_minor_rune_icons/{rune_id_for_key}.png"
                                        print(s3_rune_key)
                                        s3.put_object(Bucket=bucket, Key=s3_rune_key, Body=file_obj.read())
                                        print(f"Uploaded {s3_rune_key} to S3 _", datetime.now())

                                if member.name.startswith(f"img/perk-images/StatMods") and member.name.endswith('.png'):

                                    stat_mod_icon_name = member.name.split("/StatMods/")[-1].lower()
                                    print("inside", member.name)
                                    print(stat_mod_icon_name)
                                    file_obj = tar.extractfile(member)
                                    print(stat_mod_icon_name_to_id_filename_map)
                                    if file_obj is not None:                                        
                                        stat_mod_file_name_for_key = stat_mod_icon_name_to_id_filename_map[stat_mod_icon_name]


                                        s3_mod_key = f"major_and_minor_rune_icons/{stat_mod_file_name_for_key}.png"
                                        print(s3_mod_key)
                                        s3.put_object(Bucket=bucket, Key=s3_mod_key, Body=file_obj.read())
                                        print(f"Uploaded {s3_mod_key} to S3 _", datetime.now())




                        s3.put_object(Bucket=bucket, Key=patch_key, Body=json.dumps({'version': latest_version}))
                        print("Updated latest patch to:", latest_version, "_", datetime.now())

                    else:
                        print("Error fetching runes json from Data Dragon or stat mods from Community Dragon", datetime.now())

                else:
                    print("Error Downloading .tgz file from Data Dragon", datetime.now())

            else:
                print("No rune icons update performed", datetime.now())

        else:
            print("Error getting latest API version from Data Dragon.", datetime.now())
        
    except Exception as error:
        print(f"An error occured: {repr(error)}")



get_and_uploadlatest_major_rune_minor_rune_stat_mod_icons()



