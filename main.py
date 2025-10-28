import requests
import math
import smtplib
import asyncio

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from utils import time_it, cleanup
import os
from database import init_db, SessionLocal
from storage.main import   upload_blob
from logger import get_logger
from models import Video

import shutil
import re
from dotenv import load_dotenv
from pathlib import Path
from typing import List, Dict, Union, Any, Tuple 
import ffmpeg
from pytubefix import YouTube
import concurrent.futures

# Load environment variables from .env file
load_dotenv()
logger = get_logger(__name__)


def video_getter() -> str | None:
    """
    Fetches the URL of the latest completed video from a specified YouTube channel.

    Returns:
        Union[str, None]: The URL of the latest video, or None if an error occurs.
    """
    youtube_api_key = os.getenv('YOUTUBE_API_KEY')
    if not youtube_api_key:
        logger.error("Error: YOUTUBE_API_KEY not found in environment variables.")
        return None

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
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        data = response.json()

        if 'items' in data and data['items']:
            video_id = data['items'][0]['id']['videoId']
            return f'https://www.youtube.com/watch?v={video_id}'
        else:
            logger.info("No videos found for the specified channel.")
            return None

    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred with the YouTube API request: {e}")
        return None
    except KeyError as e:
        logger.error(f"Error parsing YouTube API response: {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return None


def video_downloader(url: str) -> Tuple[str, str]| None:
    """
    Downloads a video from a given YouTube URL.

    Args:
        url (str): The URL of the YouTube video.

    Returns:
        Union[Tuple[str, str], None]: A tuple containing the file path and sanitized project title, or None if an error occurs.
    """
    try:
        logger.info("Starting download...")
        yt = YouTube(url)
        title = yt.title
        logger.info(f"Video Title: {title}")

        sanitized_title = re.sub(r'[\\/:*?"<>|]', "", title)
        project_title = re.sub(r'\s+', "-", sanitized_title)
        
        output_path = Path("input")
        output_path.mkdir(exist_ok=True)
        
        filename = f"{sanitized_title}.mp4"
        filepath = output_path / filename

        stream = yt.streams.get_highest_resolution()
        if stream:
            stream.download(output_path=str(output_path), filename=filename)
            logger.info(f"Video downloaded successfully: {filepath}")
            return str(filepath), project_title
        else:
            logger.info("No suitable stream found for download.")
            return None
    except Exception as e:
        logger.error(f"An error occurred during video download: {e}")
        return None


def process_segment(
    input_path: str,
    output_path: str,
    start_time: int,
    segment_duration: int,
    segment_index: int,
) -> str  |  None:
    """
    Processes a single video segment using ffmpeg.
    """
    logger.info(f"Processing segment {segment_index + 1}: Writing to {output_path}...")
    try:
        (
            ffmpeg.input(input_path, ss=start_time, t=segment_duration)
            .output(
                str(output_path),
                vcodec="libx264",
                acodec="aac",
                preset="fast",
                crf=23,
                ac=2,
                ar=44100,
                ab="128k",
                
            )
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True, quiet=True)
        )
        logger.info(f"Successfully created segment {segment_index + 1}")
        return None
    except ffmpeg.Error as e:
        error_message = (
            f"Error creating segment {segment_index + 1}: {e.stderr.decode()}"
        )
        logger.error(error_message)
        return error_message


def video_editor(input_path: str, project_name: str) -> Tuple[Path, str]| None:
    """
    This function edits a video by cutting it into 15-minute segments in parallel
    and saves them in the output folder using ffmpeg-python.

    Args:
        input_path (str): The path to the input video file.
        project_name (str): The name of the project.

    Returns:
        Union[Tuple[Path, str], None]: A tuple containing the output directory and project name, or None if an error occurs.
    """
    if not input_path:
        logger.error("Error: Input path is not provided.")
        return None

    try:
        output_dir = Path(f"output/{project_name}")
        output_dir.mkdir(parents=True, exist_ok=True)

        probe = ffmpeg.probe(input_path)
        duration = float(probe["format"]["duration"])

        segment_duration = 15 * 60  # 15 minutes in seconds

        num_segments = math.ceil(duration / segment_duration)

        logger.info(f"Video duration: {duration:.2f} seconds")
        logger.info(
            f"Creating {num_segments} segments of {segment_duration / 60:.1f} minutes each"
        )

        # this createe the thread the program use 
        with concurrent.futures.ThreadPoolExecutor() as executor:
            #
            futures = []
            for i in range(num_segments):
                start_time = i * segment_duration
                output_filename = f"{project_name}_segment_{i + 1:03d}.mp4"
                output_path = output_dir / output_filename
                futures.append(
                    # the executor start the job 
                    executor.submit(
                        process_segment,
                        input_path,
                        str(output_path),
                        start_time,
                        segment_duration,
                        i,
                    )
                )

            #  this wait for the task

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    # Log errors but continue processing other segments
                    logger.error(result)

        logger.info(f"Successfully created {num_segments} video segments in {output_dir}")
        return output_dir, project_name

    except ffmpeg.Error as e:
        logger.error(f"An ffmpeg error occurred: {e.stderr.decode()}")
        return None
    except Exception as e:
        logger.error(f"An error occurred during video editing: {e}")
        return None
def compressor_out_dir(project_name:str):
    logger.info('compressing the output folder')
    input_path = f'output/{project_name}/' 
    if not os.path.exists('final_project'):
        os.mkdir('final_project')
    output_name : str = f'final_project/{project_name}_final_version'
    archive_format : str = 'zip'
    try : 
        shutil.make_archive(output_name , archive_format, input_path)
        logger.info(f"{project_name} is done compressing ")
    except Exception as e : 
        logger.error(f'there was an error :{e}')
    finally:
        logger.info('done')
async def upload_to_db( project_name:str):
    logger.info('uploading to the cloud')
    # Placeholder for cloud upload logic
    try:
        download_link = await upload_blob(f'final_project/{project_name}_final_version.zip', f'{project_name}_project_final_version.zip')
        logger.info('Upload to cloud completed successfully.')
        if download_link:
            logger.info(f'Download link: {download_link}')
            # Save to database
            with SessionLocal() as session: # Get a session
                new_video = Video(video_name=project_name, project_link=download_link) # Create Video object
                session.add(new_video) # Add to session
                session.commit() # Commit the session
            logger.info('Video entry saved to database.')
            return download_link

    except Exception as e:
        logger.error(f'Error uploading to cloud: {e}')



def video_notifier(project_name: str , download_link : str | None = None):
    """
    Sends an email notification when the video processing is complete.

    Args:
        project_name (str): The name of the project to include in the email subject.
    """
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')
    attachment = f'final_project/{project_name}_final_version.zip'
    attachment_name = f'{project_name}_final_version.zip'
    attachment_path = f'final_project'

    if not sender_email or not sender_password:
        logger.error("Error: SENDER_EMAIL or SENDER_PASSWORD not found in environment variables.")
        return
        
    error_body = f"The video project '{project_name}' has finished editing. the download likn was not found"

    download_body = f"The video project '{project_name}' has finished editing. the link to download it is : {download_link}" 
    if download_link :

        emails: List[str] = ['jemolife69@gmail.com' , 'omoparioladavidola@gmail.com', 'heritageadewumivictor@gmail.com']
        for email in emails:
            try:
                msg = MIMEMultipart()
                msg['Subject'] = f'Your project is ready: {project_name}'
                msg['From'] = sender_email
                msg['To'] = email
                msg.attach(MIMEText( download_body, 'plain' ))

                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login(sender_email, sender_password)
                    smtp.send_message(msg)
                logger.info(f"Notification email sent successfully to {email}")
            except smtplib.SMTPAuthenticationError:
                logger.error(f"Failed to send email to {email}: Authentication error. Please check your email and password.")
            except Exception as e:
                logger.error(f"An error occurred while sending the email to {email}: {e}")
    else :

        emails: List[str] = ['jemolife69@gmail.com']
        for email in emails:
            try:
                msg = MIMEMultipart()
                msg['Subject'] = f'error on the project : {project_name}'
                msg['From'] = sender_email
                msg['To'] = email
                msg.attach(MIMEText( error_body, 'plain' ))

                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login(sender_email, sender_password)
                    smtp.send_message(msg)
                logger.info(f"Notification email sent successfully to {email}")
            except smtplib.SMTPAuthenticationError:
                logger.error(f"Failed to send email to {email}: Authentication error. Please check your email and password.")
            except Exception as e:
                logger.error(f"An error occurred while sending the email to {email}: {e}")






@time_it
async def main():

    """
    Main function to run the video processing pipeline.
    """

    init_db()
    # url = video_getter()
    url : str =  input("enter the url of the video you want to edit : ")
    if url:
        download_info = video_downloader(url)
        if download_info:
            input_path, project_title = download_info
            editor_output = video_editor(input_path, project_title)
            if editor_output:
                _, project_name = editor_output
                compressor_out_dir(project_name=project_name)
                download_link   = await upload_to_db(project_name=project_name)
                video_notifier(project_name=project_name, download_link=download_link)
    cleanup()

if __name__ == "__main__":
    asyncio.run(main())
