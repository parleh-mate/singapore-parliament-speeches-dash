from google.cloud import storage
import pickle
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "tokens/gcp_token.json"

# Initialize the GCS client
storage_client = storage.Client()
bucket = storage_client.bucket("dash-app-cache")
blob = bucket.blob("dash-datasets")

# Download the serialized data
serialized_data = blob.download_as_bytes()

# Deserialize the data back into a dictionary
data = pickle.loads(serialized_data)