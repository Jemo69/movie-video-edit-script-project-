import requests
import smtplib
from email.message import EmailMessage
import os 
import re
from dotenv import load_dotenv
from pathlib import Path

from typing import List , Dict,  Union,  Any

import ffmpeg
from pytubefix import YouTube
load_dotenv()

def video_getter() -> Union[str , None]  :
    """
    this was design to go on the web and get the video 

    """
    youtube_api_key = os.getenv('YOUTUBE_API_KEY')
    # target_id = 'rccgtphb3768'
    target_id = 'UC-mvrwYr8tk6Gk8H3C8r1bg'
    YOUTUBE_API_SERVICE_NAME: str = "youtube"
    YOUTUBE_API_VERSION: str = "v3"
    base_url: str = 'https://www.googleapis.com/youtube/v3/search'
    params: Dict[str, str | int] = {
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
        data   = response.json()
        print(response)
        print(data)

        video_id : str  =  data['items'][0]['id']['videoId']
        
        return f'https://www.youtube.com/watch?v={video_id}' 



        # Assuming the first result is the current livestream
        

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def video_downloader(url: str) -> List[str]:
    """
    this function is a function that downloads a video from a url
     arg:
         url of type string
    """
    try:
        print("start download")
        yt = YouTube(url)
        title = yt.title
        print(title)
        sanitized_title = re.sub(r'[\\/:*?"<>|]', "", title)
        project_title = re.sub(r' ',"-", sanitized_title)
        stream = yt.streams.get_highest_resolution()
        assert stream is not None
        stream.download(output_path="input", filename=f"{sanitized_title}.mp4")
        print(f"Video downloaded successfully. {sanitized_title}")
        return [ f"input/{sanitized_title}.mp4" , project_title ]
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def video_editor(input_path: str, project_name: str):
    """

    This function edits a video by cutting it into 30-minute segments
    and saves them in the output folder using ffmpeg-python
    """
    if input_path is None:

        return None

    """
    This function edits a video by cutting it into 15-minute segments
    and saves them in the output folder
    """


    try:
        output_dir = Path(f"output/{project_name}")
        output_dir.mkdir(parents=True, exist_ok=True)


        # Get video duration using ffprobe
        probe = ffmpeg.probe(input_path)
        duration = float(probe["streams"][0]["duration"])

        # Set segment duration to 30 minutes
        segment_duration = 15 * 60  # 30 minutes = 1800 seconds

        # Calculate number of segments needed
        num_segments = math.ceil(duration / segment_duration)

        print(f"Video duration: {duration:.2f} seconds")
        print(
            f"Creating {num_segments} segments of {segment_duration / 60:.1f} minutes each"
        )

        # Cut the video into 30-minute segments

        for i in range(num_segments):
            start_time = i * segment_duration
            end_time = min(
                (i + 1) * segment_duration, duration
            )  # Don't exceed video duration


            print(
                f"Processing segment {i + 1}: {start_time / 60:.1f}min to {end_time / 60:.1f}min"
            )

            # Create output filename and full path
            output_filename = f"{project_name}_segment_{i + 1:03d}.mp4"
            output_path = output_dir / output_filename
            output_as_string = str(output_path)

            print(f"Writing clip {i + 1} to {output_path}...")

            # Use ffmpeg to cut the video segment
            try:
                (
                    ffmpeg.input(input_path, ss=start_time, t=end_time - start_time)
                    .output(
                        output_as_string,
                        vcodec="libx264",
                        acodec="aac",
                        preset="fast",
                        crf=23,
                        ac=2,  # Ensure audio channels are preserved
                        ar=44100,  # Set audio sample rate
                        ab="128k",  # Audio bitrate for better quality
                    )
                    .overwrite_output()
                    .run(capture_stdout=True, capture_stderr=True, quiet=True)
                )
                print(f"Successfully created segment {i + 1}")
            except ffmpeg.Error as e:
                print(f"Error creating segment {i + 1}: {e.stderr.decode()}")
                continue

        print(f"Successfully created {num_segments} video segments in {output_dir}")
        return [ output_dir , project_name]

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
def subtitle_generator():
    pass
def video_notifier(project_name : str ):
    sender_email = os.getenv('SENDER_EMAIL')
    body = """
    the video has finishing editing and it hope it working 
    """
    sender_password = os.getenv('SENDER_PASSWORD')
    emails : List[str] = ['jemolife69@gmail.com']
    for email in emails:
        try: 
            msg : EmailMessage = EmailMessage()
            msg['Subject']=f'you are project is ready {project_name} '
            msg['From']=sender_email
            msg['To']=email
            msg.set_content(body)
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login(sender_email , sender_password)
                    smtp.send_message(msg)
                    print(f'done with { email} ')    
        except Exception as e:
            print(e)

                    


def main():
    urlget = video_getter()
    tell_video = video_downloader(urlget)
    finished_product = video_editor(tell_video[0],tell_video[1])
    noti = video_notifier(project_name=finished_product[1])

if __name__ == "__main__":
    main()
