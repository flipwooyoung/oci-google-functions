#
# oci-objectstorage-get-object version 1.0.
#
# Copyright (c) 2020 Oracle, Inc.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#

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
# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/documents"]

# The ID of a sample document.
DOCUMENT_ID = "1KSTW36o6vrPSBtsLzU1cOThNtN6-Tex2Z-p-yjnTF7U"

def handler(ctx, data: io.BytesIO=None):
    try:
        body = {"bucketName": "test_bucket"}
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

def get_object(bucketName, objectName):
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
    
    # Google upload code
    try:
        # Load the service account key from OCI Object Storage
        signer = oci.auth.signers.get_resource_principals_signer()
        object_storage = oci.object_storage.ObjectStorageClient(config={}, signer=signer)
        namespace = object_storage.get_namespace().data
        bucket_name = "test_bucket" #Replace with your bucket name
        object_name = "service_account.json" #replace with your credentials file name
        object_response = object_storage.get_object(namespace, bucket_name, object_name)
        credentials_info = json.loads(object_response.data.content)

        credentials = service_account.Credentials.from_service_account_info(credentials_info)
        scoped_credentials = credentials.with_scopes(SCOPES)
        docs_service = build('docs', 'v1', credentials=scoped_credentials)

        # Retrieve the documents contents from the Docs service.
        body_dict = {}
        document = docs_service.documents().get(documentId=DOCUMENT_ID).execute()
        print(f"The title of the document is: {document.get('title')}")
        body_dict = document.get('body')
        content_list = body_dict.get('content')[-1]
        end_index = content_list.get('endIndex')

        delete_requestBody = {
            "requests":[
                { 
                    "deleteContentRange": {
                        "range": {
                        "startIndex": 1,
                        "endIndex": end_index - 1,
                        }
                    },
                },
            ],
        }

        insert_requestBody = {
            "requests":[
                { 
                    "insertText": {
                        "text": message,
                        "location": {
                        "index": 1
                        }
                    },
                },
            ],
        }
			
		#Delete everything in the doc

        if end_index == 2:
            docs_service.documents().batchUpdate(documentId=DOCUMENT_ID,body=insert_requestBody).execute()
        else:
            docs_service.documents().batchUpdate(documentId=DOCUMENT_ID,body=delete_requestBody).execute()
            docs_service.documents().batchUpdate(documentId=DOCUMENT_ID,body=insert_requestBody).execute()
		
    except Exception as e:
        return {"error": str(e)}
    #Code to return message
    return message
    #return { "content": message }
    

def list_objects(bucketName):
    signer = oci.auth.signers.get_resource_principals_signer()
    client = oci.object_storage.ObjectStorageClient(config={}, signer=signer)
    namespace = client.get_namespace().data
    print("Searching for objects in bucket " + bucketName, file=sys.stderr)
    object = client.list_objects(namespace, bucketName, fields = "timeModified")
    print("found objects", flush=True)
    #object_names = [b.name for b in object.data.objects]

    #This works for some reason
    latest_modification_date = max(([b.time_modified for b in object.data.objects]))
    #latest_object = str(max(object.data.objects, key=lambda x:x['time_modified']))
    found_object = None

    #This also works for some reason. Don't use item[time_modified], it doesn't work.
    for item in object.data.objects:
        if item.time_modified == latest_modification_date:
            found_object = item

    #When creating a response, make sure to convert whatever you have to string, otherwise it will fail.
    #response = { "Objects found in bucket '" + bucketName + "'": object_names }
    #response = { "Objects found in bucket " + bucketName: str(item)}
    response = str(found_object.name)
    #response = str(object.data.objects)
    #response = str(found_object)
    return response
