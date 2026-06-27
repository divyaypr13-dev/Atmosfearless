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
    
    # Get city-specific LIVE weather
    weather = get_live_weather(float(lat), float(lon))
    
    # If weather is None, use fallback (already handled in weather.py)
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