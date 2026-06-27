import requests
from datetime import datetime

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

def get_live_weather(lat, lon):
    """
    Fetch real-time weather data from Open-Meteo API.
    Returns weather data or None if fetch fails.
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
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        current = data.get('current_weather', {})
        hourly = data.get('hourly', {})
        
        # Extract humidity from hourly data
        humidity = 45  # default fallback
        if 'relative_humidity_2m' in hourly and len(hourly['relative_humidity_2m']) > 0:
            humidity = hourly['relative_humidity_2m'][0]
        
        # Extract cloud cover from hourly data
        cloud_cover = 20  # default fallback
        if 'cloud_cover' in hourly and len(hourly['cloud_cover']) > 0:
            cloud_cover = hourly['cloud_cover'][0]
        
        return {
            'temperature': current.get('temperature', 0),
            'rainfall': current.get('precipitation', 0),
            'humidity': humidity,
            'wind_speed': current.get('windspeed', 0),
            'cloud_cover': cloud_cover,
            'pressure': 1013,  # default pressure
            'timestamp': current.get('time', datetime.now().isoformat()),
            'source': 'Open-Meteo'
        }
    except Exception as e:
        print(f"⚠️ Weather API error: {e}")
        return None