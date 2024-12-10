import ffmpeg
import os

def merge_clips_no_transition(video_paths):
    """
    Merge two video clips sequentially without transitions.

    Args:
    - video_paths (List<str>): paths of all the video files.
    
    Returns:
    - str: Path to the final merged video.
    """
    # Create temp directory if not exists
    os.makedirs("static/temp/video", exist_ok=True)
    
    normalized_files = []
    for i, video in enumerate(video_paths):
        normalized_file = f"static/temp/video/{i}.mp4"
        (
            ffmpeg
            .input(video)
            .output(normalized_file, vcodec='libx264', acodec='aac', strict='experimental')
            .run(overwrite_output=True)
        )
        normalized_files.append(normalized_file)

    # Create a text file listing all video files to concatenate
    concat_file = "static/temp/video/concat_list.txt"
    with open(concat_file, "w") as f:
        for file in normalized_files:
            # Ensure the paths are correct
            absolute_path = os.path.abspath(file)
            f.write(f"file '{absolute_path}'\n")

    # Concatenate videos using ffmpeg
    output_file = "static/temp/video/final.mp4"
    (
        ffmpeg
        .input(concat_file, format="concat", safe=0)
        .output(output_file, c="copy")
        .run(overwrite_output=True)
    )

    # Clean up temporary files
    os.remove(concat_file)
    for file in normalized_files:
        os.remove(file)

    return output_file

# Example usage
# video_paths = ["static/mock_videos/video1.mp4", "static/mock_videos/video2.mp4"]
# output_path = merge_clips_no_transition(video_paths)
# print(f"Merged video saved to: {output_path}")
