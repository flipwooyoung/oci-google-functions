import io
import os
import json
import sys
import datetime
import logging

from fdk import response
import oci
import oci.ai_speech

#Change this to your source bucket with videos
SOURCE_BUCKET = "oci_speech_bucket"

#Change this to where your destination bucket should be (can be the same as source bucket)
DESTINATION_BUCKET = "oci_speech_output_bucket"

#Change this to be your source bucket compartment OCID
SOURCE_COMPARTMENT_OCID = "ocid1.compartment.oc1..aaaaaaaakyhbyurv7jfhbfqnr7auf3wbydtoeixltukixjqq4lphe2gtykdq"

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
            logging.getLogger().info(f'Preparing Speech Job with {data_object} from {data_source_bucket}')
            
            if str(data_object).lower().endswith(".mp3"):
                logging.getLogger().info(f'mp3 validation works')
            else:
                logging.getLogger().info(f"Most recent object is not a mp3, so this function doesn't work")
                data_object = None
    except (Exception, ValueError) as ex:
        logging.getLogger().error(str(ex))
    try:
        if data_object == None:
            logging.getLogger().info(f"Wasn't able to extract object properly")
        else:
            text_message = create_oci_speech_job(data_object, data_namespace)
            resp = text_message
    except (Exception, ValueError) as ex:
        logging.getLogger().error(str(ex))

    return response.Response(
        ctx,
        response_data=json.dumps(resp),
        headers={"Content-Type": "application/json"}
    )

def list_latest_object(bucketName):
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
    if str(found_object.name).lower().endswith(".mp3"):
        response = str(found_object.name)
    else:
        response = "Latest object is not a video"
    return response, namespace

def create_oci_speech_job(object_name, namespace):
    # Initialize service client with default config file
    signer = oci.auth.signers.get_resource_principals_signer()
    ai_speech_client = oci.ai_speech.AIServiceSpeechClient(config={}, signer=signer)
    
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
                            object_names=[object_name]
                        )
                    ]
                ),
                output_location=oci.ai_speech.models.OutputLocation(
                    namespace_name=namespace,
                    bucket_name=dest_bucket,
                    prefix= "output"
                    ),
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
