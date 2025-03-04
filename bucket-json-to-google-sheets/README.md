# OCI Object Storage to Google Sheets

This setup allows you to update a Google Sheets of your choosing, to constantly append with the contents of any .json file you upload to a bucket of your choosing. You can also configure this Function to specifically send out a specific key/value as you require. This setup uses OCI Events and OCI Functions to track updates to the bucket, and trigger the function to read the contents of the object that has been added, before updating a Google Sheet you specify with those contents. This also requires set-up on two platforms, OCI and GCP (Don't worry, you only need a google account for GCP set-up). Note, this function only automatically takes the latest uploaded object to the bucket.

## Warning: This guide assumes you have basic knowledge of OCI, and will skip a few steps for setting up the required resources, only showing you the required configurations to make this set-up work.

To summarise, you will be setting up:
1. A GCP Service Account
2. OCI Compartment for all your resources.
3. OCI Object Storage to create a bucket to hold the .txt files
4. OCI Dynamic Groups to identify the Functions
5. OCI Policies to allow the Function to interact with the bucket
6. OCI VCN for the function. (You can use VCNs in another compartment if you want to, instead of creating a new VCN.)
7. OCI Applications to hold the required Functions.
8. OCI Functions to allow us to run an application that will utilize Google API.
9. OCI Events to track the changes to the bucket and trigger the Function whenever it happens.

## IMPORTANT STEPS for GCP and OCI Set-up:
1. If you haven't created a GCP Service Account key and/or not an Administrator on OCI, go to:
https://github.com/flipwooyoung/oci-google-functions/blob/main/README.md

2. Go to your Google Sheet, and share it to the email of the Service Account you created. This won't work otherwise.

3. Enable Google Sheets API here: https://console.cloud.google.com/marketplace/product/google/sheets.googleapis.com

4. You also need to set the required scopes to use Google Sheets API. Go to https://console.cloud.google.com/auth/scopes, and click on Add or Remove Scopes.

<img width="557" alt="image" src="https://github.com/user-attachments/assets/b8ed5f25-cbeb-4adb-bf21-37717bc85aec" />

5. Scroll down to Manually add scopes, and paste the below links, before adding to table. Click on Update once you are done, and you finished the set-up.
```
https://www.googleapis.com/auth/drive
https://www.googleapis.com/auth/spreadsheets
```
<img width="482" alt="image" src="https://github.com/user-attachments/assets/f0b9f04c-5752-4625-9398-a81731eb9c75" />


## Guide to set-up environment for this Function on OCI:
Note: You can skip to step 9 if you have already done steps 1-8 for a different function.

1. Create a compartment to hold all the resources that we will create in this guide.

2. Create a Object Storage Bucket in OCI, if you haven't. Make sure to enable Emit Object Events for this bucket.

<img width="178" alt="image" src="https://github.com/user-attachments/assets/a77ac413-adab-45a0-aec3-b6f734a9a025" />

3. Now go to Identity Domain, and create a Dynamic Group to group the Function. This is the rule you have to input to group all Functions in a specified compartment:
```
All {resource.type = 'fnfunc', resource.compartment.id = 'ocid1.compartment.oc1..aaa'}
```

<img width="665" alt="image" src="https://github.com/user-attachments/assets/9018d5d9-650b-4895-9a26-c67806562c24" />

4. Now you need to create policies to enable this Dynamic Group to interact with Object Storage Buckets. This is the policy you have to input:
```
Allow dynamic-group {function_dynamic_group_name} to read objects in compartment {function_compartment_name}
```

<img width="706" alt="image" src="https://github.com/user-attachments/assets/7bee6bda-b0ef-4cea-8867-d81690a0f4cc" />

5. Create a VCN if you haven't for the function. Make sure this VCN has a subnet. You can use a VCN from another compartment if you don't want to create a new VCN.

6. Now that you have created the policy, you can set up the Function. First, you need to create an Application. Make sure to set the shape as GENERIC_X86

<img width="959" alt="image" src="https://github.com/user-attachments/assets/f8456884-3278-4418-8bd0-0f8dbdaace04" />

7. Go into the application you created, and follow the Getting Started guide, until you finish step 7. From there onwards, you will be setting up the function.

<img width="712" alt="image" src="https://github.com/user-attachments/assets/c5ab41e9-ed89-4381-aab8-183acfaac8ca" />

8. Run this command to set the compartment you push images to. Note: This is necessary if you don't have administrator privileges.
```
fn update context oracle.image-compartment-id <function_compartment-ocid>
```

9. Run this command, to clone this github repo:
```
git clone https://github.com/flipwooyoung/oci-google-functions
```

10. Go to this directory:

```
cd ~/oci-google-functions/bucket-to-google-sheets
```

12. To confirm, you should have cloned 4 necessary files, the func.py, func.yaml, requirements.txt, and the service_account.json in the main directory. You can check this with ls -la, or even more easier, check with OCI Code Editor.

<img width="240" alt="image" src="https://github.com/user-attachments/assets/ccc888ed-9619-4765-87a6-9e3e43ecbcb1" />

13. Now you need to set up the function with your variables. Go to Code Editor, and go to oci-google-functions/bucket-to-google-sheets/func.py. This python file contains all the code for this function. First, set up the SAMPLE_SPREADSHEET_ID. Go to line 23, and change this to the sheet ID of your Google sheet that you want to set as the target.

<img width="664" alt="image" src="https://github.com/user-attachments/assets/e8249e5e-0477-4cad-bc03-b64c764e6383" />

Go to your Google Sheet link. This is your sheet ID.

<img width="525" alt="image" src="https://github.com/user-attachments/assets/416876ba-f695-49bd-90c3-0989cc1cc971" />

14. Make sure to set the bucket name at line 20. Change the string value to the name of your bucket containing the object.

Optional: In the case that you want to send a specific key/value, then go to line 79. This is the JSON configuration area, where you can set what you want as the response to be pushed to Google Sheets.

15. You also need to set up the service account .json file you downloaded from your GCP Cloud Console. There is a sample service_account.json in the bucket-to-google-sheets directory that you should have cloned too. Fill in all the json values with the ones in your service account .json

16. Now you need to set up the function. cd to the directory of the function, if you still haven't. 
```
cd ~/oci-google-functions/bucket-json-to-google-sheets
```

17. Follow the command in Step 10 of the Getting Started page or copy the below command:
```
fn -v deploy --app {application_name}
```

18. Now that you have set it up, use this command to invoke the function for testing, or just copy it from Step 11  of the Getting Started page:
```
fn invoke {application_name} bucket-json-to-google-sheets
```

19. This function should display the text of the latest object you uploaded. If successful, move on to the next step, if not, try rerunning the function invoke command again. Otherwise, go to [Debug Section]

20. Now it's time to set up the OCI Event. Just search up Rules in the search bar, and create the rule with these conditions. (You have to type your bucket name, can't select it.)

<img width="554" alt="image" src="https://github.com/user-attachments/assets/fc5874d6-83ee-4666-b3d4-3b9a72b44295" />

21. Set the Action to where your function compartment is (Function should be bucket-to-google-sheets):

<img width="790" alt="image" src="https://github.com/user-attachments/assets/dbc6cdfa-fb06-446e-a33c-8c6143cb054e" />

22. Congratulations. You set up everything. Test it out by uploading an object to the bucket.

