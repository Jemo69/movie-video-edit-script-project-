"""Custom exceptions for the video processing application."""

class VideoProcessingError(Exception):
    """Base exception for video processing errors."""
    pass

class VideoDownloadError(VideoProcessingError):
    """Raised when video download fails."""
    pass

class VideoEditingError(VideoProcessingError):
    """Raised when video editing fails."""
    pass

class VideoUploadError(VideoProcessingError):
    """Raised when video upload fails."""
    pass

class EmailNotificationError(VideoProcessingError):
    """Raised when email notification fails."""
    pass