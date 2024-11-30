import ffmpeg

def merge_clips_no_transition(clip1, clip2, output_file):
    """
    Merge two video clips sequentially without transitions.

    Args:
    - clip1 (str): Path to the first video file.
    - clip2 (str): Path to the second video file.
    - output_file (str): Path to save the output file.
    """
    # Create a temporary text file to list input files
    with open("file_list.txt", "w") as f:
        f.write(f"file '{clip1}'\n")
        f.write(f"file '{clip2}'\n")

    # Concatenate the clips using the file list
    ffmpeg.input("file_list.txt", format="concat", safe=0).output(output_file, c="copy").run(overwrite_output=True)

    # Clean up the temporary file
    import os
    os.remove("file_list.txt")

# Example Usage
if __name__ == "__main__":
    # Input video files
    clip1 = "cat.mp4"    # 8-second clip
    clip2 = "stars.mp4"  # 1-minute clip

    # Output video file
    output_file = "merged_no_transition.mp4"

    # Merge videos
    merge_clips_no_transition(clip1, clip2, output_file)
