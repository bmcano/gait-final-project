import os
import openai
from dotenv import load_dotenv
import requests

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

def generate_image(prompt, num_images=5):
    """
    Generate images using OpenAI's DALL-E model with the latest API.
    :param prompt: Text prompt for the image generation API.
    :param num_images: Number of images to generate.
    :return: List of file paths to the generated images.
    """
    # Validate the API key
    validate_api_key()

    # Configure the image storage folder
    IMAGE_FOLDER = "static/images"
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

# Example usage
if __name__ == "__main__":
    prompt = "A serene mountain landscape during sunrise with vibrant colors"
    try:
        generated_images = generate_image(prompt, num_images=3)
        print("Generated images saved at:", generated_images)
    except Exception as e:
        print("Error:", e)
