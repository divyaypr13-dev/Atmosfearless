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

# City-specific realistic data (used as fallback)
CITY_DATA = {
    'delhi': {'temp': 38, 'humidity': 45, 'rain': 0, 'wind': 12, 'cloud': 20},
    'mumbai': {'temp': 30, 'humidity': 65, 'rain': 2.5, 'wind': 8, 'cloud': 40},
    'bangalore': {'temp': 26, 'humidity': 55, 'rain': 0.8, 'wind': 10, 'cloud': 30},
    'chennai': {'temp': 32, 'humidity': 50, 'rain': 0.5, 'wind': 9, 'cloud': 25},
    'kolkata': {'temp': 33, 'humidity': 60, 'rain': 1.2, 'wind': 6, 'cloud': 35},
    'hyderabad': {'temp': 34, 'humidity': 48, 'rain': 0.3, 'wind': 11, 'cloud': 22},
    'pune': {'temp': 28, 'humidity': 52, 'rain': 0.9, 'wind': 7, 'cloud': 28},
    'ahmedabad': {'temp': 36, 'humidity': 42, 'rain': 0.1, 'wind': 14, 'cloud': 15},
    'jaipur': {'temp': 37, 'humidity': 40, 'rain': 0.2, 'wind': 13, 'cloud': 18},
    'lucknow': {'temp': 35, 'humidity': 50, 'rain': 0.6, 'wind': 10, 'cloud': 25},
    'bhopal': {'temp': 33, 'humidity': 55, 'rain': 0.7, 'wind': 8, 'cloud': 30},
    'patna': {'temp': 34, 'humidity': 58, 'rain': 0.5, 'wind': 7, 'cloud': 28}
}

def get_live_weather(lat, lon):
    """
    Try Open-Meteo first. If it fails, use city-specific fallback.
    """
    # Find which city this lat/lon belongs to
    city_name = "delhi"
    for name, coords in INDIAN_CITIES.items():
        if abs(coords['lat'] - lat) < 1 and abs(coords['lon'] - lon) < 1:
            city_name = name
            break
    
    # Try Open-Meteo
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
        
        humidity = CITY_DATA[city_name]['humidity']
        if 'relative_humidity_2m' in hourly and len(hourly['relative_humidity_2m']) > 0:
            humidity = hourly['relative_humidity_2m'][0]
        
        cloud_cover = CITY_DATA[city_name]['cloud']
        if 'cloud_cover' in hourly and len(hourly['cloud_cover']) > 0:
            cloud_cover = hourly['cloud_cover'][0]
        
        return {
            'temperature': current.get('temperature', CITY_DATA[city_name]['temp']),
            'rainfall': current.get('precipitation', CITY_DATA[city_name]['rain']),
            'humidity': humidity,
            'wind_speed': current.get('windspeed', CITY_DATA[city_name]['wind']),
            'cloud_cover': cloud_cover,
            'pressure': 1013,
            'timestamp': current.get('time', datetime.now().isoformat()),
            'source': 'Open-Meteo',
            'city': city_name
        }
    except Exception as e:
        print(f"⚠️ Weather API error: {e} - Using city-specific fallback")
        # --- CITY-SPECIFIC FALLBACK ---
        city = CITY_DATA[city_name]
        # Add small random variation
        temp_variation = random.randint(-3, 3)
        rain_variation = random.choice([0, 0, 0, 0.2, 0.5, 0.8, 1.0])
        
        return {
            'temperature': city['temp'] + temp_variation,
            'rainfall': city['rain'] + rain_variation,
            'humidity': city['humidity'] + random.randint(-5, 5),
            'wind_speed': city['wind'] + random.randint(-3, 3),
            'cloud_cover': city['cloud'] + random.randint(-10, 10),
            'pressure': 1013,
            'timestamp': datetime.now().isoformat(),
            'source': 'City-Specific Fallback',
            'city': city_name
        }