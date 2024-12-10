import ffmpeg
import os

def merge_clips_no_transition(video_paths):
    """
    Merge two video clips sequentially without transitions.

    Args:
    - video_paths (List<str>): paths of all the video files
    - output_file (str): Path to save the output file.
    """
    # Normalize videos to the same codec and format if needed
    normalized_files = []
    for i, video in enumerate(video_paths):
        normalized_file = f"temp/video/{i}"
        (
            ffmpeg
            .input(video)
            .output(normalized_file, vcodec='libx264', acodec='aac', strict='experimental')
            .run(overwrite_output=True)
        )
        normalized_files.append(normalized_file)

    # Create a text file listing all video files to concatenate
    concat_file = "temp/video/concat_list.txt"
    with open(concat_file, "w") as f:
        for file in normalized_files:
            f.write(f"file '{file}'\n")

    # Concatenate videos using ffmpeg
    output_file = "temp/video/final.mp4"
    (
        ffmpeg
        .input(concat_file, format="concat", safe=0)
        .output(output_file, c="copy")
        .run(overwrite_output=True)
    )

    # Return the path to the final merged video
    os.remove(concat_file)
    return output_file

# Example ussage
# video_paths = ["static/mock_videos/video1.mp4", "static/mock_videos/video2.mp4"]
# output_path = merge_clips_no_transition(video_paths)
# print(f"Merged video saved to: {output_path}")