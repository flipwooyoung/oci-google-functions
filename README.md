<img width="959" alt="image" src="https://github.com/user-attachments/assets/dffdabc3-cfd8-4f1d-8ef5-50ec322b2fbb" /># oci-google-functions
This repository contains materials to transfer objects from OCI Object Storage to Google Workspace tools (e.g. Google Docs).

You will require a Google Account to utilize Google API, and a Service Account to use the code on this repository.

How to get Service Account from GCP Cloud Console:

1. Go to GCP (https://console.cloud.google.com).
2. Create a Project if you don't have one. The project used doesn't matter, but for the sake of safety, you should create a project for each application you create.
<img width="959" alt="image" src="https://github.com/user-attachments/assets/97d495e8-73a0-4931-be5c-af89d663ae11" />
3. Go to Service Accounts from the search bar.
<img width="520" alt="image" src="https://github.com/user-attachments/assets/f1088698-eb00-4bb3-af06-c52915f60752" />
4. You should see something like this. I have already created a Service Account, which appears here. Click on Create Service Account
<img width="952" alt="image" src="https://github.com/user-attachments/assets/8bdc3e47-52e4-4910-9e95-4c3c1ac1c445" />
5. Fill in the required details for the Service Account.
<img width="428" alt="image" src="https://github.com/user-attachments/assets/8df77468-c653-4113-b788-9f1443c65d54" />
6. For the second part, you will have to set up permissions for this Service Account. Give Editor to the Service Account for the strongest privilege, but if you only require Workspace permissions, just search Workspace and select between Workspace Developer and Reader. The third part doesn't matter, just continue with creation.
<img width="954" alt="image" src="https://github.com/user-attachments/assets/43799971-c3af-41e4-9d45-e4752578a2c0" />
7. Now that you have created a Service Account, you will have to create a key for it. Go to your created Service Account's options, and click on Manage Keys.
<img width="946" alt="image" src="https://github.com/user-attachments/assets/54ef1526-4b0d-4fc7-b9e7-cb386dddade1" />
8. Click on Add Key. Either create a new key or upload an existing one. This guide creates a new key.
<img width="955" alt="image" src="https://github.com/user-attachments/assets/2308056b-fc8d-4ffc-af16-298bcc34cd25" />
9. Keep json as the selected option, and select Create. You will automatically download your Service Account key as a .json file. Keep it in a secure location, as it is how you authorize yourself.
<img width="374" alt="image" src="https://github.com/user-attachments/assets/2d52f5cd-03f8-4578-8b6b-d018195c465d" />

Congrats! You created your Service Account and a key to access it. As long as you have given sufficient permissions to the Service Account, you can do everything in this Repository with the key.
Resources referenced:

-OCI Object Storage API Documentation
https://docs.oracle.com/en-us/iaas/tools/python/2.145.0/api/object_storage/client/oci.object_storage.ObjectStorageClient.html#oci.object_storage.ObjectStorageClient.list_objects
-Google Cloud Platform Cloud Console
https://console.cloud.google.com

