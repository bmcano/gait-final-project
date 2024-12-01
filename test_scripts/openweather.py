import requests
from datetime import datetime
import time
from config import DEMO_MODE, MOCK_WEATHER_INFO
from secret import WEATHER_API_KEY
from geopy.geocoders import Nominatim

def get_lat_lon(address):
    geolocator = Nominatim(user_agent="geoapi")
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    else:
        print(f"Could not find location for {address}")
        return None

def get_weather_data(address, start_date, end_date):
    if DEMO_MODE:
        print("DEMO_MODE is ON. Returning mock weather data.")
        return {
            "temperature": MOCK_WEATHER_INFO["temperature"],
            "condition": MOCK_WEATHER_INFO["condition"]
        }

    # Live API call logic

    base_url = "https://history.openweathermap.org/data/2.5/history/city"
    results = []
    lat, lon = get_lat_lon(address)
    # Convert dates to UNIX timestamps
    start_timestamp = int(time.mktime(datetime.strptime(start_date, "%Y-%m-%d").timetuple()))
    end_timestamp = int(time.mktime(datetime.strptime(end_date, "%Y-%m-%d").timetuple()))

    for timestamp in range(start_timestamp, end_timestamp, 86400):  # 86400 seconds in a day
        params = {
            "lat": lat,
            "lon": lon,
            "type": "hour",
            "start": timestamp,
            "end": timestamp + 86400,
            "appid": WEATHER_API_KEY,  # API key from secret.py
            "units": "metric"
        }
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            results.append(response.json())
        else:
            print(f"Failed to retrieve data for timestamp {timestamp}: {response.text}")

    return results

def process_weather_data(weather_data):
    #TODO: Process the weather data to extract relevant information
    return None

city = "paris"
latitude, longitude = get_lat_lon(city)
if latitude and longitude:
    print(f"Latitude: {latitude}, Longitude: {longitude}")