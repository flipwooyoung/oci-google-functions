#
# oci-objectstorage-list-objects-python version 1.0.
#
# Copyright (c) 2020 Oracle, Inc.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#

import io
import os
import json
import sys
import datetime

from fdk import response
import oci
import oci.ai_speech

#Change this to your source bucket with videos
SOURCE_BUCKET = "source_video_bucket"

#Change this to where your destination bucket should be (can be the same as source bucket)
DESTINATION_BUCKET = "destination_video_bucket"

#Change this to be your source bucket compartment OCID
SOURCE_COMPARTMENT_OCID = "source_compartment_ocid"

def handler(ctx, data: io.BytesIO=None):
    try:
        body = {"bucketName": SOURCE_BUCKET}
        bucketName = body["bucketName"]
    except Exception:
        raise Exception('Input a JSON object in the format: \'{"bucketName": "<bucket name>"}\' ')
    
    object_name, namespace = list_objects(SOURCE_BUCKET)

    resp = create_oci_speech_job(object_name, namespace)


    return response.Response(
        ctx,
        response_data=json.dumps(resp),
        headers={"Content-Type": "application/json"}
    )

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
    return response, namespace

def create_oci_speech_job(object_name, namespace):
    # Initialize service client with default config file
    signer = oci.auth.signers.get_resource_principals_signer()
    ai_speech_client = oci.ai_speech.AIServiceSpeechClient(config={}, signer=signer)

    #PUT YOUR VARIABLES HERE
    source_bucket_name = SOURCE_BUCKET
    source_compart = SOURCE_COMPARTMENT_OCID
    dest_bucket = DESTINATION_BUCKET


    #create_transcription_job_response = "hello"
    try:
        create_transcription_job_response = ai_speech_client.create_transcription_job(
            create_transcription_job_details=oci.ai_speech.models.CreateTranscriptionJobDetails(
                compartment_id=source_compart,
                input_location=oci.ai_speech.models.ObjectListInlineInputLocation(
                    location_type="OBJECT_LIST_INLINE_INPUT_LOCATION", #You can change this to OBJECT_LIST_FILE_INPUT_LOCATION for some reason, but dont
                    object_locations=[
                    oci.ai_speech.models.ObjectLocation(
                            namespace_name=namespace,
                            bucket_name=source_bucket_name,
                            object_names=["object_name"]
                        )
                    ]
                ),
                output_location=oci.ai_speech.models.OutputLocation(
                    namespace_name=namespace,
                    bucket_name=dest_bucket,
                    #You can change this if you want a different output
                    prefix="output"),
                additional_transcription_formats=["SRT"],
                display_name = object_name,
                model_details=oci.ai_speech.models.TranscriptionModelDetails(
                    domain="GENERIC",
                    language_code="en-GB",
                    transcription_settings=oci.ai_speech.models.TranscriptionSettings(
                        diarization=oci.ai_speech.models.Diarization(
                            is_diarization_enabled=False,
                            number_of_speakers=2)
                            )
                        )
                    )
                )


    except Exception as e:
        return {"error": str(e)}

    # Compose the path to the result file:
    return str(create_transcription_job_response.data)