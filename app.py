from flask import Flask, render_template, request
import os
from datetime import datetime
import replicate
from config import DEMO_MODE, MOCK_ITINERARIES, MOCK_WEATHER_INFO
from dotenv import load_dotenv

app = Flask(__name__)

# Configurations
# These folders contain the images generated by AI
app.config['IMAGE_FOLDER'] = 'temp/images'
app.config['VIDEO_FOLDER'] = 'temp/video'

@app.route('/')
def index():
    """
    Landing page where users enter destination and travel dates.
    """
    return render_template('index.html')

@app.route('/itineraries', methods=['POST'])
def itineraries():
    """
    Page showing multiple itinerary options in horizontal cards.
    """
    # Extract user inputs
    destination = request.form['destination']
    from_date = request.form['fromDate']
    to_date = request.form['toDate']
    travel_dates = from_date + " to " + to_date

    # Parse dates and calculate trip duration
    try:
        from_date_obj = datetime.strptime(from_date, "%Y-%m-%d")
        to_date_obj = datetime.strptime(to_date, "%Y-%m-%d")
        trip_duration = (to_date_obj - from_date_obj).days + 1
    except ValueError:
        return "Invalid date format. Please ensure dates are in YYYY-MM-DD format."

    # TODO: Use destination and dates to call the weather API and retrieve weather info.
    # Store the result in `weather_info` and pass it to the frontend instead of MOCK_WEATHER_INFO.
    weather_info = MOCK_WEATHER_INFO

    # TODO: Use ChatGPT to dynamically generate itineraries using destination, dates, and weather info
    # Replace MOCK_ITINERARIES with actual data from ChatGPT's response.
    itineraries = MOCK_ITINERARIES

    # TODO: Get prompt from ChatGPT to generate images
    prompt = ''

    # TODO: Generate images based on the destination, itineraries, weather (e.g. snowy shot of user's travel destination)
    # Use the `generate_image` function below to create images for each itinerary.
    # For now, simulate generated images as placeholders.
    generated_images = generate_image(prompt=prompt, num_images=len(itineraries))

    # Pass mock or generated data to the template
    return render_template(
        'itineraries.html',
        destination=destination,
        from_date=from_date,
        to_date=to_date,
        travel_dates=travel_dates,
        trip_duration=trip_duration,
        itineraries=itineraries,  # Pass generated itineraries here
        images=generated_images  # Pass generated images to the frontend
    )

@app.route('/itinerary_details', methods=['POST'])
def itinerary_details():
    """
    Page showing detailed itinerary, weather, and packing suggestions.
    """
    # Extract selected itinerary (index of selected card)
    selected_index = request.form.get('selected_indices', '')
    selected_indices = [int(idx) for idx in selected_index.split(',') if idx.isdigit()]
    selected_itineraries = [MOCK_ITINERARIES[idx] for idx in selected_indices]

    # Mock packing list
    # TODO: Use ChatGPT to dynamically generate packing suggestions based on destination, weather, and itinerary.
    packing_list = ["Sunscreen", "Comfortable shoes", "Hat", "Reusable water bottle"]

    # TODO: Call generate_image function to create AI-generated images of landmarks or activities in the itinerary.
    # Save the generated images in app.config['IMAGE_FOLDER'].
    # Placeholder example for generated images:
    generated_images = [
        os.path.join(app.config['IMAGE_FOLDER'], 'image1.jpg'),
        os.path.join(app.config['IMAGE_FOLDER'], 'image2.jpg')
    ]

    # Pass mock or generated data to the template
    return render_template(
        'itinerary_details.html',
        itinerary=selected_itineraries,
        weather=MOCK_WEATHER_INFO,  # Replace with dynamic weather_info once integrated
        packing_list=packing_list,
        images=generated_images  # Pass generated images here
    )

# TODO: Define the generate_image function
# Use this function to integrate an AI image generation API (e.g., DALL-E, Stable Diffusion, etc.).
# Input: Key points of interest or landmarks from the itinerary.
# Output: Save generated images in app.config['IMAGE_FOLDER'] and return their file paths.
def generate_image(prompt, num_images=5):
    """
    Generate images using an AI image generation API.
    :param prompt: Text prompt for the image generation API.
    :param num_images: Number of images to generate.
    :return: List of file paths to the generated images.
    """
    # Example code structure:
    # 1. Call the image generation API with the prompt.
    # 2. Save the returned images to app.config['IMAGE_FOLDER'].
    # 3. Return the list of file path.

def generate_video(image_path, output_filename):
    """
    Generate a drone-like hovering video from an input image using the Replicate API.
    :image_path: The file path to the image to convert to a video 
    :output_filename: The name of the temporary output video
    """
    if DEMO_MODE:
        print("using file in DEMO_MODE")
        return

    image = open(image_path, "rb")
    output = replicate.run(
        "ali-vilab/i2vgen-xl:5821a338d00033abaaba89080a17eb8783d9a17ed710a6b4246a18e0900ccad4",
        input = {
            "image": image,
            "prompt": "Drone-like hovering movement of the given scene",
            "max_frames": 8,
        }
    )

    with open(f"temp/video/{output_filename}.mp4", "wb") as file:
        file.write(output.read())
    print("Video saved")


if __name__ == '__main__':
    # Ensure required directories exist
    os.makedirs(app.config['IMAGE_FOLDER'], exist_ok=True)
    os.makedirs(app.config['VIDEO_FOLDER'], exist_ok=True)
    load_dotenv()
    app.run(debug=True)
