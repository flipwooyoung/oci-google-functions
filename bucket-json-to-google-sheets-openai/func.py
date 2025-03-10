import os.path

import google.oauth2.credentials
import google_auth_oauthlib.flow
from google.oauth2 import service_account
from googleapiclient.discovery import build
import google.auth

import io
import os
import json
import sys
import logging
from fdk import response
from openai import OpenAI
import oci.object_storage

# Modify this to whatever scope you require from google API. The current configuration allows read/write access for Google SHEETS
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

#Change this to your bucket name
BUCKET_NAME = "oci_speech_output_bucket"

# The ID of your sheet. Go to the git repo to see how to get your document ID. Only change the SAMPLE_RANGE_NAME if you want to change the column affected.
SAMPLE_SPREADSHEET_ID = "1-6l-5nAjUhwbOY8JwiOL1H724GKpFel0_81SweCUHUI"

#Only change the SAMPLE_RANGE_NAME if you want to change the column affected. Make sure to put {sheet_name}!A1 without the {}, iF your sheet name isn't Sheet1
SAMPLE_RANGE_NAME = "Sheet1!A1"

#By default you don't need to change this unless you changed the service_account.json location. Change this if you have.
SERVICE_ACCOUNT_PATH = "service_account.json"

#Change this if you want to change how the GPT model should function.
#GPT_PROMPT = "You will be given a paragraph about a foosball match narration. Clean it up to be appropriate, politically friendly, without changing the content or length at all."
GPT_PROMPT = "You will be given a paragraph. Make it grammatically correct and make sense, without changing the length or context of the paragraph too much. Make it politically correct and family friendly."

#This automatically gets added if you add in your api key from the readme
API_KEY_STRING = os.environ['openai_yuka']
#If your too lazy (Heavily recommended you dont do this), uncomment the next line
#API_KEY_STRING = "your_api_key"

def handler(ctx, data: io.BytesIO=None):
    data_bytes = data.getvalue()
    data_str = data_bytes.decode('utf-8')
    resp   = ""
    
    try:
        data_bytes = data.getvalue()
        data_str = data_bytes.decode('utf-8')
        data_object = None
        
        if data_str == "": #This method is mainly used when invoking without OCI Events
            logging.getLogger().info(f'Function invoked with OCI Events, getting latest object from {BUCKET_NAME}')
            data_object = list_latest_object(BUCKET_NAME)
        else:
            data_json = json.loads(data.getvalue())
            logging.getLogger().info(json.dumps(data_json))
            data_namespace = data_json["data"]["additionalDetails"]["namespace"]
            data_source_bucket = data_json["data"]["additionalDetails"]["bucketName"]
            data_object = data_json["data"]["resourceName"]
            logging.getLogger().info(f'Copying {data_object} from {data_source_bucket} to Google Sheets')
            
            if str(data_object).lower().endswith(".json"):
                logging.getLogger().info(f'JSON validation works')
            else:
                logging.getLogger().info(f"Most recent object is not a json, so this function doesn't work")
                data_object = None
    except (Exception, ValueError) as ex:
        logging.getLogger().error(str(ex))

    try:
        if data_object == None:
            logging.getLogger().info(f"Wasn't able to extract object properly")
        else:
            logging.getLogger().info(f"Extracting contents of object {data_object}")
            text_message = get_object_content(BUCKET_NAME, data_object)
            #text_message = openai_transform(text_prompt)
            resp = google_sheets_append_json(text_message)
    except (Exception, ValueError) as ex:
        logging.getLogger().error(str(ex))

    return response.Response(
        ctx,
        response_data=json.dumps(resp),
        headers={"Content-Type": "application/json"}
    )

def get_object_content(bucketName, objectName): # This Function gets the contents of the object you specify, and creates message with the content.
    signer = oci.auth.signers.get_resource_principals_signer()
    client = oci.object_storage.ObjectStorageClient(config={}, signer=signer)
    namespace = client.get_namespace().data
    try:
        print("Searching for bucket and object", flush=True)
        object = client.get_object(namespace, bucketName, objectName)
        print("found object", flush=True)
        if object.status == 200:
            print("Success: The object " + objectName + " was retrieved with the content: " + object.data.text, flush=True)
            message = object.data.text
            #Validation to check whether object is a .json file. Else exit from function.
            if objectName.lower().endswith(".json"):
                json_data = json.loads(message)
            else:
                message = "Most recent object is a text, so this function doesn't work"
                return message
        else:
            message = "Failed: The object " + objectName + " could not be retrieved."
    except Exception as e:
        message = "Failed: " + str(e.message)
    return message

    # Google upload code to Google Sheets, using the message variable gained.

    

def list_latest_object(bucketName):  # This function extracts the name of the latest object you uploaded in object storage.
    signer = oci.auth.signers.get_resource_principals_signer()
    client = oci.object_storage.ObjectStorageClient(config={}, signer=signer)
    namespace = client.get_namespace().data
    print("Searching for objects in bucket " + bucketName, file=sys.stderr)
    object = client.list_objects(namespace, bucketName, fields = "timeModified")
    print("found objects", flush=True)

    #This works for some reason
    latest_modification_date = max(([b.time_modified for b in object.data.objects]))
    found_object = None

    #This also works for some reason. Don't use item[time_modified], it doesn't work.
    for item in object.data.objects:
        if item.time_modified == latest_modification_date:
            found_object = item

    #When creating a response, make sure to convert whatever you have to string, otherwise it will fail.
    #This response extracts the name of the latest object you uploaded in object storage.
    response = str(found_object.name)
    return response

def openai_transform(text_prompt):
    client = OpenAI(api_key=API_KEY_STRING)

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": GPT_PROMPT},
            {
                "role": "user",
                "content": str(text_prompt)
            }
        ]
    )

    gpt_message = completion.choices[0].message
    text_content = gpt_message.content

    response = text_content

    return response


def google_sheets_append_json(text_message):
    try:
        # Load the service account key from the service_account.json
        credentials_info = json.load(open(SERVICE_ACCOUNT_PATH))
        credentials = service_account.Credentials.from_service_account_info(credentials_info)
        scoped_credentials = credentials.with_scopes(SCOPES)
        service = build('sheets', 'v4', credentials=scoped_credentials)

        #JSON Configuration (OPTIONAL). Put your own code configuration for the json here. Set the variable you are extracting from the json as json_extract
        json_data = json.loads(text_message)
        json_extract = json_data
        #This is a sample code that pushes a transcription key value as the json_extract
        #for item in json_data['transcriptions']:
            #json_extract = item.get('transcription')
        
        #This is a sample code that pushes all the values in your json as a list variable to the json_extract. This code makes your json_extract push to Google Sheets horizontal/vertical depending on the list you choose. By default it is horizontal list.
        #horizontal_list = []
        #vertical_list = []
        #for item in data.values():
            #horizontal_list.append(item)
            #vertical_list.append([item])
        #json_extract = horizontal_list
        
        #This is another sample code that pushes a transcription key value as the json_extract
        if "transcriptions" in json_data and isinstance(json_data["transcriptions"], list) and len(json_data["transcriptions"]) > 0 and "transcription" in json_data["transcriptions"][0]:
            json_extract = json_data["transcriptions"][0]["transcription"]
        #-----------------END OF JSON CONFIGURATION-----------------
        improved_json_extract = openai_transform(json_extract)

        #Puts the json_extract to a list for appending to the request body. In the case you want to 
        if isinstance(json_extract, list):
            values_to_append = [
                improved_json_extract
            ]
        else:
            values_to_append = [
                [str(improved_json_extract)]
            ]
        
        # Set up the body to append with created list
        body = {
        'values': values_to_append
        }   
    # Call the Sheets API
        sheet = service.spreadsheets().values().append(
        spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME,
        valueInputOption='USER_ENTERED', body=body).execute()

    except Exception as e:
        return {"error": str(e)}
    #Code to return message
    return str(improved_json_extract)