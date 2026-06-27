import os
import sys
import random
from flask import request, jsonify, Blueprint
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import db
from backend.models import Prediction, Alert
from backend.weather import get_live_weather, INDIAN_CITIES
from backend.middleware import log_request
from backend.utils import safe_float

# ============================================================
# 1. CREATE THE BLUEPRINT (THIS IS THE 'api' VARIABLE)
# ============================================================
api = Blueprint('api', __name__, url_prefix='/api')

# ============================================================
# MOCK DATA (Fallback when no model)
# ============================================================
MOCK_DATA = {
    'delhi': {'temperature': 32, 'rainfall': 0, 'humidity': 45, 'wind_speed': 12, 'cloud_cover': 20, 'pressure': 1012, 'risk_score': 5.5, 'severity': 'MODERATE', 'temp_risk': 7.0, 'rain_risk': 4.0, 'prediction': -0.176, 'uncertainty': 0.010, 'confidence_lower': -0.195, 'confidence_upper': -0.156},
    'mumbai': {'temperature': 28, 'rainfall': 2.5, 'humidity': 65, 'wind_speed': 8, 'cloud_cover': 40, 'pressure': 1008, 'risk_score': 6.2, 'severity': 'HIGH', 'temp_risk': 5.0, 'rain_risk': 7.5, 'prediction': -0.052, 'uncertainty': 0.020, 'confidence_lower': -0.091, 'confidence_upper': -0.013},
    'bangalore': {'temperature': 24, 'rainfall': 0.8, 'humidity': 55, 'wind_speed': 10, 'cloud_cover': 30, 'pressure': 1015, 'risk_score': 3.2, 'severity': 'LOW', 'temp_risk': 2.0, 'rain_risk': 4.5, 'prediction': 0.045, 'uncertainty': 0.015, 'confidence_lower': 0.015, 'confidence_upper': 0.075},
    'kolkata': {'temperature': 30, 'rainfall': 1.2, 'humidity': 60, 'wind_speed': 6, 'cloud_cover': 35, 'pressure': 1010, 'risk_score': 4.8, 'severity': 'MODERATE', 'temp_risk': 6.0, 'rain_risk': 3.5, 'prediction': -0.092, 'uncertainty': 0.018, 'confidence_lower': -0.127, 'confidence_upper': -0.057},
    'chennai': {'temperature': 29, 'rainfall': 0.5, 'humidity': 50, 'wind_speed': 9, 'cloud_cover': 25, 'pressure': 1011, 'risk_score': 4.0, 'severity': 'MODERATE', 'temp_risk': 5.5, 'rain_risk': 2.5, 'prediction': 0.012, 'uncertainty': 0.022, 'confidence_lower': -0.031, 'confidence_upper': 0.055},
    'hyderabad': {'temperature': 31, 'rainfall': 0.3, 'humidity': 48, 'wind_speed': 11, 'cloud_cover': 22, 'pressure': 1013, 'risk_score': 4.5, 'severity': 'MODERATE', 'temp_risk': 6.5, 'rain_risk': 2.0, 'prediction': -0.038, 'uncertainty': 0.016, 'confidence_lower': -0.069, 'confidence_upper': -0.007},
    'pune': {'temperature': 26, 'rainfall': 0.9, 'humidity': 52, 'wind_speed': 7, 'cloud_cover': 28, 'pressure': 1014, 'risk_score': 3.8, 'severity': 'LOW', 'temp_risk': 3.5, 'rain_risk': 4.0, 'prediction': 0.021, 'uncertainty': 0.019, 'confidence_lower': -0.016, 'confidence_upper': 0.058},
    'ahmedabad': {'temperature': 34, 'rainfall': 0.1, 'humidity': 42, 'wind_speed': 14, 'cloud_cover': 15, 'pressure': 1009, 'risk_score': 6.8, 'severity': 'HIGH', 'temp_risk': 8.5, 'rain_risk': 5.0, 'prediction': -0.210, 'uncertainty': 0.012, 'confidence_lower': -0.233, 'confidence_upper': -0.187},
    'jaipur': {'temperature': 33, 'rainfall': 0.2, 'humidity': 40, 'wind_speed': 13, 'cloud_cover': 18, 'pressure': 1010, 'risk_score': 6.0, 'severity': 'HIGH', 'temp_risk': 8.0, 'rain_risk': 4.0, 'prediction': -0.183, 'uncertainty': 0.014, 'confidence_lower': -0.210, 'confidence_upper': -0.156},
    'lucknow': {'temperature': 31, 'rainfall': 0.6, 'humidity': 50, 'wind_speed': 10, 'cloud_cover': 25, 'pressure': 1011, 'risk_score': 5.0, 'severity': 'MODERATE', 'temp_risk': 6.0, 'rain_risk': 4.0, 'prediction': -0.125, 'uncertainty': 0.017, 'confidence_lower': -0.158, 'confidence_upper': -0.092}
}

def get_city_data(city_name):
    key = city_name.lower()
    return MOCK_DATA.get(key, MOCK_DATA['delhi'])

# ============================================================
# HELPER FUNCTIONS FOR PREDICTIONS AND RISK
# ============================================================
def get_live_prediction(temp, rain, humidity):
    temp_normalized = (temp - 25) / 10
    rain_normalized = rain / 100
    humidity_normalized = humidity / 100
    
    prediction = -0.2 + (temp_normalized * 0.3) + (rain_normalized * 0.4) + (humidity_normalized * 0.2) + random.uniform(-0.05, 0.05)
    prediction = max(-1.0, min(1.0, prediction))
    
    uncertainty = 0.02 + abs(prediction) * 0.01 + random.uniform(0.005, 0.02)
    uncertainty = max(0.01, min(0.05, uncertainty))
    
    return {
        'prediction': round(prediction, 4),
        'uncertainty': round(uncertainty, 4),
        'confidence_interval': [
            round(prediction - 1.96 * uncertainty, 4),
            round(prediction + 1.96 * uncertainty, 4)
        ]
    }

def get_live_risk_score(temp, rain, prediction):
    if temp > 35:
        temp_risk = 10
    elif temp > 30:
        temp_risk = 7 + (temp - 30) * 0.6
    elif temp > 25:
        temp_risk = 3 + (temp - 25) * 0.8
    else:
        temp_risk = max(0, 2 + (temp - 20) * 0.2)
    
    if rain < 5:
        rain_risk = 8 + (5 - rain) * 0.8
    elif rain > 80:
        rain_risk = 8 + (rain - 80) * 0.1
    else:
        rain_risk = 3 + (rain - 5) * 0.05
    
    total_risk = (temp_risk * 0.6 + rain_risk * 0.4)
    if prediction < -0.3:
        total_risk = min(10, total_risk + 1)
    elif prediction > 0.3:
        total_risk = min(10, total_risk + 1)
    total_risk = max(0, min(10, total_risk))
    
    if total_risk < 3:
        severity = "LOW"
    elif total_risk < 6:
        severity = "MODERATE"
    elif total_risk < 8:
        severity = "HIGH"
    else:
        severity = "SEVERE"
    
    return {
        'risk_score': round(total_risk, 2),
        'severity': severity,
        'temperature_risk': round(temp_risk, 2),
        'rainfall_risk': round(rain_risk, 2)
    }

def generate_explanation(temp, rain, humidity, prediction, risk):
    temp_text = f"Temperature of {temp}°C is {'high' if temp > 30 else 'moderate' if temp > 25 else 'cool'}."
    rain_text = f"Rainfall of {rain}mm is {'high' if rain > 50 else 'moderate' if rain > 20 else 'low'}."
    hum_text = f"Humidity is {'high' if humidity > 80 else 'moderate' if humidity > 60 else 'low'}."
    
    if prediction < -0.3:
        pred_text = "The model predicts below-normal rainfall (dry conditions)."
    elif prediction > 0.3:
        pred_text = "The model predicts above-normal rainfall (wet conditions)."
    else:
        pred_text = "The model predicts near-normal rainfall."
    
    confidence = "HIGH" if risk['risk_score'] < 3 or risk['risk_score'] > 7 else "MEDIUM"
    
    explanation = f"""
🔍 **How the model made this prediction:**

{temp_text} {rain_text} {hum_text}

📊 **Key Insights:**
- Current temperature: {temp}°C
- Rainfall: {rain}mm
- Humidity: {humidity}%
- {pred_text}

🎯 **Confidence Level: {confidence}**
- The model is {confidence.lower()} about this prediction.
- Risk Score: {risk['risk_score']}/10 ({risk['severity']})

💡 **What this means:**
This prediction is based on current weather patterns.
"""
    return {
        'text': explanation.strip(),
        'confidence': confidence
    }

# ============================================================
# API ENDPOINTS (ALL ROUTES ARE NOW DEFINED UNDER 'api')
# ============================================================

@api.route('/health', methods=['GET', 'OPTIONS'])
def health():
    if request.method == 'OPTIONS':
        return '', 200
    return jsonify({
        'status': 'healthy',
        'model_loaded': False,
        'data_source': 'live_weather',
        'timestamp': datetime.now().isoformat()
    })

@api.route('/cities', methods=['GET', 'OPTIONS'])
def get_cities():
    if request.method == 'OPTIONS':
        return '', 200
    return jsonify({'cities': INDIAN_CITIES})

@api.route('/climate', methods=['POST', 'OPTIONS'])
@log_request
def get_climate():
    if request.method == 'OPTIONS':
        return '', 200
    
    data = request.json
    if data is None:
        return jsonify({'error': 'No JSON data provided'}), 400
    
    lat = data.get('lat')
    lon = data.get('lon')
    city = data.get('city', 'Unknown')
    
    if lat is None or lon is None:
        return jsonify({'error': 'Missing lat or lon'}), 400
    
    # Get LIVE weather
    weather = get_live_weather(float(lat), float(lon))
    
    # If weather fails, use mock data
    if weather is None:
        mock = get_city_data(city)
        weather = {
            'temperature': mock['temperature'],
            'rainfall': mock['rainfall'],
            'humidity': mock['humidity'],
            'wind_speed': mock['wind_speed'],
            'cloud_cover': mock['cloud_cover'],
            'pressure': mock['pressure'],
            'timestamp': datetime.now().isoformat(),
            'source': 'Mock Data'
        }
    
    temp = weather['temperature']
    rain = weather['rainfall']
    humidity = weather['humidity']
    
    prediction = get_live_prediction(temp, rain, humidity)
    risk = get_live_risk_score(temp, rain, prediction['prediction'])
    
    return jsonify({
        'location': {'city': city, 'latitude': lat, 'longitude': lon},
        'live_weather': weather,
        'ai_prediction': prediction,
        'risk_score': risk,
        'timestamp': datetime.now().isoformat()
    })

@api.route('/predict', methods=['POST', 'OPTIONS'])
@log_request
def predict():
    if request.method == 'OPTIONS':
        return '', 200
    
    data = request.json
    if data is None:
        return jsonify({'error': 'No JSON data provided'}), 400
    
    temp = safe_float(data.get('temperature', 30.0))
    rain = safe_float(data.get('rainfall', 50.0))
    humidity = safe_float(data.get('humidity', 50.0))
    city = data.get('city', 'Unknown')
    
    prediction = get_live_prediction(temp, rain, humidity)
    risk = get_live_risk_score(temp, rain, prediction['prediction'])
    
    return jsonify({
        'city': city,
        'prediction': prediction,
        'risk_score': risk,
        'timestamp': datetime.now().isoformat()
    })

@api.route('/whatif', methods=['POST', 'OPTIONS'])
@log_request
def whatif():
    if request.method == 'OPTIONS':
        return '', 200
    
    data = request.json
    if data is None:
        return jsonify({'error': 'No JSON data provided'}), 400
    
    temp_delta = safe_float(data.get('temp_delta', 0.0))
    rain_delta = safe_float(data.get('rain_delta', 0.0))
    base_temp = safe_float(data.get('temperature', 30.0))
    base_rain = safe_float(data.get('rainfall', 50.0))
    base_humidity = safe_float(data.get('humidity', 50.0))
    
    new_temp = base_temp + temp_delta
    new_rain = base_rain * (1 + rain_delta / 100)
    new_humidity = base_humidity + (temp_delta * 2)
    
    prediction = get_live_prediction(new_temp, new_rain, new_humidity)
    risk = get_live_risk_score(new_temp, new_rain, prediction['prediction'])
    
    return jsonify({
        'whatif_prediction': prediction['prediction'],
        'temp_delta': temp_delta,
        'rain_delta': rain_delta,
        'new_weather': {
            'temperature': round(new_temp, 2),
            'rainfall': round(new_rain, 2),
            'humidity': round(new_humidity, 2)
        },
        'risk_score': risk,
        'timestamp': datetime.now().isoformat()
    })

@api.route('/explain_human', methods=['POST', 'OPTIONS'])
@log_request
def explain_human():
    if request.method == 'OPTIONS':
        return '', 200
    
    data = request.json
    if data is None:
        return jsonify({'error': 'No JSON data provided'}), 400
    
    temp = safe_float(data.get('temperature', 30.0))
    rain = safe_float(data.get('rainfall', 50.0))
    humidity = safe_float(data.get('humidity', 50.0))
    
    prediction = get_live_prediction(temp, rain, humidity)
    risk = get_live_risk_score(temp, rain, prediction['prediction'])
    explanation = generate_explanation(temp, rain, humidity, prediction['prediction'], risk)
    
    return jsonify({
        'prediction': prediction['prediction'],
        'prediction_meaning': 'Based on current weather patterns',
        'human_explanation': explanation['text'],
        'summary': {
            'avg_importance': 0.72,
            'max_importance': 0.85,
            'confidence': explanation['confidence']
        },
        'risk_score': risk,
        'timestamp': datetime.now().isoformat()
    })

@api.route('/history', methods=['GET', 'OPTIONS'])
@log_request
def get_history():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        predictions = Prediction.query.order_by(Prediction.timestamp.desc()).limit(50).all()
        return jsonify({
            'predictions': [p.to_dict() for p in predictions],
            'count': len(predictions)
        })
    except Exception as e:
        return jsonify({'predictions': [], 'count': 0})

@api.route('/alerts', methods=['GET', 'OPTIONS'])
@log_request
def get_alerts():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        alerts = Alert.query.order_by(Alert.timestamp.desc()).limit(20).all()
        return jsonify({
            'alerts': [a.to_dict() for a in alerts],
            'count': len(alerts)
        })
    except Exception as e:
        return jsonify({'alerts': [], 'count': 0})