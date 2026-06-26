// ============================================================
// ATMOSFEARLESS - Frontend Logic
// ============================================================

console.log('🚀 ATMOSFEARLESS loaded!');

// --- API Configuration ---
// Use the deployed backend URL or localhost for development/
const API_BASE_URL = 'http://localhost:5001/api';
 //const API_BASE_URL = 'https://climate-ai-backend-miuc.onrender.com/api';

// --- Indian Cities ---
const indianCities = [
    { name: 'Delhi', lat: 28.61, lng: 77.23 },
    { name: 'Mumbai', lat: 19.08, lng: 72.88 },
    { name: 'Bangalore', lat: 12.97, lng: 77.59 },
    { name: 'Chennai', lat: 13.08, lng: 80.27 },
    { name: 'Kolkata', lat: 22.57, lng: 88.36 },
    { name: 'Hyderabad', lat: 17.38, lng: 78.48 },
    { name: 'Pune', lat: 18.52, lng: 73.85 },
    { name: 'Ahmedabad', lat: 23.02, lng: 72.57 },
    { name: 'Jaipur', lat: 26.91, lng: 75.79 },
    { name: 'Lucknow', lat: 26.85, lng: 80.95 },
    { name: 'Bhopal', lat: 23.26, lng: 77.41 },
    { name: 'Patna', lat: 25.59, lng: 85.14 }
];

// --- State ---
let currentCity = { name: 'Delhi', lat: 28.61, lng: 77.23 };
let map = null;
let markers = [];
let currentLayer = 'temp';
let cityData = {};

// --- DOM Elements ---
const citySelect = document.getElementById('citySelect');
const refreshBtn = document.getElementById('refreshDataBtn');

// --- API Status Check ---
async function checkAPIStatus() {
    const dot = document.getElementById('apiStatusDot');
    const text = document.getElementById('apiStatusText');
    
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            dot.style.background = '#22c55e';
            text.textContent = 'ONLINE';
            text.style.color = '#22c55e';
            return true;
        } else {
            throw new Error('API returned ' + response.status);
        }
    } catch (error) {
        dot.style.background = '#ef4444';
        text.textContent = 'OFFLINE';
        text.style.color = '#ef4444';
        console.warn('API is offline:', error.message);
        return false;
    }
}

// --- Populate City Dropdown ---
function populateDropdown() {
    citySelect.innerHTML = '';
    indianCities.forEach(city => {
        const option = document.createElement('option');
        option.value = JSON.stringify(city);
        option.textContent = city.name;
        citySelect.appendChild(option);
    });
    citySelect.value = JSON.stringify(currentCity);
}

// --- Update UI with Data ---
function updateUI(data) {
    if (!data) return;
    
    const weather = data.live_weather || {};
    const prediction = data.ai_prediction || {};
    const risk = data.risk_score || {};
    
    // Weather
    document.getElementById('liveTemp').innerHTML = (weather.temperature || '--') + '<span style="font-size:1rem; color:#94a3b8;">°C</span>';
    document.getElementById('liveRain').innerHTML = (weather.rainfall || 0) + '<span style="font-size:1rem; color:#94a3b8;">mm</span>';
    document.getElementById('liveHumidity').innerHTML = (weather.humidity || '--') + '<span style="font-size:1rem; color:#94a3b8;">%</span>';
    document.getElementById('liveWind').innerHTML = (weather.wind_speed || '--') + '<span style="font-size:1rem; color:#94a3b8;">km/h</span>';
    document.getElementById('liveCloud').innerHTML = (weather.cloud_cover || '--') + '<span style="font-size:1rem; color:#94a3b8;">%</span>';
    document.getElementById('livePressure').innerHTML = (weather.pressure || '--') + '<span style="font-size:1rem; color:#94a3b8;">hPa</span>';
    
    // Info Panel
    document.getElementById('infoTemp').textContent = (weather.temperature || '--') + '°C';
    document.getElementById('infoRain').textContent = (weather.rainfall || 0) + 'mm';
    document.getElementById('infoHumidity').textContent = (weather.humidity || '--') + '%';
    document.getElementById('infoRisk').textContent = risk.risk_score || '--';
    
    // Prediction
    const pred = prediction.prediction || 0;
    document.getElementById('predictionValue').textContent = pred.toFixed(3);
    document.getElementById('infoPrediction').textContent = pred.toFixed(3);
    document.getElementById('uncertaintyValue').textContent = '±' + (prediction.uncertainty || 0).toFixed(3);
    document.getElementById('ciLower').textContent = (prediction.confidence_interval?.[0] || 0).toFixed(3);
    document.getElementById('ciUpper').textContent = (prediction.confidence_interval?.[1] || 0).toFixed(3);
    
    // Risk
    const score = risk.risk_score || 0;
    document.getElementById('criScore').textContent = score.toFixed(1);
    document.getElementById('impactAgri').textContent = (risk.temperature_risk || 0).toFixed(1);
    document.getElementById('impactWater').textContent = (risk.rainfall_risk || 0).toFixed(1);
    
    // Risk Level
    const rl = document.getElementById('criLevel');
    let levelText, color;
    if (score < 3) { levelText = 'LOW'; color = '#22c55e'; }
    else if (score < 6) { levelText = 'MODERATE'; color = '#eab308'; }
    else if (score < 8) { levelText = 'HIGH'; color = '#f97316'; }
    else { levelText = 'SEVERE'; color = '#ef4444'; }
    rl.textContent = levelText;
    rl.style.color = color;
    
    // Update time
    document.getElementById('twinUpdate').textContent = 'Just now';
    
    // Store data for map
    cityData[currentCity.name] = {
        temperature: weather.temperature || 0,
        rainfall: weather.rainfall || 0,
        risk_score: risk.risk_score || 0
    };
    addCityMarkers();
    highlightCity(currentCity);
}

// --- Fetch Data from API ---
async function fetchAllDataForCity(city) {
    if (!city) return;
    console.log('📡 Fetching data for', city.name);
    
    // Show loading state
    const infoCityName = document.getElementById('infoCityName');
    if (infoCityName) infoCityName.textContent = city.name + ' ⏳';
    document.getElementById('cityNameDisplay').textContent = city.name;
    document.getElementById('cityCoordsDisplay').textContent = '📍 Latitude: ' + city.lat + ' | Longitude: ' + city.lng;
    
    try {
        const response = await fetch(`${API_BASE_URL}/climate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                lat: city.lat,
                lon: city.lng,
                city: city.name
            })
        });
        
        if (!response.ok) throw new Error('HTTP ' + response.status);
        const data = await response.json();
        console.log('📊 Data received:', data);
        updateUI(data);
        
        // Get XAI explanation
        try {
            const xaiResponse = await fetch(`${API_BASE_URL}/explain_human`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ city: city.name })
            });
            if (xaiResponse.ok) {
                const xaiData = await xaiResponse.json();
                document.getElementById('xaiExplanation').textContent = xaiData.human_explanation || 'Explanation not available.';
                if (xaiData.summary?.confidence) {
                    const el = document.getElementById('confidenceLevel');
                    el.textContent = xaiData.summary.confidence;
                    el.style.color = xaiData.summary.confidence === 'HIGH' ? '#22c55e' : xaiData.summary.confidence === 'MEDIUM' ? '#eab308' : '#ef4444';
                    el.style.background = 'rgba(30,41,59,0.5)';
                    el.style.padding = '2px 12px';
                    el.style.borderRadius = '12px';
                }
            }
        } catch (xaiErr) {
            console.warn('XAI not available:', xaiErr);
        }
        
    } catch (error) {
        console.error('❌ Error fetching data:', error);
        document.getElementById('infoCityName').textContent = city.name + ' ❌';
        document.getElementById('xaiExplanation').textContent = '⚠️ Failed to fetch data. API may be offline.';
    }
}

// --- Map Functions ---
function initMap() {
    if (map) { map.invalidateSize(); return; }
    map = L.map('indiaMap').setView([20.59, 78.96], 4.5);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    console.log('✅ Map initialized!');
    addCityMarkers();
}

function addCityMarkers() {
    if (!map) return;
    markers.forEach(m => map.removeLayer(m));
    markers = [];
    
    indianCities.forEach(city => {
        const data = cityData[city.name] || {};
        const risk = data.risk_score || 0;
        let color = '#22c55e';
        if (risk > 7) color = '#ef4444';
        else if (risk > 5) color = '#f97316';
        else if (risk > 3) color = '#eab308';
        
        // Layer-based colors
        if (currentLayer === 'temp') {
            const temp = data.temperature || 25;
            if (temp > 35) color = '#ef4444';
            else if (temp > 30) color = '#f97316';
            else if (temp > 25) color = '#eab308';
            else color = '#22c55e';
        } else if (currentLayer === 'rain') {
            const rain = data.rainfall || 0;
            if (rain > 50) color = '#3b82f6';
            else if (rain > 20) color = '#60a5fa';
            else if (rain > 5) color = '#93c5fd';
            else color = '#fbbf24';
        } else if (currentLayer === 'sat') {
            color = '#a78bfa';
        }
        
        const marker = L.circleMarker([city.lat, city.lng], {
            radius: city.name === currentCity.name ? 12 : 8,
            fillColor: color,
            color: city.name === currentCity.name ? 'white' : color,
            weight: city.name === currentCity.name ? 3 : 1,
            fillOpacity: 0.8
        }).addTo(map);
        
        marker.bindPopup('<strong>' + city.name + '</strong><br>🌡️ ' + (data.temperature || '--') + '°C<br>🌧️ ' + (data.rainfall || '--') + 'mm<br>⚠️ Risk: ' + (data.risk_score || '--'));
        
        marker.on('click', function() {
            currentCity = { name: city.name, lat: city.lat, lng: city.lng };
            citySelect.value = JSON.stringify(currentCity);
            fetchAllDataForCity(currentCity);
            highlightCity(city);
        });
        markers.push(marker);
    });
}

function highlightCity(city) {
    markers.forEach(m => {
        const isSelected = m.getPopup()?.getContent()?.includes(city.name);
        m.setRadius(isSelected ? 14 : 8);
        m.setStyle({
            weight: isSelected ? 3 : 1,
            color: isSelected ? 'white' : m.options.color
        });
    });
    if (map) map.flyTo([city.lat, city.lng], 7, { duration: 1.5 });
}

function changeLayer(layer) {
    currentLayer = layer;
    document.querySelectorAll('.layer-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.layer === layer);
    });
    addCityMarkers();
}

// --- Simulation ---
function runSimulation() {
    const tempChange = parseFloat(document.getElementById('tempSlider').value || 0);
    const rainChange = parseFloat(document.getElementById('rainSlider').value || 0);
    
    fetch(`${API_BASE_URL}/whatif`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            city: currentCity.name,
            temp_delta: tempChange,
            rain_delta: rainChange
        })
    })
    .then(res => res.json())
    .then(result => {
        const el = document.getElementById('simResult');
        const newPred = result.whatif_prediction || 0;
        let text = '📊 New Prediction: ' + newPred.toFixed(3);
        if (newPred > 0.2) text += ' ☀️ (Above-normal)';
        else if (newPred < -0.2) text += ' 🌧️ (Below-normal)';
        else text += ' ⚖️ (Near-normal)';
        text += ' (Temp: ' + (tempChange > 0 ? '+' : '') + tempChange + '°C, Rain: ' + (rainChange > 0 ? '+' : '') + rainChange + '%)';
        el.textContent = text;
        el.style.color = '#22c55e';
    })
    .catch(err => {
        console.error('Simulation error:', err);
        document.getElementById('simResult').textContent = '⚠️ API offline. Please try again later.';
        document.getElementById('simResult').style.color = '#ef4444';
    });
}

// --- Event Listeners ---
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ DOM loaded');
    
    populateDropdown();
    initMap();
    checkAPIStatus();
    
    // Load default city
    setTimeout(() => fetchAllDataForCity(currentCity), 500);
    
    citySelect.addEventListener('change', function() {
        const selected = JSON.parse(this.value);
        currentCity = selected;
        fetchAllDataForCity(selected);
        highlightCity(selected);
    });
    
    refreshBtn.addEventListener('click', function() {
        fetchAllDataForCity(currentCity);
        checkAPIStatus();
    });
    
    document.getElementById('tempSlider').addEventListener('input', function() {
        document.getElementById('tempDisplay').textContent = (this.value > 0 ? '+' : '') + this.value + '°C';
    });
    document.getElementById('rainSlider').addEventListener('input', function() {
        document.getElementById('rainDisplay').textContent = (this.value > 0 ? '+' : '') + this.value + '%';
    });
    document.getElementById('runSimulation').addEventListener('click', runSimulation);
    
    // Hide loading screen
    const ls = document.getElementById('loadingScreen');
    if (ls) {
        setTimeout(function() { ls.style.display = 'none'; }, 1000);
    }
    
    // Check API status every 60 seconds
    setInterval(checkAPIStatus, 60000);
    
    console.log('✅ ATMOSFEARLESS is ready!');
});
