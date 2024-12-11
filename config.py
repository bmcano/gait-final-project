# Project Settings

# To save money on API calls when we test the program itself use this for hard-coded responses.
# Otherwise when testing AI calls set this to false. 
DEMO_MODE = True 

# Mock Data - These values will be used when DEMO_MODE is set to True.
MOCK_WEATHER_INFO = {
    "temperature": "25°C",
    "condition": "Sunny with clear skies"
}

MOCK_ITINERARIES = [
    {"title": "Attraction 1", "description": "A detailed description of attraction 1", "image": "static/mock_images/image1.png"},
    {"title": "Attraction 2", "description": "A detailed description of attraction 2", "image": "static/mock_images/image2.png"},
    {"title": "Attraction 3", "description": "A detailed description of attraction 3", "image": "static/mock_images/image3.png"},
    {"title": "Attraction 4", "description": "A detailed description of attraction 4", "image": "static/mock_images/image4.png"},
    {"title": "Attraction 5", "description": "A detailed description of attraction 5", "image": "static/mock_images/image5.png"},
]

MOCK_IMAGES = [
    "static/mock_images/image1.png",
    "static/mock_images/image2.png",
    "static/mock_images/image3.png",
    "static/mock_images/image4.png",
    "static/mock_images/image5.png"
]

MOCK_VIDEO = "static/mock_videos/final.mp4"
