import json
import boto3
import os
import requests
from dotenv import load_dotenv
import requests
from utilities import update_required
import logging

load_dotenv()

logging.basicConfig(
    filename='/var/log/icons/item_icons_job.log',
    level=logging.DEBUG,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

logging.debug("Starting item icon job...")



def main():

    try:
        s3 = boto3.client(
            's3',
            region_name='us-east-2',
            aws_access_key_id=os.environ["AWS_IAM_ACCESS_KEY"],
            aws_secret_access_key=os.environ["AWS_IAM_SECRET_ACCESS_KEY"]
        )
        
        bucket = 'wr-gg-images-bucket'
        destination_folder = 'item_icons'
        patch_key = 'item_icons/latestPatch.json'

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
                url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/data/en_US/item.json"
                response = requests.get(url)
                if response.status_code == 200:
                    all_items = response.json()["data"]
                    for item in all_items:
                        item_name = all_items[item]["name"]
                        item_icon_key = f"item_icons/{item}.png"
                        response = requests.get(f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/img/item/{item}.png")
                        if response.status_code == 200:
                            item_icon_png = response.content
                            s3.put_object(Body=item_icon_png, Bucket=bucket, Key=item_icon_key)
                            logging.info("Uploaded", item_icon_key, item_name, "to S3.")
                    s3.put_object(Bucket=bucket, Key=patch_key, Body=json.dumps({'version': latest_version}))
                    logging.info("Updated item latest patch to:", latest_version)

            else:
                logging.warning("No item icons update performed")
        else:
            logging.error("Error getting latest API version from Data Dragon.")

    except Exception as error:
        logging.error(f"An error occured: {repr(error)}")

if __name__ == "__main__":
    main()