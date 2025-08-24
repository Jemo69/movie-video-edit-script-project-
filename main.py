

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


def video_editor(input_path: str, project_name: str):
    """
    This function edits a video by cutting it into 15-minute segments
    and saves them in the output folder
    """

    try:
        output_dir = Path(f"output/{project_name}")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Load the original video
        original_clip = mp.VideoFileClip(input_path)
        duration = original_clip.duration

        # Set segment duration to 15 minutes
        segment_duration = 15 * 60  # 15 minutes = 900 seconds

        # Calculate number of segments needed
        num_segments = math.ceil(duration / segment_duration)

        print(f"Video duration: {duration:.2f} seconds")
        print(
            f"Creating {num_segments} segments of {segment_duration / 60:.1f} minutes each"
        )

        # Cut the video into 30-second segments
        for i in range(num_segments):
            start_time = i * segment_duration
            end_time = min(
                (i + 1) * segment_duration, duration
            )  # Don't exceed video duration

            print(
                f"Processing segment {i + 1}: {start_time / 60:.1f}min to {end_time / 60:.1f}min"
            )

            # Use subclip to get the desired segment
            subclip = original_clip.subclipped(start_time, end_time)

            # Create output filename and full path
            output_filename = f"{project_name}_segment_{i + 1:03d}.mp4"
            output_path = output_dir / output_filename
            output_as_string = str(output_path)

            print(f"Writing clip {i + 1} to {output_path}...")

            # Write the subclip to a new file in the output directory
            subclip.write_videofile(
                output_as_string,
                codec="libx264",
                audio_codec="aac",
                verbose=False,
                logger=None,
            )

            # Close the subclip to free memory
            subclip.close()

        # Close the original clip to free up resources (moved outside the loop)
        original_clip.close()

        print(f"Successfully created {num_segments} video segments in {output_dir}")
        return output_dir
    except Exception as e:
        print(f"An error occurred: {e}")
        return str(e)


if __name__ == "__main__":
    tell_video = video_downloader(
        "https://www.youtube.com/live/gGFQuTMHCZg?si=OTEXY3a3T0Zi0xOs"
    )
    video_editor(tell_video, "zen")
