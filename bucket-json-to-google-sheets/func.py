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
from fdk import response

import oci.object_storage

# Modify this to whatever scope you require from google API. The current configuration allows read/write access for Google SHEETS
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

#Change this to your bucket name
BUCKET_NAME = "test_bucket"

# The ID of your sheet. Go to the git repo to see how to get your document ID. Only change the SAMPLE_RANGE_NAME if you want to change the column affected.
SAMPLE_SPREADSHEET_ID = "1-6l-5nAjUhwbOY8JwiOL1H724GKpFel0_81SweCUHUI"

#Only change the SAMPLE_RANGE_NAME if you want to change the column affected. Make sure to put {sheet_name}!A1 without the {}, iF your sheet name isn't Sheet1
SAMPLE_RANGE_NAME = "Sheet1!A1"

#By default you don't need to change this unless you changed the service_account.json location. Change this if you have.
SERVICE_ACCOUNT_PATH = "service_account.json"

def handler(ctx, data: io.BytesIO=None):
    try:
        body = {"bucketName": BUCKET_NAME}
        bucketName = body["bucketName"]
    except Exception:
        raise Exception('Input a JSON object in the format: \'{"bucketName": "<bucket name>"}\' ')
        
    extracted_object_name = list_objects(bucketName)

    resp = get_object(bucketName, extracted_object_name)

    return response.Response(
        ctx,
        response_data=json.dumps(resp),
        headers={"Content-Type": "application/json"}
    )

def get_object(bucketName, objectName): # This Function gets the contents of the object you specify, and creates message with the content.
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
    
    # Google upload code to Google Sheets, using the message variable gained.
    try:
        # Load the service account key from the service_account.json
        credentials_info = json.load(open(SERVICE_ACCOUNT_PATH))
        credentials = service_account.Credentials.from_service_account_info(credentials_info)
        scoped_credentials = credentials.with_scopes(SCOPES)
        service = build('sheets', 'v4', credentials=scoped_credentials)

        #JSON Configuration (OPTIONAL). Put your own code configuration for the json here. Set the variable you are extracting from the json as json_extract
        json_extract = json_data #Comment this line out if you are adding your own JSON configuration.

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
        #if "transcriptions" in json_data and isinstance(json_data["transcriptions"], list) and len(json_data["transcriptions"]) > 0 and "transcription" in json_data["transcriptions"][0]:
            #json_extract = json_data["transcriptions"][0]["transcription"]
        #-----------------END OF JSON CONFIGURATION-----------------
    

        #Puts the json_extract to a list for appending to the request body. In the case you want to 
        if isinstance(json_extract, list):
            values_to_append = [
                json_extract
            ]
        else:
            values_to_append = [
                [str(json_extract)]
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
    return str(json_extract)
    

def list_objects(bucketName):  # This function extracts the name of the latest object you uploaded in object storage.
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
