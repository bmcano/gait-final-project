import base64
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import requests
from textwrap import wrap

#
# Job: Holds additional helper functions unrelated to API calls or prompts
#
def encode_image_to_base64(image_path):
    """
    Encode an image to base64
    """
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string


def save_video(video_url, output_filename):
    """
    Save the given video url to the given filename
    """
    response = requests.get(video_url, stream=True)
    if response.status_code == 200:
        # Open a file in binary write mode and save the video content
        with open(f"static/temp/video/{output_filename}.mp4", "wb") as video_file:
            for chunk in response.iter_content(chunk_size=8192):
                video_file.write(chunk)
        print("Video saved.")
    else:
        print(f"Failed to save video. Status code: {response.status_code}, Error: {response.text}")


def save_itinerary_to_pdf(plain_text, file_path):
    """
    Save the given plain text as a PDF with text wrapping to prevent overflow.
    """
    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Create the PDF
    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter

    # Set up margins and font
    left_margin = 50
    right_margin = 50
    max_line_width = width - left_margin - right_margin  # Available width for text
    c.setFont("Helvetica", 12)

    # Add title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(left_margin, height - 50, "Travel Itinerary")
    y = height - 80  # Starting height for text
    line_height = 14

    # Handle text wrapping for each line
    c.setFont("Helvetica", 12)
    for line in plain_text.split("\n"):
        wrapped_lines = wrap(line, width=int(max_line_width / 6))  # Approx 6 pixels per character
        for wrapped_line in wrapped_lines:
            if y < 50:  # Start a new page if we're near the bottom
                c.showPage()
                y = height - 50
                c.setFont("Helvetica", 12)
            c.drawString(left_margin, y, wrapped_line)
            y -= line_height

    c.save()
