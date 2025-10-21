import requests
import math
import smtplib
import asyncio
import traceback

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from utils import time_it, cleanup
import os
from database import init_db, get_session
from storage.main import upload_blob
from logger import get_logger
from models import Video
from exceptions import (
    VideoDownloadError,
    VideoEditingError,
    VideoUploadError,
    EmailNotificationError
)

import shutil
import re
from dotenv import load_dotenv
from pathlib import Path
from typing import List, Dict, Union, Tuple
import ffmpeg
import yt_dlp
import concurrent.futures

load_dotenv()
logger = get_logger(__name__)


def video_getter() -> Union[str, None]:
    """
    Fetches the URL of the latest completed video from a specified YouTube channel.

    Returns:
        Union[str, None]: The URL of the latest video, or None if an error occurs.

    Raises:
        VideoDownloadError: If the API request fails
    """
    youtube_api_key = os.getenv('YOUTUBE_API_KEY')
    if not youtube_api_key:
        raise VideoDownloadError("YOUTUBE_API_KEY not found in environment variables")

    target_id = 'UC-mvrwYr8tk6Gk8H3C8r1bg'
    base_url = 'https://www.googleapis.com/youtube/v3/search'
    params: Dict[str, Union[str, int]] = {
        'part': 'snippet',
        'channelId': target_id,
        'eventType': 'completed',
        'type': 'video',
        'order': 'date',
        'maxResults': 1,
        'key': youtube_api_key,
    }

    try:
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        if 'items' in data and data['items']:
            video_id = data['items'][0]['id']['videoId']
            video_url = f'https://www.youtube.com/watch?v={video_id}'
            logger.info(f"Found video: {video_url}")
            return video_url
        else:
            logger.warning("No videos found for the specified channel")
            return None

    except requests.exceptions.Timeout:
        logger.error("YouTube API request timed out")
        raise VideoDownloadError("YouTube API request timed out")
    except requests.exceptions.RequestException as e:
        logger.error(f"YouTube API request failed: {e}")
        raise VideoDownloadError(f"YouTube API request failed: {e}")
    except KeyError as e:
        logger.error(f"Error parsing YouTube API response: {e}")
        raise VideoDownloadError(f"Invalid API response format: {e}")


def video_downloader(url: str, max_retries: int = 3) -> Union[Tuple[str, str], None]:
    """
    Downloads a video from a given YouTube URL with retry logic using yt-dlp.

    Args:
        url (str): The URL of the YouTube video
        max_retries (int): Maximum number of download attempts

    Returns:
        Union[Tuple[str, str], None]: A tuple of (file_path, project_title) or None

    Raises:
        VideoDownloadError: If download fails after retries
    """
    output_path = Path("input")
    output_path.mkdir(exist_ok=True)

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': str(output_path / '%(title)s.%(ext)s'),
        'retries': max_retries,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'untitled')
            filename = ydl.prepare_filename(info)

            sanitized_title = re.sub(r'[\\/:*?"<>|]', "", title)
            project_title = re.sub(r'\s+', "-", sanitized_title)

            logger.info(f"Video downloaded successfully: {filename}")
            return str(filename), project_title

    except Exception as e:
        logger.error(f"Download failed after {max_retries} attempts: {e}")
        raise VideoDownloadError(f"Failed to download after {max_retries} attempts: {e}")


def video_editor(input_path: str, project_name: str) -> Union[Tuple[Path, str], None]:
    """
    Edits a video by cutting it into 15-minute segments in parallel.

    Args:
        input_path (str): Path to the input video file
        project_name (str): Name of the project

    Returns:
        Union[Tuple[Path, str], None]: Tuple of (output_dir, project_name) or None

    Raises:
        VideoEditingError: If editing fails
    """
    if not input_path:
        raise VideoEditingError("Input path is not provided")

    input_file = Path(input_path)
    if not input_file.exists():
        raise VideoEditingError(f"Input file does not exist: {input_path}")

    try:
        output_dir = Path(f"output/{project_name}")
        output_dir.mkdir(parents=True, exist_ok=True)

        probe = ffmpeg.probe(input_path)
        duration = float(probe["format"]["duration"])

        segment_duration = 15 * 60  # 15 minutes in seconds
        num_segments = math.ceil(duration / segment_duration)

        logger.info(f"Video duration: {duration:.2f} seconds")
        logger.info(f"Creating {num_segments} segments of {segment_duration / 60:.1f} minutes each")

        errors = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for i in range(num_segments):
                start_time = i * segment_duration
                output_filename = f"{project_name}_segment_{i + 1:03d}.mp4"
                output_path = output_dir / output_filename
                futures.append(
                    executor.submit(
                        process_segment,
                        input_path,
                        str(output_path),
                        start_time,
                        segment_duration,
                        i,
                    )
                )

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    errors.append(result)

        if errors:
            error_msg = f"Failed to create {len(errors)} segments: {'; '.join(errors)}"
            logger.error(error_msg)
            raise VideoEditingError(error_msg)

        logger.info(f"Successfully created {num_segments} video segments in {output_dir}")
        return output_dir, project_name

    except ffmpeg.Error as e:
        error_msg = f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}"
        logger.error(error_msg)
        raise VideoEditingError(error_msg)
    except Exception as e:
        logger.error(f"Error during video editing: {e}")
        raise VideoEditingError(f"Video editing failed: {e}")


def compressor_out_dir(project_name: str) -> str:
    """
    Compresses the output folder into a zip file.

    Args:
        project_name: Name of the project

    Returns:
        str: Path to the compressed file

    Raises:
        VideoEditingError: If compression fails
    """
    logger.info('Compressing the output folder')
    input_path = f'output/{project_name}/' 

    if not os.path.exists('final_project'):
        os.mkdir('final_project')

    output_name = f'final_project/{project_name}_final_version'
    archive_format = 'zip'

    try:
        archive_path = shutil.make_archive(output_name, archive_format, input_path)
        logger.info(f"{project_name} compressed successfully")
        return archive_path
    except Exception as e:
        logger.error(f'Compression error: {e}')
        raise VideoEditingError(f'Failed to compress output: {e}')


async def upload_to_db(project_name: str) -> str:
    """
    Uploads the compressed video to cloud storage and saves to database.

    Args:
        project_name: Name of the project

    Returns:
        str: Download link for the uploaded file

    Raises:
        VideoUploadError: If upload fails
    """
    logger.info('Uploading to the cloud')

    try:
        file_path = f'final_project/{project_name}_final_version.zip'

        if not os.path.exists(file_path):
            raise VideoUploadError(f"Compressed file not found: {file_path}")

        download_link = await upload_blob(
            file_path,
            f'{project_name}_project_final_version.zip'
        )

        if not download_link:
            raise VideoUploadError("Failed to get download link from cloud storage")

        logger.info(f'Upload completed. Download link: {download_link}')

        # Save to database
        with get_session() as session:
            new_video = Video(video_name=project_name, project_link=download_link)
            session.add(new_video)
            session.commit()

        logger.info('Video entry saved to database')
        return download_link

    except Exception as e:
        logger.error(f'Upload error: {e}', exc_info=True)
        raise VideoUploadError(f'Failed to upload: {e}')


def video_notifier(project_name: str, download_link: str | None = None):
    """
    Sends an email notification when video processing is complete.

    Args:
        project_name: Name of the project
        download_link: Download link (None if upload failed)

    Raises:
        EmailNotificationError: If email sending fails
    """
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')

    if not sender_email or not sender_password:
        raise EmailNotificationError("SENDER_EMAIL or SENDER_PASSWORD not found")
        
    if download_link:
        body = f"The video project '{project_name}' has finished editing.\n\nDownload link: {download_link}"
        emails = ['jemolife69@gmail.com', 'omoparioladavidola@gmail.com', 'heritageadewumivictor@gmail.com']
        subject = f'Your project is ready: {project_name}'
    else:
        body = f"The video project '{project_name}' has finished editing, but the download link was not generated."
        emails = ['jemolife69@gmail.com']
        subject = f'Error on project: {project_name}'

    errors = []
    for email in emails:
        try:
            msg = MIMEMultipart()
            msg['Subject'] = subject
            msg['From'] = sender_email
            msg['To'] = email
            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=30) as smtp:
                smtp.login(sender_email, sender_password)
                smtp.send_message(msg)

            logger.info(f"Notification email sent successfully to {email}")

        except smtplib.SMTPAuthenticationError:
            error = f"Authentication error for {email}"
            logger.error(error)
            errors.append(error)
        except Exception as e:
            error = f"Failed to send email to {email}: {e}"
            logger.error(error)
            errors.append(error)

    if errors and len(errors) == len(emails):
        raise EmailNotificationError(f"Failed to send all emails: {'; '.join(errors)}")


@time_it
async def main():
    """
    Main function to run the video processing pipeline.
    """
    project_name = None

    try:
        logger.info("=" * 50)
        logger.info("Starting video processing pipeline")
        logger.info("=" * 50)

        # Initialize database
        init_db()
        logger.info("Database initialized")

        # Get video URL
        url = video_getter()
        if not url:
            logger.error("No video URL found. Exiting.")
            return

        # Download video
        download_info = video_downloader(url)
        if not download_info:
            logger.error("Video download failed. Exiting.")
            return

        input_path, project_name = download_info

        # Edit video
        editor_output = video_editor(input_path, project_name)
        if not editor_output:
            logger.error("Video editing failed. Exiting.")
            return

        _, project_name = editor_output

        # Compress output
        compressor_out_dir(project_name)

        # Upload to cloud and database
        download_link = await upload_to_db(project_name)

        # Send success notification
        video_notifier(project_name, download_link)

        logger.info("=" * 50)
        logger.info("Video processing completed successfully")
        logger.info("=" * 50)

    except VideoDownloadError as e:
        logger.error(f"Download failed: {e}", exc_info=True)
        if project_name:
            try:
                video_notifier(project_name, None)
            except:
                pass

    except VideoEditingError as e:
        logger.error(f"Editing failed: {e}", exc_info=True)
        if project_name:
            try:
                video_notifier(project_name, None)
            except:
                pass

    except VideoUploadError as e:
        logger.error(f"Upload failed: {e}", exc_info=True)
        if project_name:
            try:
                video_notifier(project_name, None)
            except:
                pass

    except EmailNotificationError as e:
        logger.error(f"Email notification failed: {e}", exc_info=True)

    except Exception as e:
        logger.error(f"Unexpected error in main: {e}", exc_info=True)
        logger.error(f"Traceback: {traceback.format_exc()}")
        if project_name:
            try:
                video_notifier(project_name, None)
            except:
                pass
        raise

    finally:
        # Always cleanup temporary files
        try:
            cleanup()
            logger.info("Cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())