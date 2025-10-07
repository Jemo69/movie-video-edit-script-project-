import unittest
from unittest.mock import MagicMock, patch
import os
from storage import main
import google.api_core.exceptions

class TestStorage(unittest.TestCase):

    @patch('google.cloud.storage.Client')
    def test_create_bucket_exists(self, MockClient):
        mock_client_instance = MockClient.return_value
        mock_bucket = MagicMock()
        mock_bucket.name = "movie-edit"
        mock_client_instance.lookup_bucket.return_value = mock_bucket # Bucket exists
        mock_client_instance.get_bucket.return_value = mock_bucket # For the logger info

        result = main.create_bucket()
        self.assertEqual(result, mock_bucket)
        mock_client_instance.lookup_bucket.assert_called_with("movie-edit")
        mock_client_instance.create_bucket.assert_not_called()

    @patch('google.cloud.storage.Client')
    def test_create_bucket_new(self, MockClient):
        mock_client_instance = MockClient.return_value
        mock_bucket = MagicMock()
        mock_bucket.name = "movie-edit"
        mock_client_instance.lookup_bucket.return_value = None # Bucket does not exist
        mock_client_instance.create_bucket.return_value = mock_bucket
        mock_bucket.location = "US" # Set the location here

        result = main.create_bucket()
        self.assertEqual(result, mock_bucket)
        mock_client_instance.create_bucket.assert_called_once()
        self.assertEqual(mock_bucket.location, "US")

    @patch('google.cloud.storage.Client')
    def test_create_bucket_forbidden(self, MockClient):
        mock_client_instance = MockClient.return_value
        mock_client_instance.lookup_bucket.side_effect = google.api_core.exceptions.Forbidden("Permission denied")

        result = main.create_bucket()
        self.assertIsNone(result)

    @patch('storage.main.create_bucket')
    async def test_upload_blob_success(self, mock_create_bucket):
        mock_bucket = MagicMock()
        mock_create_bucket.return_value = mock_bucket
        mock_blob = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_blob.public_url = "http://example.com/test_blob"

        source_file = "test_file.txt"
        destination_blob = "test_destination.txt"
        
        # Create a dummy file for upload_from_filename
        with open(source_file, "w") as f:
            f.write("test content")

        result = await main.upload_blob(source_file, destination_blob)
        self.assertEqual(result, "http://example.com/test_blob")
        mock_create_bucket.assert_called_once()
        mock_bucket.blob.assert_called_with(destination_blob)
        mock_blob.upload_from_filename.assert_called_with(source_file)
        mock_blob.make_public.assert_called_once()

        os.remove(source_file) # Clean up dummy file

    @patch('storage.main.create_bucket')
    async def test_upload_blob_failure(self, mock_create_bucket):
        mock_bucket = MagicMock()
        mock_create_bucket.return_value = mock_bucket
        mock_blob = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_blob.upload_from_filename.side_effect = Exception("Upload failed")

        source_file = "test_file.txt"
        destination_blob = "test_destination.txt"

        with open(source_file, "w") as f:
            f.write("test content")

        result = await main.upload_blob(source_file, destination_blob)
        self.assertIsNone(result)
        os.remove(source_file) # Clean up dummy file

if __name__ == '__main__':
    unittest.main()
