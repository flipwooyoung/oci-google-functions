<img width="712" alt="image" src="https://github.com/user-attachments/assets/e897a276-c98c-46a4-bf4b-13632a6ac449" />This setup allows you to update a Google Doc of your choosing, to constantly update with the contents of any .txt file you upload to a bucket of your choosing. This setup uses OCI Events and OCI Functions to track updates to the bucket, and trigger the function to read the contents of the object that has been added, before updating a Google Doc you specify with those contents. This also requires set-up on two platforms, OCI and GCP (Don't worry, you only need a google account for GCP set-up). Note, this function only automatically takes the latest uploaded object to the bucket.

Warning: This guide assumes you have basic knowledge of OCI, and will skip a few steps for setting up the required resources, only showing you the required configurations to make this set-up work.

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

8. Run this command, to create boilerplate Python code for the Function: fn init --runtime python {name_your_function_directory)

9. Run this command to go to your function directory: cd {your_function_directory)

10. Run this command, to make the directory into a local git repo: git init

References:

https://googleapis.github.io/google-api-python-client/docs/dyn/docs_v1.documents.html#get
