from google.cloud import storage
import pickle
import os

if os.environ.get('ENVIRONMENT') == 'development':

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "tokens/gcp_token.json"

else:

    credentials_json = os.environ.get('GCP_JSON')

    if not credentials_json:
        raise EnvironmentError("The GOOGLE_APPLICATION_CREDENTIALS environment variable is not set.")

    credentials_path = '/tmp/gcp_token.json'
    
    with open(credentials_path, 'w') as f:
        f.write(credentials_json)

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
    

# Initialize the GCS client
storage_client = storage.Client()
bucket = storage_client.bucket("dash-app-cache")
blob = bucket.blob("dash-datasets")

# Download the serialized data
serialized_data = blob.download_as_bytes()

# Deserialize the data back into a dictionary
data = pickle.loads(serialized_data)