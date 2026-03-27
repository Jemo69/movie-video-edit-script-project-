# ytsegment

Automated YouTube video processing pipeline — download, segment, compress, upload, and notify.

## Overview

`ytsegment` fetches the latest video from a YouTube channel, splits it into 15-minute segments using FFmpeg, compresses the output into a zip archive, uploads it to Google Cloud Storage, and sends email notifications with the download link.

## Pipeline

```
YouTube API → Download Video → Split into Segments → Compress → Upload to GCS → Email Notification
```

## Features

- **YouTube Integration** — Fetches the latest completed video from a target channel via the YouTube Data API
- **Parallel Video Processing** — Splits videos into 15-min segments using FFmpeg with concurrent processing
- **Cloud Storage** — Uploads compressed output to Google Cloud Storage
- **Database Tracking** — Stores video metadata in a database (Tortoise ORM / SQLAlchemy)
- **Email Notifications** — Notifies recipients when processing completes (success or failure)
- **Automatic Cleanup** — Removes temporary files after each run

## Prerequisites

- Python >= 3.12.11
- FFmpeg installed and available on `PATH`
- Google Cloud Storage credentials (`key.json`)
- YouTube Data API key
- Gmail account (for email notifications)

## Installation

```bash
# Clone the repo
git clone https://github.com/Jemo69/ytsegment.git 
cd ytsegment

# Install dependencies
pip install -r requirements.txt
```

Or using `uv`:

```bash
uv sync
```

## Configuration

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

```env
# Database Configuration (Turso/LibSQL)
TURSO_DATABASE_URL="libsql://your-database.turso.io"
TURSO_TOKEN="your_auth_token"

# Email Configuration
SENDER_EMAIL="your_email@gmail.com"
SENDER_PASSWORD="your_app_password"

# YouTube API
YOUTUBE_API_KEY="your_youtube_api_key"

# Google Cloud Storage
GOOGLE_APPLICATION_CREDENTIALS="key.json"
```

Place your Google Cloud service account key file as `key.json` in the project root.

## Usage

```bash
python main.py
```

The pipeline will:

1. Fetch the latest video URL from the configured YouTube channel
2. Download the video
3. Split it into 15-minute segments
4. Compress segments into a zip file
5. Upload to Google Cloud Storage
6. Send email notifications with the download link
7. Clean up temporary files

## Project Structure

```
ytsegment/
├── main.py              # Main pipeline orchestrator
├── src/
│   ├── database.py      # Database connection and initialization
│   ├── exceptions.py    # Custom exception classes
│   ├── logger.py        # Logging configuration
│   ├── models.py        # SQLAlchemy/Tortoise ORM models
│   ├── storage.py       # Google Cloud Storage operations
│   ├── type.py          # Type definitions
│   └── utils.py         # Utility functions (timing, cleanup)
├── input/               # Downloaded videos (auto-cleaned)
├── output/              # Segmented video output (auto-cleaned)
├── final_project/       # Compressed zip archives (auto-cleaned)
├── migrations/          # Database migrations
├── log/                 # Application logs
├── .env.example         # Environment variable template
├── pyproject.toml       # Project metadata and dependencies
└── requirements.txt     # Python dependencies
```

## Development

```bash
# Run tests
pytest

# Install dev dependencies
pip install -r requirements.txt
```

## License

MIT
