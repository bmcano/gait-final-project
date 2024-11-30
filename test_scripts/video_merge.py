import ffmpeg

def merge_two_clips_with_transition(clip1, clip2, output_file, transition_duration=1):
    """
    Merge two video clips with a crossfade transition.

    Args:
    - clip1 (str): Path to the first video file.
    - clip2 (str): Path to the second video file.
    - output_file (str): Path to save the output file.
    - transition_duration (int): Duration of the crossfade transition in seconds.
    """
    # Load input videos
    input1 = ffmpeg.input(clip1)
    input2 = ffmpeg.input(clip2)

    # Define the filter complex for crossfade
    filter_complex = (
        f"[0:v]trim=0,setpts=PTS-STARTPTS[v0];"
        f"[0:a]atrim=0,asetpts=PTS-STARTPTS[a0];"
        f"[1:v]trim=0,setpts=PTS-STARTPTS[v1];"
        f"[1:a]atrim=0,asetpts=PTS-STARTPTS[a1];"
        f"[v0][a0][v1][a1]xfade=transition=fade:duration={transition_duration}:offset=PTS-STARTPTS[outv][outa]"
    )

    # Run FFmpeg command
    (
        ffmpeg
        .input(clip1)
        .input(clip2)
        .output(output_file, v="outv", a="outa", filter_complex=filter_complex)
        .run(overwrite_output=True)
    )

# Example Usage
if __name__ == "__main__":
    # Define the input clips
    clip1 = "sunflower.mp4"
    clip2 = "cinematic-background-hd.mp4"

    # Define the output file name
    output_file = "merged_with_transition.mp4"

    # Merge the clips with a 2-second crossfade transition
    merge_two_clips_with_transition(clip1, clip2, output_file, transition_duration=2)
