import ast
import hashlib
from io import BytesIO
import os
import openai
from dotenv import load_dotenv
import requests
from PIL import Image, PngImagePlugin


# Load environment variables from the .env file
load_dotenv()

# Retrieve the API key
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise Exception("OpenAI API key not found. Please set it in the .env file.")

def validate_api_key():
    """
    Validate the OpenAI API key by making a test call to a lightweight endpoint.
    """
    try:
        openai.Engine.list()  # A lightweight API call to validate the key
        print("API key is valid.")
    except openai.AuthenticationError:
        raise Exception("Invalid API key. Please check your .env file.")
    except Exception as e:
        raise Exception(f"Error validating API key: {e}")


# def generate_image(prompt, num_images=5):
    """
    Generate images using OpenAI's DALL-E model with the latest API.
    :param prompt: Text prompt for the image generation API.
    :param num_images: Number of images to generate.
    :return: List of file paths to the generated images.
    """
    # Validate the API key
    validate_api_key()

    # Configure the image storage folder
    IMAGE_FOLDER = "static/temp/images"
    if not os.path.exists(IMAGE_FOLDER):
        os.makedirs(IMAGE_FOLDER)

    file_paths = []

    for i in range(num_images):
        try:
            # Call OpenAI API for image generation
            response = openai.Image.create(
                prompt=prompt,
                n=1,  # Number of images per request
                size="1024x1024"  # Specify the size
            )

            # Extract the image URL from the response
            image_url = response["data"][0]["url"]

            # Download the image
            image_response = requests.get(image_url)
            image_response.raise_for_status()

            # Save the image to the specified folder
            from PIL import Image
            from io import BytesIO
            image = Image.open(BytesIO(image_response.content))
            file_name = f"{prompt.replace(' ', '_')}_{i + 1}.png"
            file_path = os.path.join(IMAGE_FOLDER, file_name)
            image.save(file_path)
            file_paths.append(file_path)

        except Exception as e:
            print(f"Error generating image {i + 1}: {e}")
            continue

    return file_paths


# ---------- PROMPT GENERATION + IMAGE GENERATION ------------------

# STEP 1 : create the prompt using 'destination'
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
# call, 5 images are generated and saved in the static/images directory
def generate_images_from_prompts(imagePrompt_List):
    """
    Generate images using OpenAI's DALL-E model based on a list of prompts.
    :param imagePrompt_List: List of text prompts for the image generation API.
    :return: Dictionary mapping prompts to their generated image file paths.
    """
    # Configure the image storage folder. Create directory if it doesn't exist
    IMAGE_FOLDER = "temp/images"
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
            file_path = os.path.join(IMAGE_FOLDER, file_name)

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

# ------------------------------------------------------------------


# Example usage
if __name__ == "__main__":

    destination = "Paris"
    fromDate = "2024-04-10"
    toDate = "2024-04-20"

    # Un-comment the following line to generate 5 images in your static/images folder

    try:
        mustSeeAttractions_List = generate_must_see_attractions_list(create_must_see_attractions_prompt(destination))

        # Convert to Python object
        mustSeeAttractions_List = [(mustSeeAttractions_List)][0]
        mustSeeAttractions_List = ast.literal_eval(f"[{mustSeeAttractions_List}]")
        # print(mustSeeAttractions_List)

        # List of 5 image prompts 
        imagePrompt_List = create_image_prompts(mustSeeAttractions_List, fromDate, toDate)
        # print(imagePrompt_List)

        generated_images = generate_images_from_prompts(imagePrompt_List)
        
    except Exception as e:
        print("Error:", e)

    # prompt = "A serene mountain landscape during sunrise with vibrant colors"
    # try:
    #     generated_images = generate_image(prompt, num_images=3)
    #     print("Generated images saved at:", generated_images)
    # except Exception as e:
    #     print("Error:", e)
