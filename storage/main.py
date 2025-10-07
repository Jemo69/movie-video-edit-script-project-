from google.cloud import storage
from logger import get_logger
import google
import os

logger = get_logger(__name__)

# Set the GOOGLE_APPLICATION_CREDENTIALS environment variable
# Assuming googlekey.json is in the root directory of the project
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key.json"

def create_bucket():
    """
    Creates a new bucket in Google Cloud Storage.
    """
    try:
        bucket_name = "movie-edit"  # Replace with your bucket name
        storage_client = storage.Client()
        
        # Check if the bucket already exists
        bucket = storage_client.lookup_bucket(bucket_name)
        if bucket:
            bucket = storage_client.get_bucket(bucket_name)
            logger.info(f"Bucket {bucket.name} already exists.")
            return bucket
        else:
            # Create the bucket if it doesn't exist
            bucket = storage_client.bucket(bucket_name)
            bucket.location = "US"
            bucket = storage_client.create_bucket(bucket)
            logger.info(f"Bucket {bucket.name} created.")
            return bucket
    except google.api_core.exceptions.Forbidden as e:
        logger.warning(f"Could not create bucket: {e}. This might be due to billing issues.")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred during bucket creation: {e}")
        return None

async def upload_blob( source_file_name, destination_blob_name):
    """
    Uploads a file to the bucket.
    """
    try:
        bucket_name = "movie-edit"  # Replace with your bucket name
        bucket = create_bucket()
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_name)
        blob.make_public()
        logger.info(f"File {source_file_name} uploaded to {destination_blob_name}.")
        return blob.public_url
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return None
