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
    {"title": "Relax in the city", "description": "A slow-paced trip exploring the best cafes, museums, and parks.", "image": "/static/mock_images/relax_in_city.webp"},
    {
        "title": "Eiffel Tower", 
        "description": "The Eiffel Tower, standing proudly in the heart of Paris, is one of the world's most iconic landmarks. Designed by Gustave Eiffel and completed in 1889 for the World's Fair, this wrought-iron masterpiece towers 330 meters (1,083 feet) above the city, offering breathtaking panoramic views. Visitors can ascend its three levels by stairs or elevator, each revealing unique perspectives of Paris' historic skyline.", 
        "image": "/static/mock_images/eiffel_tower.webp"
    },
    {"title": "Adventure and Outdoors", "description": "Hiking, kayaking, and exploring the wilderness of the region.", "image": "/static/mock_images/adventure_outdoors.webp"},
    {"title": "Cultural Exploration", "description": "Visit famous landmarks, historical sites, and cultural experiences.", "image": "/static/mock_images/cultural_exploration.webp"}
]

MOCK_SELECTED_IMAGES = [
    {"image": "/static/mock_images/relax_in_city.webp"},
    {"image": "/static/mock_images/eiffel_tower.webp"}
]

MOCK_VIDEOS = [
    "static/mock_videos/video1.mp4",
    "static/mock_videos/video2.mp4"
]
