
import math
import os 
import re
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
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
    target_id = 'UCL9c56uR0zI_h2K_jT0_c2g'
    YOUTUBE_API_SERVICE_NAME: str = "youtube"
    YOUTUBE_API_VERSION: str = "v3"
    try:
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=youtube_api_key)

        # Search for active livestreams on the specified channel
        search_response: Dict[str, Any] = youtube.search().list(
            channelId=target_id,
            part="snippet",
            eventType="completed",
            type="video",
            maxResults=1
        ).execute()

        videos: List[Dict[str, Any]] = search_response.get("items", [])

        if not videos:
            print(f"No active livestream found for channel ID: {channel_id}")
            return None

        # Assuming the first result is the current livestream
        video_id: str = videos[0]["id"]["videoId"]
        live_stream_url: str = f"https://www.youtube.com/watch?v={video_id}"
        
        print(f"Found active livestream: {live_stream_url}")
        return live_stream_url

    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred: {e.content}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def video_downloader(url: str) -> str:
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
        stream = yt.streams.get_highest_resolution()
        assert stream is not None
        stream.download(output_path="input", filename=f"{sanitized_title}.mp4")
        print(f"Video downloaded successfully. {sanitized_title}")
        return f"input/{sanitized_title}.mp4"

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
        return output_dir

    except Exception as e:
        print(f"An error occurred: {e}")
        return None




if __name__ == "__main__":
    urlget = video_getter()
    tell_video = video_downloader(
            urlget
    )
    video_editor(tell_video, "a-new-thing-part-3")
