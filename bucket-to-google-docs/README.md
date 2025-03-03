This setup allows you to update a Google Doc of your choosing, to constantly update with the contents of any .txt file you upload to a bucket of your choosing. This setup uses OCI Events and OCI Functions to track updates to the bucket, and trigger the function to read the contents of the object that has been added, before updating a Google Doc you specify with those contents. This also requires set-up on two platforms, OCI and GCP (Don't worry, you only need a google account for GCP set-up). Note, this function only automatically takes the latest uploaded object to the bucket.

## Warning: This guide assumes you have basic knowledge of OCI, and will skip a few steps for setting up the required resources, only showing you the required configurations to make this set-up work.

To summarise, you will be setting up:
1. A GCP Service Account
2. OCI Compartment for all your resources.
3. OCI Object Storage to create a bucket to hold the .txt files
4. OCI Dynamic Groups to identify the Functions
5. OCI Policies to allow the Function to interact with the bucket
6. OCI VCN for the function. (You can use VCNs in another compartment if you want to, instead of creating a new VCN.)
7. OCI Functions to allow us to run an application that will utilize Google API to update the Google Doc.
8. OCI Events to track the changes to the bucket and trigger the Function whenever it happens.

If you haven't created a GCP Service Account key, go to:
https://github.com/flipwooyoung/oci-google-functions/blob/main/README.md

IMPORTANT STEP:
Go to your Google Doc, and share it to the email of the Service Account you created. This won't work otherwise. Also, enable Google Doc API here: https://console.cloud.google.com/apis/api/docs.googleapis.com

Guide to utilize this Function:

1. Create a compartment to hold all the resources that we will create in this guide.

2. Create a Object Storage Bucket in OCI, if you haven't. Make sure to enable Emit Object Events for this bucket.

<img width="178" alt="image" src="https://github.com/user-attachments/assets/a77ac413-adab-45a0-aec3-b6f734a9a025" />

3. Now go to Identity Domain, and create a Dynamic Group to group the Function. This is the rule you have to input to group all Functions in a specified compartment: All {resource.type = 'fnfunc', resource.compartment.id = 'ocid1.compartment.oc1..aaa'}

<img width="665" alt="image" src="https://github.com/user-attachments/assets/9018d5d9-650b-4895-9a26-c67806562c24" />

4. Now you need to create policies to enable this Dynamic Group to interact with Object Storage Buckets. This is the policy you have to input: Allow dynamic-group {function_dynamic_group_name} to read objects in compartment {function_compartment_name}

<img width="706" alt="image" src="https://github.com/user-attachments/assets/7bee6bda-b0ef-4cea-8867-d81690a0f4cc" />

5. Create a VCN if you haven't for the function. Make sure this VCN has a subnet. You can use a VCN from another compartment if you don't want to create a new VCN.

6. Now that you have created the policy, you can set up the Function. First, you need to create an Application. Make sure to set the shape as GENERIC_X86

<img width="959" alt="image" src="https://github.com/user-attachments/assets/f8456884-3278-4418-8bd0-0f8dbdaace04" />

7. Go into the application you created, and follow the Getting Started guide, until you finish step 7. From there onwards, you will be setting up the function.

<img width="712" alt="image" src="https://github.com/user-attachments/assets/c5ab41e9-ed89-4381-aab8-183acfaac8ca" />

8. Run this command, to clone this github repo: git clone https://github.com/flipwooyoung/oci-google-functions

9. Go to this directory: cd oci-google-functions/bucket-to-google-docs

10. To confirm, you should have cloned 4 necessary files, the func.py, func.yaml, requirements.txt, and the service_account.json in the main directory. You can check this with ls -la, or even more easier, check with OCI Code Editor.

<img width="240" alt="image" src="https://github.com/user-attachments/assets/ccc888ed-9619-4765-87a6-9e3e43ecbcb1" />

11. Now you need to set up the function with your variables. Go to Code Editor, and go to oci-google-functions/bucket-to-google-docs/func.py. This python file contains all the code for this function. First, set up the document ID. Go to line 23, and change this to the document ID of your Google Doc that you want to set as the target.

<img width="551" alt="image" src="https://github.com/user-attachments/assets/43aa9423-9ec0-46d7-b0d9-e5084ef56688" />

Go to your Google Doc link. This is your document ID.

<img width="605" alt="image" src="https://github.com/user-attachments/assets/51ce5d98-12a4-4355-bf14-eef2538342c5" />

12. Make sure to set the bucket name at line 20. Change the string value to the name of your bucket.

13. You also need to set up the service account .json file you downloaded from your GCP Cloud Console. There is a service_account.json in the repo that you should have cloned too. Fill in all the json values with the ones in your service account .json

14. Now you need to set up the function. You should already be in the  oci-google-functions/bucket-to-google-docs directory from a previous step, but in case you aren't, cd there.  Follow the command in Step 10 of the Getting Started page. It should be similar to this: fn -v deploy --app {name_of_application}

15. Now that you have set it up, use this command to invoke the function for testing: fn invoke {application_name} bucket-to-google-docs

16. This function should display the text of the latest object you uploaded. If successful, move on to 17, if not, try rerunning the function invoke cmd again.

17. Now it's time to set up the OCI Event. Just search up Rules in the search bar, and create the rule with these conditions. (You have to type your bucket name, can't select it.)

<img width="554" alt="image" src="https://github.com/user-attachments/assets/fc5874d6-83ee-4666-b3d4-3b9a72b44295" />

18. Set the Action as so (Function should be bucket-to-google-docs):

<img width="803" alt="image" src="https://github.com/user-attachments/assets/9deff2cf-02c7-4a67-bc6d-7f2c865536b1" />

19. Congrats. You set up everything. Test it out by uploading an object to the bucket.

