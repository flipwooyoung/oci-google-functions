<img width="493" alt="image" src="https://github.com/user-attachments/assets/77342bf9-8709-4149-a8a9-a1b844ad8f14" /># OCI Object Storage to Google Sheets

This setup allows you to utilize OCI Functions to convert a video file (mp3, wav, etc.) to text using OCI Speech. This setup uses OCI Events and OCI Functions to track updates to the bucket, and trigger the function to read the contents of the object that has been added, before updating a Google Sheet you specify with those contents. Note: this function only automatically takes the latest uploaded object to the bucket.

## Warning: This guide assumes you have basic knowledge of OCI, and will skip a few steps for setting up the required resources, only showing you the required configurations to make this set-up work.

To summarise, you will be setting up:
1. OCI Compartment for all your resources.
2. OCI Object Storage to create a bucket to hold the .txt files
3. OCI Dynamic Groups to identify the Functions
4. OCI Policies to allow the Function to interact with the bucket
5. OCI VCN for the function. (You can use VCNs in another compartment if you want to, instead of creating a new VCN.)
6. OCI Applications to hold the required Functions.
7. OCI Functions to allow us to run an application that will utilize OCI Speech.
8. OCI Events to track the changes to the bucket and trigger the Function whenever it happens.



## Guide to set-up environment for this Function on OCI:
Note: You can skip to step 8 if you have already done steps 1-7 for a different function.

1. Create a compartment to hold all the resources that we will create in this guide.

2. Create a Object Storage Bucket in OCI, if you haven't. Make sure to enable Emit Object Events for this bucket.

<img width="178" alt="image" src="https://github.com/user-attachments/assets/a77ac413-adab-45a0-aec3-b6f734a9a025" />

3. Now go to Identity Domain, and create a Dynamic Group to group the Function. This is the rule you have to input to group all Functions in a specified compartment:
```
All {resource.type = 'fnfunc', resource.compartment.id = 'ocid1.compartment.oc1..aaa'}
```

<img width="665" alt="image" src="https://github.com/user-attachments/assets/9018d5d9-650b-4895-9a26-c67806562c24" />


4. Create a VCN if you haven't for the function. Make sure this VCN has a subnet. You can use a VCN from another compartment if you don't want to create a new VCN.

5. Now that you have created the policy, you can set up the Function. First, you need to create an Application. Make sure to set the shape as GENERIC_X86

<img width="959" alt="image" src="https://github.com/user-attachments/assets/f8456884-3278-4418-8bd0-0f8dbdaace04" />

6. Go into the application you created, and follow the Getting Started guide, until you finish step 7. From there onwards, you will be setting up the function.

<img width="712" alt="image" src="https://github.com/user-attachments/assets/c5ab41e9-ed89-4381-aab8-183acfaac8ca" />

7. Run this command to set the compartment you push images to. Note: This is necessary if you don't have administrator privileges.
```
fn update context oracle.image-compartment-id <function_compartment-ocid>
```

8. Run this command, to clone this github repo:
```
git clone https://github.com/flipwooyoung/oci-google-functions
```

9. Now you need to create policies to enable this Dynamic Group to interact with Object Storage Buckets and use OCI Speech. This is the policy you have to input (skip this step if you have already done this.):
```
allow dynamic-group {function_dynamic_group_name} to manage ai-service-speech-family in compartment {function_compartment_name}
allow dynamic-group {function_dynamic_group_name} to read tag-namespaces in compartment {function_compartment_name}
allow dynamic-group {function_dynamic_group_name} to inspect tag-namespaces in compartment {function_compartment_name}
allow dynamic-group {function_dynamic_group_name} to manage object-family in compartment {function_compartment_name}
```

10. Go to this directory:

```
cd ~/oci-google-functions/oci-speech-test
```

11. To confirm, you should have cloned 3 necessary files, the func.py, func.yaml, requirements.txt. You can check this with ls -la, or even more easier, check with OCI Code Editor.

<img width="240" alt="image" src="https://github.com/user-attachments/assets/ccc888ed-9619-4765-87a6-9e3e43ecbcb1" />

12. Now you need to set up the function with your variables. Go to Code Editor, and go to oci-google-functions/oci-speech-test/func.py. Change the variables at line 18-25. The SOURCE_BUCKET, DESTINATION_BUCKET, SOURCE_COMPARTMENT_OCID, change these to your resource requirements.

<img width="493" alt="image" src="https://github.com/user-attachments/assets/16524010-bb4c-4137-9e89-7368833a517d" />

13. Now you need to set up the function. cd to the directory of the function, if you still haven't. 
```
cd ~/oci-google-functions/oci-speech-test
```

14. Follow the command in Step 10 of the Getting Started page or copy the below command:
```
fn -v deploy --app {application_name}
```

15. Now that you have set it up, use this command to invoke the function for testing, or just copy it from Step 11  of the Getting Started page:
```
fn invoke {application_name} oci-speech-test
```

16. This function should display the text of the latest object you uploaded. If successful, move on to the next step, if not, try rerunning the function invoke command again. Otherwise, go to {insert debug section later}

17. Now it's time to set up the OCI Event. Just search up Rules in the search bar, and create the rule with these conditions. (You have to type your bucket name, can't select it.)

<img width="554" alt="image" src="https://github.com/user-attachments/assets/fc5874d6-83ee-4666-b3d4-3b9a72b44295" />

18. Set the Action to where your function compartment is (Function should be oci-speech-test):

<img width="790" alt="image" src="https://github.com/user-attachments/assets/dbc6cdfa-fb06-446e-a33c-8c6143cb054e" />

19. Congratulations. You set up everything. Test it out by uploading an video to the bucket.

