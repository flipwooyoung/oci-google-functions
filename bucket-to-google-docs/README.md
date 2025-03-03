This setup allows you to update a Google Doc of your choosing, to constantly update with the contents of any .txt file you upload to a bucket of your choosing. This setup uses OCI Events and OCI Functions to track updates to the bucket, and trigger the function to read the contents of the object that has been added, before updating a Google Doc you specify with those contents. This also requires set-up on two platforms, OCI and GCP (Don't worry, you only need a google account for GCP set-up).

To summarise, you will be setting up:
1. A GCP Service Account
2. OCI Object Storage to create a bucket to hold the .txt files
3. OCI Policies to allow the Function to interact with the bucket
4. OCI Functions to allow us to run an application that will utilize Google API to update the Google Doc.
5. OCI Events to track the changes to the bucket and trigger the Function whenever it happens.

If you haven't created a GCP Service Account key, go to:
https://github.com/flipwooyoung/oci-google-functions/blob/main/README.md

References:

https://googleapis.github.io/google-api-python-client/docs/dyn/docs_v1.documents.html#get
