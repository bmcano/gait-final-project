import requests
from datetime import datetime
import time
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
    import requests
    from datetime import datetime
    import time

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
    processed_data = []
    for day_data in weather_data:
        # Extract relevant data for each day
        date = datetime.utcfromtimestamp(day_data["dt"]).strftime('%Y-%m-%d')
        temperature = day_data["main"]["temp"]
        condition = day_data["weather"][0]["description"]
        processed_data.append({"date": date, "temperature": temperature, "condition": condition})
    return processed_data

city = "paris"
latitude, longitude = get_lat_lon(city)
if latitude and longitude:
    print(f"Latitude: {latitude}, Longitude: {longitude}")