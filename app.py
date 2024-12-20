import ast
import hashlib
from io import BytesIO
from PIL import Image, PngImagePlugin
import openai
from flask import Flask, render_template, request
import os
from datetime import datetime
from config import *
from prompts import *
from helper import *
from merge_videos import merge_clips_no_transition
from dotenv import load_dotenv
import time
from runwayml import RunwayML
import requests
import json

app = Flask(__name__)

# Configurations
# These folders contain the images generated by AI
app.config['IMAGE_FOLDER'] = 'static/temp/images'
app.config['VIDEO_FOLDER'] = 'static/temp/video'

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
    description = request.form['description']
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

    if DEMO_MODE:
        time.sleep(5) # To mock a load time
        packing_list = MOCK_PACKING_LIST
        weather_info = MOCK_WEATHER_INFO
        itineraries = MOCK_ITINERARIES
        generated_images = MOCK_IMAGES
    else:
        itineraries = []
        packing_list = []
        weather_info = {}
        try:
            # generate attractions from destination
            attraction_prompt = create_must_see_attractions_prompt(destination)
            mustSeeAttractions_List = generate_must_see_attractions_list(attraction_prompt)
            # generate weather and packing information from destination and date
            weather_prompt = create_weather_and_packing_list_prompt(destination, description, from_date, to_date)
            weather_and_packing_info = generate_weather_and_packing_list(weather_prompt)
            # Convert to Python object
            weather_and_packing_info = ast.literal_eval(f"[{weather_and_packing_info}]")
            mustSeeAttractions_List = [(mustSeeAttractions_List)][0]
            mustSeeAttractions_List = ast.literal_eval(f"[{mustSeeAttractions_List}]")
            # generate images based on date range and suggestions
            imagePrompt_List = create_image_prompts(mustSeeAttractions_List, from_date, to_date)
            generated_images = list(generate_images_from_prompts(imagePrompt_List).values())
            
            for i in range(len(mustSeeAttractions_List)):
                itineraries.append({ 
                    "title": mustSeeAttractions_List[i][0], 
                    "description": f"{mustSeeAttractions_List[i][1]} {mustSeeAttractions_List[i][2]}",
                    "image": generated_images[i]
                })
            
            for key, value in weather_and_packing_info:
                if key == 'conditions':
                    weather_info['condition'] = value
                elif key == 'average_high':
                    weather_info['average_high'] = value
                elif key == 'average_low':
                    weather_info['average_low'] = value
                elif key.startswith('Item'):
                    packing_list.append(value)
            
            print("weather_info")
            print(weather_info)
            print("parking_list")
            print(packing_list)
        except Exception as e:
            print("Error:", e)
    
    # Pass mock or generated data to the template
    return render_template(
        'itineraries.html',
        destination=destination,
        from_date=from_date,
        to_date=to_date,
        travel_dates=travel_dates,
        trip_duration=trip_duration,
        itineraries=itineraries,
        images=generated_images,
        weather_info=str(weather_info),
        packing_list=str(packing_list) 
    )

@app.route('/itinerary_details', methods=['POST'])
def itinerary_details():
    """
    Page showing detailed itinerary, weather, and packing suggestions.
    """

    selected_attractions = request.form.get('selected_attractions', '').split(',')
    selected_descriptions = request.form.get('selected_descriptions', '').split(',')

    selected_images = request.form.get('selected_images', '').split(',')
    weather_info = ast.literal_eval(request.form.get('weather_info', '{}'))
    packing_list = ast.literal_eval(request.form.get('packing_list', '[]'))
    selected_itineraries = []
    for i in range(len(selected_attractions)):
        selected_itineraries.append({
            "title": selected_attractions[i],
            "description": selected_descriptions[i]
        })

    travel_dates = f"{request.form.get('fromDate')} to {request.form.get('toDate')}"
    prompt = create_itinerary_pdf_prompt(selected_itineraries, weather_info, packing_list, travel_dates)
    itinerary_text_for_pdf = generate_detailed_itinerary(prompt)

    pdf_file_path = "static/temp/itinerary.pdf"
    save_itinerary_to_pdf(itinerary_text_for_pdf, pdf_file_path)
    
    if DEMO_MODE:
        time.sleep(5) # To mock a load time
        merged_video = [
            {"video": MOCK_VIDEO}
        ]
    else:
        # convert all selected items into videos
        index = 0
        generated_videos = []
        for i, image in enumerate(selected_images):
            index += 1 
            video = generate_runway_video(image, "png", f"video{i}")
            generated_videos.append(video)
        # merge all the videos together
        merged_video = [
            {"video": f"{merge_clips_no_transition(generated_videos)}" }
        ]

    # Pass mock or generated data to the template
    return render_template(
        'itinerary_details.html',
        itinerary=selected_itineraries,
        weather=weather_info,
        packing_list=packing_list,
        video=merged_video,
        pdf_path=pdf_file_path
    )

#
# ---------- API CALLS FOR AI GENERATION ------------------
#
def generate_must_see_attractions_list(prompt):
    '''
    Using the prompt created in create_must_see_attractions_prompt(), we generate a list of must see attractions of the given destination using OpenAI API

    :param prompt: prompt
    :return: A string OpenAI prompt to generate the attractions.
    '''
    
    client = openai.OpenAI()
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    mustSeeAttractionsList = completion.choices[0].message
    return mustSeeAttractionsList.content


def generate_weather_and_packing_list(prompt):
    """
    Generate a list of must-see attractions for the given destination using OpenAI API.

    :param prompt: The prompt to generate the list of attractions.
    :return: A list of must-see attractions for the destination.
    """

    client = openai.OpenAI()
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    response = completion.choices[0].message
    return response.content


def generate_images_from_prompts(imagePrompt_List):
    """
    Generate images using OpenAI's DALL-E model based on a list of prompts.
    :param imagePrompt_List: List of text prompts for the image generation API.
    :return: Dictionary mapping prompts to their generated image file paths.
    """

    # Configure the image storage folder. Create directory if it doesn't exist
    IMAGE_FOLDER = "static/temp/images"
    if not os.path.exists(IMAGE_FOLDER):
        os.makedirs(IMAGE_FOLDER)

    file_paths = {}
    client = openai.OpenAI()

    for prompt in imagePrompt_List:
        try:
            # Call OpenAI API for image generation
            response = client.images.generate(
                model="dall-e-3",
                quality="standard",
                size="1024x1024",   # Specify the size
                prompt=prompt,
                n=1                 # Generate one image per prompt
            )

            # Extract the image URL from the response and download the image
            image_url = response.data[0].url
            image_response = requests.get(image_url)
            image_response.raise_for_status()

            # Generate a short and unique filename using a hash of the prompt
            hash_object = hashlib.md5(prompt.encode())
            file_name = f"{hash_object.hexdigest()}.png"
            file_path = f"{IMAGE_FOLDER}/{file_name}"

            # Save the image to the specified folder
            image = Image.open(BytesIO(image_response.content))
            
            # --- COMMENT OUT METADATA FEATURE IF ERRORS ENCOUNTERED ---
            # Add metadata to the image
            metadata = PngImagePlugin.PngInfo()
            metadata.add_text("Prompt", prompt)  # Add the prompt as metadata
            image.save(file_path, "PNG", pnginfo=metadata)
            
            # Map the prompt to the file path
            file_paths[prompt] = file_path            

        except Exception as e:
            print(f"Error generating image for prompt '{prompt}': {e}")
            continue

    return file_paths


def generate_detailed_itinerary(prompt):
    client = openai.OpenAI()
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a travel planning assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    detailed_itinerary = completion.choices[0].message
    return detailed_itinerary.content

def generate_runway_video(image_path, image_tpye, output_filename):
    """
    Generate a drone-like hovering video from an input image using the Replicate API.
    :image_path: The file path to the image to convert to a video 
    :output_filename: The name of the temporary output video
    """
 
    if DEMO_MODE:
        print("using program in DEMO_MODE - no video generation")
        return "static/mock_videos/video2.mp4"
    
    print("start video generation - for debug purpose")
    client = RunwayML()
    base64_image = encode_image_to_base64(image_path)
    task = client.image_to_video.create(
        model='gen3a_turbo',
        prompt_image=f"data:image/{image_tpye};base64,{base64_image}",
        prompt_text='Drone-like hovering movement of the given scene',
        duration=5
    )
    task_id = task.id

    # Poll the task until it's complete
    time.sleep(10)
    task = client.tasks.retrieve(task_id)
    while task.status not in ['SUCCEEDED', 'FAILED']:
        time.sleep(10)
        task = client.tasks.retrieve(task_id)

    print('Task complete:', task)
    save_video(task.output[0], output_filename)
    return f"static/temp/video/{output_filename}.mp4"


if __name__ == '__main__':
    # Ensure required directories exist
    os.makedirs(app.config['IMAGE_FOLDER'], exist_ok=True)
    os.makedirs(app.config['VIDEO_FOLDER'], exist_ok=True)

    # Remove old temp files on project startup 
    directory_paths = ["static/temp/video", "static/temp/images"]
    for directory_path in directory_paths:
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            os.remove(file_path)

    load_dotenv()
    app.run(debug=True)
