import requests
import math
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from utils import time_it 
import os
from db.main import create_database_connection , executes_sql_query  

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
conn = create_database_connection()

@time_it
def video_getter() -> Union[str, None]:


    """
    Fetches the URL of the latest completed video from a specified YouTube channel.

    Returns:
        Union[str, None]: The URL of the latest video, or None if an error occurs.
    """
    youtube_api_key = os.getenv('YOUTUBE_API_KEY')
    if not youtube_api_key:
        print("Error: YOUTUBE_API_KEY not found in environment variables.")
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
            print("No videos found for the specified channel.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"An error occurred with the YouTube API request: {e}")
        return None
    except KeyError as e:
        print(f"Error parsing YouTube API response: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def video_downloader(url: str) -> Union[Tuple[str, str], None]:
    """
    Downloads a video from a given YouTube URL.

    Args:
        url (str): The URL of the YouTube video.

    Returns:
        Union[Tuple[str, str], None]: A tuple containing the file path and sanitized project title, or None if an error occurs.
    """
    try:
        print("Starting download...")
        yt = YouTube(url)
        title = yt.title
        print(f"Video Title: {title}")

        sanitized_title = re.sub(r'[\\/:*?"<>|]', "", title)
        project_title = re.sub(r'\s+', "-", sanitized_title)
        
        output_path = Path("input")
        output_path.mkdir(exist_ok=True)
        
        filename = f"{sanitized_title}.mp4"
        filepath = output_path / filename

        stream = yt.streams.get_highest_resolution()
        if stream:
            stream.download(output_path=str(output_path), filename=filename)
            print(f"Video downloaded successfully: {filepath}")
            return str(filepath), project_title
        else:
            print("No suitable stream found for download.")
            return None
    except Exception as e:
        print(f"An error occurred during video download: {e}")
        return None


def process_segment(
    input_path: str,
    output_path: str,
    start_time: int,
    segment_duration: int,
    segment_index: int,
):
    """
    Processes a single video segment using ffmpeg.
    """
    print(f"Processing segment {segment_index + 1}: Writing to {output_path}...")
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
        print(f"Successfully created segment {segment_index + 1}")
        return None
    except ffmpeg.Error as e:
        error_message = (
            f"Error creating segment {segment_index + 1}: {e.stderr.decode()}"
        )
        print(error_message)
        return error_message


def video_editor(input_path: str, project_name: str) -> Union[Tuple[Path, str], None]:
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
        print("Error: Input path is not provided.")
        return None

    try:
        output_dir = Path(f"output/{project_name}")
        output_dir.mkdir(parents=True, exist_ok=True)

        probe = ffmpeg.probe(input_path)
        duration = float(probe["format"]["duration"])

        segment_duration = 15 * 60  # 15 minutes in seconds

        num_segments = math.ceil(duration / segment_duration)

        print(f"Video duration: {duration:.2f} seconds")
        print(
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
                    print(result)

        print(f"Successfully created {num_segments} video segments in {output_dir}")
        return output_dir, project_name

    except ffmpeg.Error as e:
        print(f"An ffmpeg error occurred: {e.stderr.decode()}")
        return None
    except Exception as e:
        print(f"An error occurred during video editing: {e}")
        return None
def compressor_out_dir(project_name:str):
    print('compressing the output folder')
    input_path = f'output/{project_name}/' 
    if not os.path.exists('final_project'):
        os.mkdir('final_project')
    output_name : str = f'final_project/{project_name}_final_version'
    archive_format : str = 'zip'
    try : 
        shutil.make_archive(output_name , archive_format, input_path)
        print(f"{project_name} is done compressing ")
    except Exception as e : 
        print(f'there was an error :{e}')
    finally:
        print('done')
def upload_to_cloud():
    print('uploading to the cloud')
    # Placeholder for cloud upload logic
    base_url = 'https://www.googleapis.com/drive/v3'

async def create_table():    
  create_table_query: str = """
    CREATE TABLE IF NOT EXISTS videoproject (
        project_name VARCHAR(255) NOT NULL,
        project_link TEXT
    );
    """
  executes_sql_query( create_table_query ,  conn)
    


def video_notifier(project_name: str):
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
        print("Error: SENDER_EMAIL or SENDER_PASSWORD not found in environment variables.")
        return
        
    body = f"The video project '{project_name}' has finished editing."
    emails: List[str] = ['jemolife69@gmail.com']

    for email in emails:
        try:
            msg = MIMEMultipart()
            msg['Subject'] = f'Your project is ready: {project_name}'
            msg['From'] = sender_email
            msg['To'] = email
            msg.attach(MIMEText( body, 'plain' ))
            with open(attachment, 'rb') as f:
                attach_file = MIMEApplication(f.read(), _subtype='zip')
                attach_file.add_header('Content-Disposition' , 'attachment')
                msg.attach(attach_file)

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(sender_email, sender_password)
                smtp.send_message(msg)
            print(f"Notification email sent successfully to {email}")
        except smtplib.SMTPAuthenticationError:
            print(f"Failed to send email to {email}: Authentication error. Please check your email and password.")
        except Exception as e:
            print(f"An error occurred while sending the email to {email}: {e}")

def main():
    """
    Main function to run the video processing pipeline.
    """
    url = video_getter()
    if url:
        download_info = video_downloader(url)
        if download_info:
            input_path, project_title = download_info
            editor_output = video_editor(input_path, project_title)
            if editor_output:
                _, project_name = editor_output
                compressor_out_dir(project_name=project_name)
                video_notifier(project_name=project_name)

if __name__ == "__main__":
    main()
