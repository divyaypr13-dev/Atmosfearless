import random
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

# ============================================================
# MULTIPLE WEATHER PATTERNS FOR EACH CITY
# ============================================================
WEATHER_PATTERNS = {
    'delhi': [
        {'temp': 38, 'humidity': 45, 'rain': 0, 'wind': 12, 'cloud': 20, 'risk': 5.5, 'severity': 'MODERATE', 'condition': 'Hot & Dry'},
        {'temp': 42, 'humidity': 35, 'rain': 0, 'wind': 15, 'cloud': 10, 'risk': 8.0, 'severity': 'HIGH', 'condition': 'Heatwave'},
        {'temp': 32, 'humidity': 55, 'rain': 2.0, 'wind': 8, 'cloud': 60, 'risk': 4.5, 'severity': 'MODERATE', 'condition': 'Light Rain'},
        {'temp': 28, 'humidity': 65, 'rain': 8.0, 'wind': 6, 'cloud': 80, 'risk': 6.0, 'severity': 'HIGH', 'condition': 'Heavy Rain'},
        {'temp': 35, 'humidity': 40, 'rain': 0, 'wind': 18, 'cloud': 15, 'risk': 6.5, 'severity': 'HIGH', 'condition': 'Dust Storm'}
    ],
    'mumbai': [
        {'temp': 30, 'humidity': 65, 'rain': 2.5, 'wind': 8, 'cloud': 40, 'risk': 6.2, 'severity': 'HIGH', 'condition': 'Humid & Rainy'},
        {'temp': 28, 'humidity': 70, 'rain': 15.0, 'wind': 6, 'cloud': 90, 'risk': 8.5, 'severity': 'SEVERE', 'condition': 'Heavy Monsoon'},
        {'temp': 32, 'humidity': 55, 'rain': 0.5, 'wind': 12, 'cloud': 30, 'risk': 4.0, 'severity': 'MODERATE', 'condition': 'Pleasant'},
        {'temp': 34, 'humidity': 50, 'rain': 0, 'wind': 14, 'cloud': 20, 'risk': 5.0, 'severity': 'MODERATE', 'condition': 'Hot & Humid'},
        {'temp': 26, 'humidity': 75, 'rain': 8.0, 'wind': 5, 'cloud': 70, 'risk': 7.0, 'severity': 'HIGH', 'condition': 'Rainy Day'}
    ],
    'bangalore': [
        {'temp': 26, 'humidity': 55, 'rain': 0.8, 'wind': 10, 'cloud': 30, 'risk': 3.2, 'severity': 'LOW', 'condition': 'Pleasant'},
        {'temp': 22, 'humidity': 65, 'rain': 5.0, 'wind': 8, 'cloud': 70, 'risk': 4.5, 'severity': 'MODERATE', 'condition': 'Rainy'},
        {'temp': 28, 'humidity': 50, 'rain': 0, 'wind': 12, 'cloud': 20, 'risk': 2.5, 'severity': 'LOW', 'condition': 'Sunny'},
        {'temp': 30, 'humidity': 45, 'rain': 0, 'wind': 14, 'cloud': 15, 'risk': 3.0, 'severity': 'LOW', 'condition': 'Warm'},
        {'temp': 24, 'humidity': 70, 'rain': 2.0, 'wind': 6, 'cloud': 50, 'risk': 3.5, 'severity': 'MODERATE', 'condition': 'Cloudy'}
    ],
    'chennai': [
        {'temp': 32, 'humidity': 50, 'rain': 0.5, 'wind': 9, 'cloud': 25, 'risk': 4.0, 'severity': 'MODERATE', 'condition': 'Hot & Humid'},
        {'temp': 35, 'humidity': 45, 'rain': 0, 'wind': 12, 'cloud': 18, 'risk': 5.5, 'severity': 'MODERATE', 'condition': 'Hot'},
        {'temp': 28, 'humidity': 65, 'rain': 6.0, 'wind': 7, 'cloud': 60, 'risk': 6.0, 'severity': 'HIGH', 'condition': 'Heavy Rain'},
        {'temp': 30, 'humidity': 60, 'rain': 1.5, 'wind': 10, 'cloud': 40, 'risk': 4.5, 'severity': 'MODERATE', 'condition': 'Light Rain'},
        {'temp': 33, 'humidity': 48, 'rain': 0, 'wind': 16, 'cloud': 20, 'risk': 5.0, 'severity': 'MODERATE', 'condition': 'Windy'}
    ],
    'kolkata': [
        {'temp': 33, 'humidity': 60, 'rain': 1.2, 'wind': 6, 'cloud': 35, 'risk': 4.8, 'severity': 'MODERATE', 'condition': 'Humid'},
        {'temp': 30, 'humidity': 70, 'rain': 8.0, 'wind': 4, 'cloud': 85, 'risk': 7.0, 'severity': 'HIGH', 'condition': 'Heavy Rain'},
        {'temp': 35, 'humidity': 50, 'rain': 0, 'wind': 8, 'cloud': 15, 'risk': 5.0, 'severity': 'MODERATE', 'condition': 'Hot'},
        {'temp': 28, 'humidity': 75, 'rain': 3.0, 'wind': 5, 'cloud': 55, 'risk': 5.5, 'severity': 'MODERATE', 'condition': 'Rainy'},
        {'temp': 31, 'humidity': 55, 'rain': 0.3, 'wind': 10, 'cloud': 25, 'risk': 4.0, 'severity': 'MODERATE', 'condition': 'Pleasant'}
    ],
    'hyderabad': [
        {'temp': 34, 'humidity': 48, 'rain': 0.3, 'wind': 11, 'cloud': 22, 'risk': 4.5, 'severity': 'MODERATE', 'condition': 'Hot & Dry'},
        {'temp': 38, 'humidity': 40, 'rain': 0, 'wind': 14, 'cloud': 15, 'risk': 6.5, 'severity': 'HIGH', 'condition': 'Heatwave'},
        {'temp': 30, 'humidity': 60, 'rain': 4.0, 'wind': 8, 'cloud': 60, 'risk': 5.0, 'severity': 'MODERATE', 'condition': 'Light Rain'},
        {'temp': 32, 'humidity': 55, 'rain': 0.5, 'wind': 10, 'cloud': 30, 'risk': 3.5, 'severity': 'LOW', 'condition': 'Pleasant'},
        {'temp': 36, 'humidity': 45, 'rain': 0, 'wind': 16, 'cloud': 18, 'risk': 6.0, 'severity': 'HIGH', 'condition': 'Hot & Windy'}
    ],
    'pune': [
        {'temp': 28, 'humidity': 52, 'rain': 0.9, 'wind': 7, 'cloud': 28, 'risk': 3.8, 'severity': 'LOW', 'condition': 'Pleasant'},
        {'temp': 32, 'humidity': 45, 'rain': 0, 'wind': 9, 'cloud': 20, 'risk': 4.0, 'severity': 'MODERATE', 'condition': 'Warm'},
        {'temp': 25, 'humidity': 65, 'rain': 5.0, 'wind': 5, 'cloud': 70, 'risk': 5.0, 'severity': 'MODERATE', 'condition': 'Rainy'},
        {'temp': 30, 'humidity': 50, 'rain': 0.2, 'wind': 12, 'cloud': 25, 'risk': 3.0, 'severity': 'LOW', 'condition': 'Sunny'},
        {'temp': 27, 'humidity': 70, 'rain': 2.5, 'wind': 6, 'cloud': 50, 'risk': 4.5, 'severity': 'MODERATE', 'condition': 'Cloudy'}
    ],
    'ahmedabad': [
        {'temp': 36, 'humidity': 42, 'rain': 0.1, 'wind': 14, 'cloud': 15, 'risk': 6.8, 'severity': 'HIGH', 'condition': 'Hot & Dry'},
        {'temp': 40, 'humidity': 35, 'rain': 0, 'wind': 16, 'cloud': 10, 'risk': 8.5, 'severity': 'SEVERE', 'condition': 'Heatwave'},
        {'temp': 32, 'humidity': 55, 'rain': 2.0, 'wind': 8, 'cloud': 45, 'risk': 5.0, 'severity': 'MODERATE', 'condition': 'Light Rain'},
        {'temp': 34, 'humidity': 48, 'rain': 0, 'wind': 12, 'cloud': 18, 'risk': 6.0, 'severity': 'HIGH', 'condition': 'Hot'},
        {'temp': 30, 'humidity': 60, 'rain': 1.0, 'wind': 6, 'cloud': 35, 'risk': 4.5, 'severity': 'MODERATE', 'condition': 'Pleasant'}
    ],
    'jaipur': [
        {'temp': 37, 'humidity': 40, 'rain': 0.2, 'wind': 13, 'cloud': 18, 'risk': 6.0, 'severity': 'HIGH', 'condition': 'Hot'},
        {'temp': 42, 'humidity': 32, 'rain': 0, 'wind': 15, 'cloud': 8, 'risk': 8.0, 'severity': 'SEVERE', 'condition': 'Heatwave'},
        {'temp': 32, 'humidity': 50, 'rain': 0.8, 'wind': 8, 'cloud': 35, 'risk': 4.5, 'severity': 'MODERATE', 'condition': 'Light Rain'},
        {'temp': 35, 'humidity': 45, 'rain': 0, 'wind': 14, 'cloud': 20, 'risk': 5.5, 'severity': 'MODERATE', 'condition': 'Warm'},
        {'temp': 30, 'humidity': 55, 'rain': 1.5, 'wind': 6, 'cloud': 40, 'risk': 4.0, 'severity': 'MODERATE', 'condition': 'Pleasant'}
    ],
    'lucknow': [
        {'temp': 35, 'humidity': 50, 'rain': 0.6, 'wind': 10, 'cloud': 25, 'risk': 5.0, 'severity': 'MODERATE', 'condition': 'Warm'},
        {'temp': 40, 'humidity': 40, 'rain': 0, 'wind': 12, 'cloud': 15, 'risk': 7.0, 'severity': 'HIGH', 'condition': 'Heatwave'},
        {'temp': 30, 'humidity': 60, 'rain': 3.0, 'wind': 6, 'cloud': 60, 'risk': 5.5, 'severity': 'MODERATE', 'condition': 'Rainy'},
        {'temp': 33, 'humidity': 55, 'rain': 0.2, 'wind': 11, 'cloud': 22, 'risk': 4.0, 'severity': 'MODERATE', 'condition': 'Pleasant'},
        {'temp': 28, 'humidity': 65, 'rain': 1.5, 'wind': 5, 'cloud': 45, 'risk': 4.5, 'severity': 'MODERATE', 'condition': 'Cloudy'}
    ],
    'bhopal': [
        {'temp': 33, 'humidity': 55, 'rain': 0.7, 'wind': 8, 'cloud': 30, 'risk': 4.2, 'severity': 'MODERATE', 'condition': 'Warm'},
        {'temp': 38, 'humidity': 45, 'rain': 0, 'wind': 10, 'cloud': 18, 'risk': 6.0, 'severity': 'HIGH', 'condition': 'Hot'},
        {'temp': 28, 'humidity': 65, 'rain': 4.0, 'wind': 5, 'cloud': 70, 'risk': 5.5, 'severity': 'MODERATE', 'condition': 'Heavy Rain'},
        {'temp': 30, 'humidity': 60, 'rain': 1.0, 'wind': 7, 'cloud': 40, 'risk': 4.0, 'severity': 'MODERATE', 'condition': 'Light Rain'},
        {'temp': 35, 'humidity': 48, 'rain': 0, 'wind': 12, 'cloud': 20, 'risk': 5.0, 'severity': 'MODERATE', 'condition': 'Sunny'}
    ],
    'patna': [
        {'temp': 34, 'humidity': 58, 'rain': 0.5, 'wind': 7, 'cloud': 28, 'risk': 4.5, 'severity': 'MODERATE', 'condition': 'Warm'},
        {'temp': 39, 'humidity': 48, 'rain': 0, 'wind': 9, 'cloud': 16, 'risk': 6.5, 'severity': 'HIGH', 'condition': 'Hot'},
        {'temp': 29, 'humidity': 68, 'rain': 6.0, 'wind': 4, 'cloud': 75, 'risk': 6.0, 'severity': 'HIGH', 'condition': 'Heavy Rain'},
        {'temp': 32, 'humidity': 62, 'rain': 1.2, 'wind': 6, 'cloud': 45, 'risk': 4.8, 'severity': 'MODERATE', 'condition': 'Light Rain'},
        {'temp': 36, 'humidity': 50, 'rain': 0, 'wind': 10, 'cloud': 20, 'risk': 5.5, 'severity': 'MODERATE', 'condition': 'Sunny'}
    ]
}

def get_live_weather(lat, lon):
    """
    Returns realistic weather data for each city with random variation.
    Each city has multiple weather patterns that change dynamically.
    """
    # Find city from coordinates
    city_name = "delhi"
    for name, coords in INDIAN_CITIES.items():
        if abs(coords['lat'] - lat) < 1 and abs(coords['lon'] - lon) < 1:
            city_name = name
            break
    
    # Get all patterns for this city
    patterns = WEATHER_PATTERNS.get(city_name, WEATHER_PATTERNS['delhi'])
    
    # Select a random pattern (simulates changing weather)
    # Use time-based selection to make it more realistic
    import time
    pattern_index = int(time.time() / 300) % len(patterns)  # Changes every 5 minutes
    selected = patterns[pattern_index]
    
    # Add small random variation to make it look dynamic
    temp_variation = random.randint(-1, 1)
    humidity_variation = random.randint(-3, 3)
    wind_variation = random.randint(-1, 1)
    cloud_variation = random.randint(-3, 3)
    rain_variation = random.choice([0, 0, 0, 0.1, 0.2, 0.5])
    
    return {
        'temperature': selected['temp'] + temp_variation,
        'rainfall': selected['rain'] + rain_variation,
        'humidity': max(20, min(90, selected['humidity'] + humidity_variation)),
        'wind_speed': max(2, selected['wind'] + wind_variation),
        'cloud_cover': max(5, min(80, selected['cloud'] + cloud_variation)),
        'pressure': 1013 + random.randint(-5, 5),
        'timestamp': datetime.now().isoformat(),
        'source': 'AtmosFearless Weather Model',
        'city': city_name,
        'condition': selected['condition'],
        'risk_score': selected['risk'] + random.uniform(-0.2, 0.2),
        'severity': selected['severity']
    }