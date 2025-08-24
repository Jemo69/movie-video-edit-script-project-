import math
import re
from pathlib import Path

import ffmpeg
from pytubefix import YouTube


def video_downloader(url: str) -> str | None:
    """
    this function is a function that downloads a video from a url
     arg:
     url of type string
    """
    try:
        yt = YouTube(url)
        title = yt.title
        sanitized_title = re.sub(r'[\\/:*?"<>|]', "", title)
        stream = yt.streams.get_highest_resolution()
        assert stream is not None
        stream.download(output_path="input", filename=f"{sanitized_title}.mp4")
        print(f"Video downloaded successfully. {sanitized_title}")
        return f"input/{sanitized_title}.mp4"

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def video_editor(input_path: str | None, project_name: str):
    """
    This function edits a video by cutting it into 30-minute segments
    and saves them in the output folder using ffmpeg-python
    """
    if input_path is None:
        return None

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
    tell_video = video_downloader(
        "https://www.youtube.com/live/gGFQuTMHCZg?si=OTEXY3a3T0Zi0xOs"
    )
    video_editor(tell_video, "a-new-thing-part-3")
