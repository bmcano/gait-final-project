import ast
import hashlib
from io import BytesIO
from PIL import Image, PngImagePlugin
import openai
from flask import Flask, render_template, request
import os
from datetime import datetime
from config import DEMO_MODE, MOCK_ITINERARIES, MOCK_VIDEO, MOCK_WEATHER_INFO, MOCK_IMAGES, MOCK_PACKING_LIST
from merge_videos import merge_clips_no_transition
from dotenv import load_dotenv
import time
from runwayml import RunwayML
import base64
import requests

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
        packing_list = MOCK_PACKING_LIST
        weather_info = MOCK_WEATHER_INFO
        itineraries = MOCK_ITINERARIES
        generated_images = MOCK_IMAGES
    else:
        itineraries = []
        packing_list = []
        try:
            attraction_prompt = create_must_see_attractions_prompt(destination)
            mustSeeAttractions_List = generate_must_see_attractions_list(attraction_prompt)
            weather_prompt = create_weather_and_packing_list(destination, from_date, to_date)
            weather_and_packing_info = generate_weather_and_packing_list(weather_prompt)
            # Convert to Python object
            weather_and_packing_info = ast.literal_eval(f"[{weather_and_packing_info}]")
            print(weather_and_packing_info)
            mustSeeAttractions_List = [(mustSeeAttractions_List)][0]
            mustSeeAttractions_List = ast.literal_eval(f"[{mustSeeAttractions_List}]")
            print(mustSeeAttractions_List)

            imagePrompt_List = create_image_prompts(mustSeeAttractions_List, from_date, to_date)
            generated_images = list(generate_images_from_prompts(imagePrompt_List).values())
            print(generated_images)
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
    # TODO: Extract all selected items, and then prepare them for ChatGPT to make the itinerary with
    weather_info = ast.literal_eval(request.form.get('weather_info', '{}'))
    print("Weather Info:", weather_info)
    selected_index = request.form.get('selected_indices', '')
    selected_indices = [int(idx) for idx in selected_index.split(',') if idx.isdigit()]
    selected_itineraries = [MOCK_ITINERARIES[idx] for idx in selected_indices]

    # TODO: Use ChatGPT to dynamically generate packing suggestions based on destination, weather, and itinerary.
    packing_list = ast.literal_eval(request.form.get('packing_list', '[]'))
    print("Packing List:", packing_list)
    # Grab all selected images
    selected_images = request.form.get('selected_images', '').split(',')
    updated_paths = selected_images
    if DEMO_MODE:
        merged_video = [
            {"video": MOCK_VIDEO}
        ]
    else:
        # convert all selected items into videos
        index = 0
        generated_videos = []
        for i, image in enumerate(updated_paths):
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
        video=merged_video
    )

# ---------- PROMPT GENERATION + IMAGE GENERATION ------------------
def create_weather_and_packing_list(destination, description, from_date, to_date):
    """
    Generate an OpenAI prompt to create a list of must-see attractions for the given destination,
    and also provide expected weather conditions, average temperatures for those dates, and a recommended packing list.
    """

    prompt = f"""
    You are a travel expert. For travelers visiting {destination} from {from_date} to {to_date} wanting to have a trip with the following description: {description}, 
    do the following:

    1. Based on historical weather data for {destination} during this time of year, 
    provide an expected weather outlook. Describe the general weather conditions 
    (e.g., mostly sunny, occasional rain), and include approximate average high and low temperatures 
    in Celsius.

    2. Based on the expected weather, generate a comprehensive packing list that would be suitable 
    for someone visiting during this period. Include items that are both weather-appropriate and 
    generally useful for exploring the attractions.


    The expected format is:
    ('conditions', 'Sunny with clear skies'),('average_high', '25C'),('average_low', '15C'),('Item 1', 'Heavy Coat'),('Item 2', 'Boots'),('Item 3', 'Sunglasses'),('Item 4', 'Sunscreen'),('Item 5', 'Hat'),('Item 6', 'Reusable Water Bottle')

    Ensure that the output follows Python syntax strictly, with all strings enclosed in double quotes (`"`), and no special characters (e.g., single quotes, backslashes) causing invalid syntax. And no next-line character after each tuple. 
    """

    return prompt

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


# STEP 1 : create the prompt using user's 'destination'
def create_must_see_attractions_prompt(destination):
    """
    Generate an OpenAI prompt to create 5 must-see attractions for the given destination.

    :param destination: The destination for which must-see attractions are generated.
    :return: A string OpenAI prompt to generate the attractions.
    """
    prompt = f"""
    You are a travel expert. Generate a list of 5 must-see attractions for travelers visiting {destination}.
    Each attraction should have:
    1. The name of the attraction (place_name).
    2. A brief description (description) of why it's iconic or famous.
    3. A highlight of its most notable features (features).
    Format the output as follows:
    
    ('Place Name 1', 'Brief description of the attraction', 'Key features or highlights of the place'),
    ('Place Name 2', 'Brief description of the attraction', 'Key features or highlights of the place'),
        ...
    
    Ensure that the output follows Python syntax strictly, with all strings enclosed in double quotes (`"`), and no special characters (e.g., single quotes, backslashes) causing invalid syntax. And no next-line character after the last tuple. 
    """
    return prompt

# STEP 2 : OpenAI API call to generate 5 must attractions list 
# from 'create_must_see_attractions_prompt()' function 
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

# STEP 3 : Using output from generate_must_see_attractions_list() function (which 
# is list of 5 must see attractions), we create image prompts for each. 
def create_image_prompts(mustSeeAttractions, fromDate, toDate):
    """
    Generate image prompts for a list of must-see attractions during the given travel dates.

    :param mustSeeAttractions: List of tuples containing (place_name, description, features).
    :param fromDate: Start date of the trip (YYYY-MM-DD).
    :param toDate: End date of the trip (YYYY-MM-DD).
    :return: List of image prompts as strings.
    """
    prompts = []
    for attraction in mustSeeAttractions:
        attraction_name, description, features = attraction
        prompt = (f"An ultra-realistic photograph of {attraction_name}, taken during a trip from {fromDate} to {toDate}. "
                  f"The scene highlights {description}, surrounded by its natural or urban environment. "
                  f"The lighting is balanced and natural, showcasing intricate details of {features}. "
                  f"The perspective is carefully chosen to emphasize the grandeur and charm of the location, "
                  f"captured with a high-quality, true-to-life photographic style.")
        prompts.append(prompt)
    return prompts

# STEP 4: Takes the list of 5 image prompts for user's destination, and using OpenAI API
# call, 5 images are generated and saved in the static/temp/images directory
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

    # Dictionary to store file paths for each prompt
    file_paths = {}

    client = openai.OpenAI()

    # Process each prompt in the list
    for prompt in imagePrompt_List:
        try:
            # Call OpenAI API for image generation
            response = client.images.generate(
                model="dall-e-3",
                quality="standard",
                size="1024x1024",  # Specify the size
                prompt=prompt,
                n=1               # Generate one image per prompt
            )

            # Extract the image URL from the response
            image_url = response.data[0].url

            # Download the image
            image_response = requests.get(image_url)
            image_response.raise_for_status()

            # Generate a short and unique filename using a hash of the prompt
            hash_object = hashlib.md5(prompt.encode())
            file_name = f"{hash_object.hexdigest()}.png"
            # file_path = os.path.join(IMAGE_FOLDER, file_name)
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

# -------------------------------------------------------------------- 

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

#
# ---------- VIDEO GENERATION HELPER FUNCTIONS ---------- 
#
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string

def save_video(video_url, output_filename):
    response = requests.get(video_url, stream=True)
    if response.status_code == 200:
        # Open a file in binary write mode and save the video content
        with open(f"static/temp/video/{output_filename}.mp4", "wb") as video_file:
            for chunk in response.iter_content(chunk_size=8192):
                video_file.write(chunk)
        print("Video saved.")
    else:
        print(f"Failed to save video. Status code: {response.status_code}, Error: {response.text}")


if __name__ == '__main__':
    # Ensure required directories exist
    os.makedirs(app.config['IMAGE_FOLDER'], exist_ok=True)
    os.makedirs(app.config['VIDEO_FOLDER'], exist_ok=True)
    load_dotenv()
    app.run(debug=True)
