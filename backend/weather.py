import requests
from datetime import datetime
import random

INDIAN_CITIES = {
    'delhi': {'lat': 28.61, 'lon': 77.23},
    'mumbai': {'lat': 19.08, 'lon': 72.88},
    'bangalore': {'lat': 12.97, 'lon': 77.59},
    'chennai': {'lat': 13.08, 'lon': 80.27},
    'kolkata': {'lat': 22.57, 'lon': 88.36},
    'hyderabad': {'lat': 17.38, 'lon': 78.48},
    'pune': {'lat': 18.52, 'lon': 73.85},
    'ahmedabad': {'lat': 23.02, 'lon': 72.57},
    'jaipur': {'lat': 26.91, 'lon': 75.79},
    'lucknow': {'lat': 26.85, 'lon': 80.95},
    'bhopal': {'lat': 23.26, 'lon': 77.41},
    'patna': {'lat': 25.59, 'lon': 85.14}
}

# Realistic base temperatures for different cities
CITY_BASE_TEMP = {
    'delhi': 38, 'mumbai': 30, 'bangalore': 26, 'chennai': 32,
    'kolkata': 33, 'hyderabad': 34, 'pune': 28, 'ahmedabad': 36,
    'jaipur': 37, 'lucknow': 35, 'bhopal': 33, 'patna': 34
}

def get_live_weather(lat, lon):
    """
    Fetch real-time weather data from Open-Meteo API.
    If it fails, returns city-specific realistic mock data.
    """
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": True,
            "hourly": "temperature_2m,precipitation,relative_humidity_2m,wind_speed_10m,cloud_cover",
            "timezone": "Asia/Kolkata"
        }
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        current = data.get('current_weather', {})
        hourly = data.get('hourly', {})
        
        humidity = 45
        if 'relative_humidity_2m' in hourly and len(hourly['relative_humidity_2m']) > 0:
            humidity = hourly['relative_humidity_2m'][0]
        
        cloud_cover = 20
        if 'cloud_cover' in hourly and len(hourly['cloud_cover']) > 0:
            cloud_cover = hourly['cloud_cover'][0]
        
        return {
            'temperature': current.get('temperature', 30),
            'rainfall': current.get('precipitation', 0),
            'humidity': humidity,
            'wind_speed': current.get('windspeed', 10),
            'cloud_cover': cloud_cover,
            'pressure': 1013,
            'timestamp': current.get('time', datetime.now().isoformat()),
            'source': 'Open-Meteo'
        }
    except Exception as e:
        print(f"⚠️ Weather API error: {e} - Using fallback data")
        # --- FALLBACK: City-specific realistic data ---
        city_name = "delhi"
        for name, coords in INDIAN_CITIES.items():
            if abs(coords['lat'] - lat) < 1 and abs(coords['lon'] - lon) < 1:
                city_name = name
                break
        
        # Use city-specific base temperature
        base_temp = CITY_BASE_TEMP.get(city_name, 32)
        temp = base_temp + random.randint(-3, 3)
        
        return {
            'temperature': temp,
            'rainfall': random.choice([0, 0, 0, 0.5, 1.2, 0]),
            'humidity': random.randint(35, 75),
            'wind_speed': random.randint(5, 18),
            'cloud_cover': random.randint(10, 60),
            'pressure': 1013,
            'timestamp': datetime.now().isoformat(),
            'source': 'Fallback Data'
        }