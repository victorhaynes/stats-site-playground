import json
import boto3
import os
import requests
from dotenv import load_dotenv
import requests
from datetime import datetime
from botocore.exceptions import ClientError
from utilities import update_required

print("Starting summoner spell icon job...", datetime.now())


load_dotenv()



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
            if update_required(latest_version, last_saved_game_version):
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
                print("No profile summoner spell update performed", datetime.now())
        else:
            print("Error getting latest API version from Data Dragon.", datetime.now())

    except Exception as error:
        print(f"An error occured: {repr(error)}")

get_and_upload_latest_summoner_spell_icons()


