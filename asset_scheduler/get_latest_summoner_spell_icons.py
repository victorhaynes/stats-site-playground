import json
import boto3
import os
import requests
from dotenv import load_dotenv
import requests
from datetime import datetime
from botocore.exceptions import ClientError

load_dotenv()

# Ex. Compare 14.11.1 to 14.5.1 and determine which patch is "larger" (i.e. most recent)
def compare_latest_version_to_last_saved_version(latest_version, last_saved_version):
    # Split the 2 patch versions into parts
    latest_parts = [int(part) for part in latest_version.split('.')]
    saved_parts = [int(part) for part in last_saved_version.split('.')]
    
    # Compare the chunks one by one
    for latest_part, saved_part in zip(latest_parts, saved_parts):
        if latest_part < saved_part:
            return False  # latest_version is less than last_saved_version
        elif latest_part > saved_part:
            return True   # latest_version is greater than last_saved_version
    
    # If all compared parts are equal, check if one version has more parts
    if len(latest_parts) <= len(saved_parts):
        return False # latest_version is less than or equal to last_saved_version
    else:
        return True   # latest_version is greater than last_saved_version


# Note: unlike item icons & champion icons, summoner spell icons do not frequently change. So this function checks if exists first
# the goal is to reduce the number of writes to s3
def get_and_upload_latest_summoner_spell_icons():

    try:
        s3 = boto3.client(
            's3',
            region_name='us-east-2',
            aws_access_key_id=os.environ["AWS_IAM_ACCESS_KEY"],
            aws_secret_access_key=os.environ["AWS_IAM_SECRET_ACCESS_KEY"]
        )
        
        bucket = 'wr-gg-images-bucket'
        destination_folder = 'item_icons'
        patch_key = 'profile_icons/latestPatch.json'

        # GET latest game version from Riot Data Dragon
        url = "https://ddragon.leagueoflegends.com/api/versions.json"
        response = requests.get(url)
        if response.status_code == 200:
            latest_version = response.json()[0]

            # GET last saved game version from S3            
            response = s3.get_object(Bucket=bucket, Key=patch_key)
            file_content = response['Body'].read().decode('utf-8')
            last_saved_game_version = json.loads(file_content)['version']

            # Compare Latest Version to Last Saved Version
            if compare_latest_version_to_last_saved_version(latest_version, last_saved_game_version):
                # Fetch (all) item(s).json from Riot Data Dragon
                url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/data/en_US/summoner.json"
                response = requests.get(url)
                if response.status_code == 200:
                    all_sums = response.json()["data"]
                    for spell in all_sums:
                        summoner_spell_id_with_file_extention = f"{all_sums[spell]["key"]}.png"
                        summoner_spell_icon_key = f"summoner_spell_icons/{summoner_spell_id_with_file_extention}"

                        try:
                            s3.head_object(Bucket=bucket, Key=summoner_spell_icon_key)
                            print(f"{summoner_spell_icon_key} already exists. Skipping upload.")
                        except ClientError as err:
                            if err.response['Error']['Code'] == "404":
                                response = requests.get(f"https://ddragon.leagueoflegends.com/cdn/14.3.1/img/spell/{allSums[spell]['id']}.png")
                                if response.status_code == 200:
                                    profile_icon_png = response.content
                                    s3.put_object(Body=profile_icon_png, Bucket=bucket, Key=summoner_spell_icon_key)
                                    print("Uploaded", summoner_spell_id_with_file_extention, "to S3, _", datetime.now())
                            else:
                                raise 

                    s3.put_object(Bucket=bucket, Key=patch_key, Body=json.dumps({'version': latest_version}))
                    print("Updated item latest patch to:", latest_version)


            else:
                print("No profile icons update performed", datetime.now())
        else:
            print("Error getting latest API version from Data Dragon.", datetime.now())

    except Exception as error:
        print(f"An error occured: {repr(error)}")

get_and_upload_latest_summoner_spell_icons()


# update URL https://developer.riotgames.com/docs/lol#data-dragon_items
url = "https://ddragon.leagueoflegends.com/cdn/14.3.1/data/en_US/summoner.json"


count = 1
response = requests.get(url)
if response.status_code == 200:
    allSums = response.json()["data"]
    for sumspell in allSums:
        print(allSums[sumspell]["name"], count)
        path = f"./summoner_spell_icons/{allSums[sumspell]['key']}.png"
        res = requests.get(f"https://ddragon.leagueoflegends.com/cdn/14.3.1/img/spell/{allSums[sumspell]['id']}.png")
        if res.status_code == 200:
            with open(path, "wb") as file:
                file.write(res.content)
        else:
            print(res.status_code, res.content)
        count+=1
        time.sleep(0.1)