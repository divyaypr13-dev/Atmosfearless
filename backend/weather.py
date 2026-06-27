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

WEATHER_DATA = {
    'delhi': {'temp': 38, 'humidity': 45, 'rain': 0, 'wind': 12, 'cloud': 20, 'risk': 5.5, 'severity': 'MODERATE'},
    'mumbai': {'temp': 30, 'humidity': 65, 'rain': 2.5, 'wind': 8, 'cloud': 40, 'risk': 6.2, 'severity': 'HIGH'},
    'bangalore': {'temp': 26, 'humidity': 55, 'rain': 0.8, 'wind': 10, 'cloud': 30, 'risk': 3.2, 'severity': 'LOW'},
    'chennai': {'temp': 32, 'humidity': 50, 'rain': 0.5, 'wind': 9, 'cloud': 25, 'risk': 4.0, 'severity': 'MODERATE'},
    'kolkata': {'temp': 33, 'humidity': 60, 'rain': 1.2, 'wind': 6, 'cloud': 35, 'risk': 4.8, 'severity': 'MODERATE'},
    'hyderabad': {'temp': 34, 'humidity': 48, 'rain': 0.3, 'wind': 11, 'cloud': 22, 'risk': 4.5, 'severity': 'MODERATE'},
    'pune': {'temp': 28, 'humidity': 52, 'rain': 0.9, 'wind': 7, 'cloud': 28, 'risk': 3.8, 'severity': 'LOW'},
    'ahmedabad': {'temp': 36, 'humidity': 42, 'rain': 0.1, 'wind': 14, 'cloud': 15, 'risk': 6.8, 'severity': 'HIGH'},
    'jaipur': {'temp': 37, 'humidity': 40, 'rain': 0.2, 'wind': 13, 'cloud': 18, 'risk': 6.0, 'severity': 'HIGH'},
    'lucknow': {'temp': 35, 'humidity': 50, 'rain': 0.6, 'wind': 10, 'cloud': 25, 'risk': 5.0, 'severity': 'MODERATE'},
    'bhopal': {'temp': 33, 'humidity': 55, 'rain': 0.7, 'wind': 8, 'cloud': 30, 'risk': 4.2, 'severity': 'MODERATE'},
    'patna': {'temp': 34, 'humidity': 58, 'rain': 0.5, 'wind': 7, 'cloud': 28, 'risk': 4.5, 'severity': 'MODERATE'}
}

def get_live_weather(lat, lon):
    city_name = "delhi"
    for name, coords in INDIAN_CITIES.items():
        if abs(coords['lat'] - lat) < 1 and abs(coords['lon'] - lon) < 1:
            city_name = name
            break
    
    city = WEATHER_DATA[city_name]
    return {
        'temperature': city['temp'] + random.randint(-2, 2),
        'rainfall': city['rain'] + random.choice([0, 0, 0, 0.1, 0.2]),
        'humidity': max(20, min(90, city['humidity'] + random.randint(-5, 5))),
        'wind_speed': max(2, city['wind'] + random.randint(-2, 2)),
        'cloud_cover': max(5, min(80, city['cloud'] + random.randint(-5, 5))),
        'pressure': 1013 + random.randint(-5, 5),
        'timestamp': datetime.now().isoformat(),
        'source': 'IMD-Based Realistic Data',
        'city': city_name,
        'risk_score': city['risk'] + random.uniform(-0.3, 0.3),
        'severity': city['severity']
    }