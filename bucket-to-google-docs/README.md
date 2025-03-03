This setup allows you to update a Google Doc of your choosing, to constantly update with the contents of any .txt file you upload to a bucket of your choosing. This setup uses OCI Events and OCI Functions to track updates to the bucket, and trigger the function to read the contents of the object that has been added, before updating a Google Doc you specify with those contents. This also requires set-up on two platforms, OCI and GCP (Don't worry, you only need a google account for GCP set-up). Note, this function only automatically takes the latest uploaded object to the bucket.

Warning: This guide assumes you have basic knowledge of OCI, and will skip a few steps for setting up the required resources, only showing you the required configurations to make this set-up work.

To summarise, you will be setting up:
1. A GCP Service Account
2. OCI Object Storage to create a bucket to hold the .txt files
3. OCI Dynamic Groups to identify the Functions
4. OCI Policies to allow the Function to interact with the bucket
5. OCI Functions to allow us to run an application that will utilize Google API to update the Google Doc.
6. OCI Events to track the changes to the bucket and trigger the Function whenever it happens.

If you haven't created a GCP Service Account key, go to:
https://github.com/flipwooyoung/oci-google-functions/blob/main/README.md

Guide to utilize this Function:
1. Create a Object Storage Bucket in OCI, if you haven't. Make sure to enable Emit Object Events for this bucket.
<img width="178" alt="image" src="https://github.com/user-attachments/assets/a77ac413-adab-45a0-aec3-b6f734a9a025" />
2. Now go to Identity Domain, and create a Dynamic Group to group the Function. This is the rule you have to input to group all Functions in a specified compartment: All {resource.type = 'fnfunc', resource.compartment.id = 'ocid1.compartment.oc1..aaa'}

<img width="665" alt="image" src="https://github.com/user-attachments/assets/9018d5d9-650b-4895-9a26-c67806562c24" />

3. Now you need to create policies to enable this Dynamic Group to interact with Object Storage Buckets. This is the policy you have to input: Allow service faas to manage objects in compartment function_compartment	



4. Now that you have created the policy, you can set up the Function. 

References:

https://googleapis.github.io/google-api-python-client/docs/dyn/docs_v1.documents.html#get
