import ffmpeg

def merge_two_clips(clip1, clip2, output_file):
    """
    Merge two video clips sequentially using FFmpeg.

    Args:
    - clip1 (str): Path to the first video file.
    - clip2 (str): Path to the second video file.
    - output_file (str): Path to save the output file.
    """
    (
        ffmpeg
        .concat(
            ffmpeg.input(clip1),
            ffmpeg.input(clip2),
            v=1, a=1  # Enable video and audio
        )
        .output(output_file)
        .run(overwrite_output=True)
    )

# Example Usage
if __name__ == "__main__":
    # Input video files
    clip1 = "sunflower.mp4"
    clip2 = "cinematic-background-hd.mp4"

    # Output video file
    output_file = "merged_output.mp4"

    # Merge videos
    merge_two_clips(clip1, clip2, output_file)
