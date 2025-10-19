"""Integration tests for the full pipeline."""
import pytest
from unittest.mock import patch
from main import main
import os

@pytest.mark.asyncio
async def test_full_pipeline_success(mock_env_vars, temp_dir):
    """Test complete pipeline execution."""
    original_cwd = os.getcwd()
    os.chdir(temp_dir)

    try:
        with patch('main.video_getter') as mock_getter, \
             patch('main.video_downloader') as mock_downloader, \
             patch('main.video_editor') as mock_editor, \
             patch('main.compressor_out_dir') as mock_compressor, \
             patch('main.upload_to_db') as mock_upload, \
             patch('main.video_notifier') as mock_notifier, \
             patch('main.cleanup') as mock_cleanup, \
             patch('main.init_db') as mock_init_db:

            # Setup mocks
            mock_getter.return_value = 'https://youtube.com/watch?v=test'
            mock_downloader.return_value = ('input/test.mp4', 'test-project')

            # Create a dummy output directory for the editor to return
            output_dir = temp_dir / 'output'
            output_dir.mkdir()
            mock_editor.return_value = (output_dir, 'test-project')

            mock_compressor.return_value = 'final_project/test.zip'
            mock_upload.return_value = 'https://storage.example.com/test.zip'

            # Run pipeline
            await main()

            # Verify all steps were called
            mock_init_db.assert_called_once()
            mock_getter.assert_called_once()
            mock_downloader.assert_called_once_with('https://youtube.com/watch?v=test')
            mock_editor.assert_called_once_with('input/test.mp4', 'test-project')
            mock_compressor.assert_called_once_with('test-project')
            mock_upload.assert_called_once_with('test-project')
            mock_notifier.assert_called_once_with('test-project', 'https://storage.example.com/test.zip')
            mock_cleanup.assert_called_once()
    finally:
        os.chdir(original_cwd)

@pytest.mark.asyncio
async def test_pipeline_handles_download_failure(mock_env_vars, temp_dir):
    """Test pipeline handles download failures gracefully."""
    from exceptions import VideoDownloadError

    original_cwd = os.getcwd()
    os.chdir(temp_dir)

    try:
        with patch('main.video_getter') as mock_getter, \
             patch('main.video_downloader') as mock_downloader, \
             patch('main.video_editor') as mock_editor, \
             patch('main.video_notifier') as mock_notifier, \
             patch('main.cleanup') as mock_cleanup, \
             patch('main.init_db') as mock_init_db:

            mock_getter.return_value = 'https://youtube.com/watch?v=test'
            # Simulate a failure in the downloader
            mock_downloader.side_effect = VideoDownloadError("Download failed")

            # The main function should catch this and exit gracefully
            await main()

            # Verify that the pipeline stopped after the failure
            mock_init_db.assert_called_once()
            mock_getter.assert_called_once()
            mock_downloader.assert_called_once()
            mock_editor.assert_not_called() # Should not be called
            mock_notifier.assert_not_called() # Should not be called when download fails before project_name is set
            mock_cleanup.assert_called_once()
    finally:
        os.chdir(original_cwd)