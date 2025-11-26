"""Unit tests for main module functions."""
import pytest
from unittest.mock import Mock, patch
from main import video_getter, video_downloader
from exceptions import VideoDownloadError
from pathlib import Path

def test_video_getter_success(mock_env_vars, mock_youtube_response):
    """Test successful video URL retrieval."""
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = mock_youtube_response
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        url = video_getter()

        assert url == 'https://www.youtube.com/watch?v=test_video_id'
        mock_get.assert_called_once()

def test_video_getter_no_api_key():
    """Test video_getter raises error when API key is missing."""
    with patch.dict('os.environ', {}, clear=True):
        with pytest.raises(VideoDownloadError, match="YOUTUBE_API_KEY not found"):
            video_getter()

def test_video_getter_no_videos(mock_env_vars):
    """Test video_getter returns None when no videos found."""
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = {'items': []}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        url = video_getter()

        assert url is None

def test_video_getter_api_timeout(mock_env_vars):
    """Test video_getter handles API timeout."""
    with patch('requests.get') as mock_get:
        import requests
        mock_get.side_effect = requests.exceptions.Timeout()

        with pytest.raises(VideoDownloadError, match="timed out"):
            video_getter()

def test_video_downloader_success(mock_env_vars, temp_dir):
    """Test successful video download."""
    with patch('main.YouTube') as mock_yt:
        # Mock YouTube object
        mock_instance = Mock()
        mock_instance.title = "Test Video Title"
        mock_stream = Mock()
        mock_instance.streams.get_highest_resolution.return_value = mock_stream
        mock_yt.return_value = mock_instance

        # Mock download
        def mock_download(output_path, filename):
            filepath = Path(output_path) / filename
            filepath.parent.mkdir(exist_ok=True, parents=True)
            filepath.touch()
            # Write some content
            filepath.write_text("fake video content")

        mock_stream.download.side_effect = mock_download

        # Change to temp directory
        import os
        original_cwd = os.getcwd()
        os.chdir(temp_dir)

        try:
            result = video_downloader('https://youtube.com/watch?v=test')

            assert result is not None
            filepath, project_title = result
            assert Path(filepath).exists()
            assert project_title == "Test-Video-Title"
        finally:
            os.chdir(original_cwd)

def test_video_downloader_no_stream(mock_env_vars):
    """Test video_downloader handles missing stream."""
    with patch('main.YouTube') as mock_yt:
        mock_instance = Mock()
        mock_instance.title = "Test Video"
        mock_instance.streams.get_highest_resolution.return_value = None
        mock_yt.return_value = mock_instance

        with pytest.raises(VideoDownloadError, match="No suitable stream"):
            video_downloader('https://youtube.com/watch?v=test')

def test_video_downloader_retries(mock_env_vars):
    """Test video_downloader retry logic."""
    with patch('main.YouTube') as mock_yt:
        mock_yt.side_effect = Exception("Download failed")

        with pytest.raises(VideoDownloadError, match="Failed to download after 3 attempts"):
            video_downloader('https://youtube.com/watch?v=test', max_retries=3)

        assert mock_yt.call_count == 3