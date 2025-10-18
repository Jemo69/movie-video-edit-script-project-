"""Pytest configuration and fixtures."""
import pytest
import os
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile
import shutil

@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)

@pytest.fixture
def mock_env_vars():
    """Mock environment variables."""
    with patch.dict(os.environ, {
        'YOUTUBE_API_KEY': 'test_api_key',
        'SENDER_EMAIL': 'test@example.com',
        'SENDER_PASSWORD': 'test_password',
        'TURSO_DATABASE_URL': 'file:test.db',
        'TURSO_TOKEN': 'test_token'
    }):
        yield

@pytest.fixture
def mock_youtube_response():
    """Mock YouTube API response."""
    return {
        'items': [{
            'id': {'videoId': 'test_video_id'},
            'snippet': {'title': 'Test Video'}
        }]
    }

@pytest.fixture
def sample_video_path(temp_dir):
    """Create a sample video file for testing."""
    video_path = temp_dir / 'test_video.mp4'
    video_path.touch()
    return str(video_path)