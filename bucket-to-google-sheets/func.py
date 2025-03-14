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

import oci.object_storage

# Modify this to whatever scope you require from google API. The current configuration allows read/write access for Google SHEETS
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

#Change this to your bucket name
BUCKET_NAME = "your_bucket_name"

# The ID of your sheet. Go to the git repo to see how to get your document ID. Only change the SAMPLE_RANGE_NAME if you want to change the column affected.
SAMPLE_SPREADSHEET_ID = "your_spreadsheet_id"

#Only change the SAMPLE_RANGE_NAME if you want to change the column affected. Make sure to put {sheet_name}!A1 without the {}, iF your sheet name isn't Sheet1
SAMPLE_RANGE_NAME = "Sheet1!A1"

#By default you don't need to change this unless you changed the service_account.json location. Change this if you have.
SERVICE_ACCOUNT_PATH = "service_account.json"

def handler(ctx, data: io.BytesIO=None):

    try:
        data_bytes = data.getvalue()
        data_str = data_bytes.decode('utf-8')
        data_object = None
        
        if data_str == "":
            data_object = list_latest_object(BUCKET_NAME)
        else:
            data_json = json.loads(data.getvalue())
            logging.getLogger().info(json.dumps(data_json))
            data_namespace = data_json["data"]["additionalDetails"]["namespace"]
            data_nsrc_bucket = data_json["data"]["additionalDetails"]["bucketName"]
            data_object = data_json["data"]["resourceName"]
    except (Exception, ValueError) as ex:
        logging.getLogger().error(str(ex))

    if not data_object:
        resp = "Wasn't able to extract object properly"
    else:
        text_message = get_object_content(BUCKET_NAME, data_object)
        google_sheets_append(text_message)
        resp = text_message

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
        else:
            message = "Failed: The object " + objectName + " could not be retrieved."
    except Exception as e:
        message = "Failed: " + str(e.message)
    #Code to return message
    return message
    

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

def google_sheets_append(text_message):
        # Google upload code to Google Sheets, using the message variable gained.
    try:
        # Load the service account key from the service_account.json
        credentials_info = json.load(open(SERVICE_ACCOUNT_PATH))
        credentials = service_account.Credentials.from_service_account_info(credentials_info)
        scoped_credentials = credentials.with_scopes(SCOPES)
        service = build('sheets', 'v4', credentials=scoped_credentials)

        #Put the message extracted from object storage to a list
        values_to_append = [[str(text_message)]]
        
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
        