from google.cloud import storage
from logger import get_logger
import google

logger = get_logger(__name__)

def create_bucket():
    """
    Creates a new bucket in Google Cloud Storage.
    """
    try:
        bucket_name = "movie-edit"  # Replace with your bucket name
        storage_client = storage.Client()
        checker = storage_client.list_buckets()
        bucket_list = [bucket for bucket in checker]
        if bucket_name not in bucket_list:
            bucket = storage_client.bucket(bucket_name)
            bucket.location = "US"
            bucket = storage_client.create_bucket(bucket)
            logger.info(f"Bucket {bucket.name} created.")
            return bucket
        else:
            bucket = storage_client.get_bucket(bucket_name)
            logger.info(f"Bucket {bucket.name} created.")
            return bucket
    except google.api_core.exceptions.Forbidden as e:
        logger.warning(f"Could not create bucket: {e}. This might be due to billing issues.")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred during bucket creation: {e}")
        return None

async def upload_blob(bucket, source_file_name, destination_blob_name):
    """
    Uploads a file to the bucket.
    """
    try:
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_name)
        logger.info(f"File {source_file_name} uploaded to {destination_blob_name}.")
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return None
