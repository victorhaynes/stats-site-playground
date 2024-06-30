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
    filename='/var/log/icons/champion_icons_job.log',
    level=logging.DEBUG,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

logging.debug("Starting champ icon job...")


def main():
    try:
        s3 = boto3.client(
            's3',
            region_name='us-east-2',
            aws_access_key_id=os.environ["AWS_IAM_ACCESS_KEY"],
            aws_secret_access_key=os.environ["AWS_IAM_SECRET_ACCESS_KEY"]
        )
        
        bucket = 'wr-gg-images-bucket'
        patch_key = 'champion_icons/latestPatch.json'
        

        # try:
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
                # Download the tarball
                url = f"https://ddragon.leagueoflegends.com/cdn/dragontail-{latest_version}.tgz"
                response = requests.get(url)
                if response.status_code == 200:
                    with tarfile.open(fileobj=io.BytesIO(response.content)) as tar:
                        logging.info("successfully downloaded tarball")
                        for member in tar.getmembers():
                            # Check if the member is inside the f'{latest_version}/img/champion' directory
                            if member.name.startswith(f"{latest_version}/img/champion"):
                                # Extract the file to an in-memory buffer
                                file_obj = tar.extractfile(member)
                                if file_obj is not None:
                                    # Create a path in S3
                                    file_name = os.path.basename(member.name)
                                    s3_champ_key = f"champion_icons/{file_name}"
                                    # Upload the file to S3
                                    s3.put_object(Bucket=bucket, Key=s3_champ_key, Body=file_obj.read())
                                    logging.info(f"Uploaded {s3_champ_key} to S3")

                    s3.put_object(Bucket=bucket, Key=patch_key, Body=json.dumps({'version': latest_version}))
                    logging.info("Updated latest patch to:", latest_version,)

                else:
                    logging.error("Error Downloading .tgz file from Data Dragon")

            else:
                logging.warning("No champion icons update performed")

        else:
            logging.error("Error getting latest API version from Data Dragon.")
        
    except Exception as error:
        logging.error(f"An error occured: {repr(error)}")



if __name__ == "__main__":
    main()