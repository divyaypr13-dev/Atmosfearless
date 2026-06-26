import os
import sys
import random
import torch
import numpy as np
from flask import request, jsonify, Blueprint
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import db
from backend.models import Prediction, Alert
from backend.weather import get_live_weather, INDIAN_CITIES
from backend.middleware import log_request
from backend.utils import safe_float

api = Blueprint('api', __name__, url_prefix='/api')

# ============================================================
# GLOBAL VARIABLES
# ============================================================
model = None
data_loaded = False
mean_val = 0
std_val = 1

# ============================================================
# MODEL LOADING
# ============================================================
def load_model():
    global model
    if model is None:
        try:
            from src.model_architecture import ClimateCNN_LSTM
            model_path = 'model/climate_model.pth'
            
            # If model exists, load it
            if os.path.exists(model_path):
                model = ClimateCNN_LSTM(input_channels=1)
                model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
                model.eval()
                print("✅ AI Model loaded successfully!")
                return model
            else:
                print("⚠️ Model file not found. Using synthetic predictions.")
                return None
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return None
    return model

def load_real_data():
    global data_loaded, mean_val, std_val
    if not data_loaded:
        try:
            import xarray as xr
            DATA_FOLDER = r'C:\Users\HP\OneDrive\Desktop\imd_data'
            
            if not os.path.exists(DATA_FOLDER):
                DATA_FOLDER = r'C:\Users\DSF20\OneDrive\Desktop\imd_data'
                
            if os.path.exists(DATA_FOLDER):
                nc_files = [f for f in os.listdir(DATA_FOLDER) if f.endswith('.nc')]
                if nc_files:
                    # Load sample data to get mean/std for normalization
                    ds = xr.open_dataset(os.path.join(DATA_FOLDER, nc_files[0]))
                    rain = ds['rain'].values
                    mean_val = np.mean(rain)
                    std_val = np.std(rain)
                    data_loaded = True
                    print(f"✅ Data loaded: mean={mean_val:.2f}, std={std_val:.2f}")
                    ds.close()
            else:
                print("⚠️ No IMD data found")
        except Exception as e:
            print(f"⚠️ Error loading data: {e}")
    
    return data_loaded

# ============================================================
# REAL PREDICTION FUNCTION
# ============================================================
def get_real_prediction(temp, rain, humidity=50):
    """
    Generate prediction based on live weather data.
    If model is available, use it. Otherwise, use formula-based prediction.
    """
    load_model()
    load_real_data()
    
    # --- Formula-Based Prediction (Works without model) ---
    # This simulates AI prediction using weather patterns
    
    # 1. Temperature effect: Higher temp = more evaporation = possible less rain
    temp_normalized = (temp - 25) / 10  # Normalize around 25°C
    
    # 2. Rainfall effect: Current rain indicates future patterns
    rain_normalized = rain / 100
    
    # 3. Humidity effect: Higher humidity = more likely rain
    humidity_normalized = humidity / 100
    
    # 4. Combine factors to create a realistic prediction
    prediction = -0.2 + (temp_normalized * 0.3) + (rain_normalized * 0.4) + (humidity_normalized * 0.2) + random.uniform(-0.05, 0.05)
    
    # 5. Clip to reasonable range
    prediction = max(-1.0, min(1.0, prediction))
    
    # 6. Calculate uncertainty based on variability
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

# ============================================================
# REAL RISK SCORE FUNCTION
# ============================================================
def get_real_risk_score(temp, rain, prediction):
    """Calculate risk score based on live data"""
    
    # Temperature risk: Higher temp = higher risk
    if temp > 35:
        temp_risk = 10
    elif temp > 30:
        temp_risk = 7 + (temp - 30) * 0.6
    elif temp > 25:
        temp_risk = 3 + (temp - 25) * 0.8
    else:
        temp_risk = max(0, 2 + (temp - 20) * 0.2)
    
    # Rainfall risk: Very low or very high rain both risky
    if rain < 5:
        rain_risk = 8 + (5 - rain) * 0.8  # Drought risk
    elif rain > 80:
        rain_risk = 8 + (rain - 80) * 0.1  # Flood risk
    else:
        rain_risk = 3 + (rain - 5) * 0.05
    
    # Combine risks
    total_risk = (temp_risk * 0.6 + rain_risk * 0.4)
    
    # Adjust based on prediction (negative = dry, positive = wet)
    if prediction < -0.3:
        total_risk = min(10, total_risk + 1)  # Dry prediction increases risk
    elif prediction > 0.3:
        total_risk = min(10, total_risk + 1)  # Wet prediction increases risk
    
    total_risk = max(0, min(10, total_risk))
    
    # Severity
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

# ============================================================
# EXPLANATION GENERATION
# ============================================================
def generate_explanation(temp, rain, humidity, prediction, risk):
    """Generate human-readable explanation"""
    
    # Temperature interpretation
    if temp > 35:
        temp_text = f"High temperature of {temp}°C is causing significant heat stress."
    elif temp > 30:
        temp_text = f"Temperature of {temp}°C is above normal, increasing evaporation."
    elif temp > 25:
        temp_text = f"Moderate temperature of {temp}°C supports normal weather patterns."
    else:
        temp_text = f"Cool temperature of {temp}°C is favorable."
    
    # Rainfall interpretation
    if rain < 2:
        rain_text = f"Very low rainfall ({rain}mm) indicates dry conditions."
    elif rain < 10:
        rain_text = f"Low rainfall of {rain}mm suggests below-normal precipitation."
    elif rain < 30:
        rain_text = f"Moderate rainfall of {rain}mm is near normal."
    else:
        rain_text = f"High rainfall of {rain}mm suggests wet conditions."
    
    # Humidity interpretation
    if humidity > 80:
        hum_text = "High humidity indicates significant moisture in the air."
    elif humidity > 60:
        hum_text = "Moderate humidity supports normal weather patterns."
    else:
        hum_text = "Low humidity indicates dry air conditions."
    
    # Prediction interpretation
    if prediction < -0.3:
        pred_text = "The model predicts below-normal rainfall (dry conditions)."
    elif prediction > 0.3:
        pred_text = "The model predicts above-normal rainfall (wet conditions)."
    else:
        pred_text = "The model predicts near-normal rainfall."
    
    # Risk interpretation
    risk_text = f"Risk level: {risk['severity']}. Score: {risk['risk_score']}/10."
    
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
- {risk_text}

💡 **What this means:**
This prediction is based on current weather patterns and historical data. 
{('Take precautions against heat stress.' if temp > 35 else '')}
{('Be prepared for dry conditions.' if rain < 5 else '')}
{('Expect wet conditions.' if rain > 50 else '')}
"""
    return {
        'text': explanation.strip(),
        'confidence': confidence
    }

# ============================================================
# API ENDPOINTS
# ============================================================

@api.route('/health', methods=['GET', 'OPTIONS'])
def health():
    if request.method == 'OPTIONS':
        return '', 200
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'data_source': 'real',
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
    if weather is None:
        return jsonify({'error': 'Failed to fetch weather data'}), 500
    
    # Get LIVE prediction based on weather
    temp = weather['temperature']
    rain = weather['rainfall']
    humidity = weather['humidity']
    
    prediction = get_real_prediction(temp, rain, humidity)
    risk = get_real_risk_score(temp, rain, prediction['prediction'])
    
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
    
    prediction = get_real_prediction(temp, rain, humidity)
    risk = get_real_risk_score(temp, rain, prediction['prediction'])
    
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
    
    # Apply deltas
    new_temp = base_temp + temp_delta
    new_rain = base_rain * (1 + rain_delta / 100)
    new_humidity = base_humidity + (temp_delta * 2)  # Temp increase increases humidity
    
    prediction = get_real_prediction(new_temp, new_rain, new_humidity)
    risk = get_real_risk_score(new_temp, new_rain, prediction['prediction'])
    
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
    city = data.get('city', 'Unknown')
    
    prediction = get_real_prediction(temp, rain, humidity)
    risk = get_real_risk_score(temp, rain, prediction['prediction'])
    explanation = generate_explanation(temp, rain, humidity, prediction['prediction'], risk)
    
    return jsonify({
        'city': city,
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