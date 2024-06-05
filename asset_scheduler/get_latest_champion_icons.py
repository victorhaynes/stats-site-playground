import json
import boto3
import os
import requests
import tarfile
import io
from dotenv import load_dotenv
from datetime import datetime
# requests provided by ARN arn:aws:lambda:us-east-2:770693421928:layer:Klayers-p310-arm64-requests:10
# https://github.com/keithrozario/Klayers?tab=readme-ov-file#list-of-arns


load_dotenv()

# Ex. Compare 14.11.1 to 14.5.1 and determine which patch is "larger"
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





def get_and_upload_latests_champ_icons():
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
            if compare_latest_version_to_last_saved_version(latest_version, last_saved_game_version):
                # Download the tarball
                url = f"https://ddragon.leagueoflegends.com/cdn/dragontail-{latest_version}.tgz"
                response = requests.get(url)
                if response.status_code == 200:
                    with tarfile.open(fileobj=io.BytesIO(response.content)) as tar:
                        print("successfully downloaded tarball")
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
                                    print(f"Uploaded {s3_champ_key} to S3 _", datetime.now())


                    # # Major and Minor Runes
                    # # Note: rune ids are not available in the data dragon .tgz file, must look them up directly form Riot 
                    # url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/data/en_US/runesReforged.json"
                    # response = requests.get(url)
                    # if response.status_code == 200:
                    #     all_runes_data = response.json()

                    #     rune_name_to_id_map = {}
                    #     for category in all_runes_data:
                    #         for slot in category['slots']:
                    #             for rune in slot['runes']:
                    #                 rune_key = rune['key']
                    #                 rune_id = rune['id']
                    #                 rune_name_to_id_map[rune_key] = rune_id


                    #     with tarfile.open(fileobj=io.BytesIO(response.content)) as tar:
                    #         for member in tar.getmembers():
                    #             if member.name.startswith(f"{latest_version}/img/perk-images/Styles") and member.name.endswith('.png'):
                    #                 file_obj = tar.extractfile(member)
                    #                 if file_obj is not None:
                    #                     file_name = os.path.basename(member.name)

                    #                     rune_name_no_file_extension = file_name.split('.')[0]

                    #                     rune_id_for_key = rune_name_to_id_map[rune_name_no_file_extension]

                    #                     s3_rune_key = f"major_and_minor_rune_icons/{rune_id_for_key}"
                    #                     s3.put_object(Bucket=bucket, Key=s3_rune_key, Body=file_obj.read())
                    #                     print(f"Uploaded {s3_champ_key} to S3 _", datetime.now())

                    s3.put_object(Bucket=bucket, Key=patch_key, Body=json.dumps({'version': latest_version}))
                    print("Updated latest patch to:", latest_version, "_", datetime.now())

                    # else:
                    #     print("Error fetching Champions json from Data Dragon", datetime.now())

                else:
                    print("Error Downloading .tgz file from Data Dragon", datetime.now())

            else:
                print("No champion icons update performed", datetime.now())

        else:
            print("Error getting latest API version from Data Dragon.", datetime.now())
        
    except Exception as error:
        print(f"An error occured: {repr(error)}")



get_and_upload_latests_champ_icons()




# import json
# import boto3
# import os
# import requests
# import tarfile
# import io
# import random
# from dotenv import load_dotenv

# # requests provided by ARN arn:aws:lambda:us-east-2:770693421928:layer:Klayers-p310-arm64-requests:10
# # https://github.com/keithrozario/Klayers?tab=readme-ov-file#list-of-arns




# load_dotenv()

# def get_and_upload_latests_champ_icons():


#     random_string = ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for i in range(5))

#     s3_client = boto3.client(
#         's3',
#         region_name='us-east-2',
#         aws_access_key_id=os.environ["AWS_IAM_ACCESS_KEY"],
#         aws_secret_access_key=os.environ["AWS_IAM_SECRET_ACCESS_KEY"]
#     )

#     print('the test is running')
#     s3_client.put_object(Bucket='wr-gg-images-bucket', Key='test', Body=json.dumps({"this is a test": f"{random_string}"}))


# get_and_upload_latests_champ_icons()



# # successfully uplodated "{"this is a test": "azhnt"}"!!!!!!!! download again in a minute