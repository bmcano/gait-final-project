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
    {"title": "Adventure and Outdoors", "description": "Hiking, kayaking, and exploring the wilderness of the region.", "image": "/static/mock_images/adventure_outdoors.webp"},
    {"title": "Cultural Exploration", "description": "Visit famous landmarks, historical sites, and cultural experiences.", "image": "/static/mock_images/cultural_exploration.webp"}
]
