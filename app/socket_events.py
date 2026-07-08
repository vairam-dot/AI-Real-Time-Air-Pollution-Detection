from flask_socketio import emit
from app import socketio
from services.aqi_service import get_current_aqi
from ai.predict import predict_aqi
from app.alerts import check_alert_condition
import logging

logging.basicConfig(level=logging.INFO)

@socketio.on('connect')
def handle_connect():
    logging.info('Client connected')
    emit('connected', {'data': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    logging.info('Client disconnected')

@socketio.on('request_update')
def handle_update_request(data):
    lat = data.get('lat', 28.6139)
    lon = data.get('lon', 77.2090)
    
    # Get current AQI
    current_aqi = get_current_aqi(lat, lon)
    
    # Predict next AQI
    predicted_aqi = predict_aqi(current_aqi['aqi'])
    
    # Check alerts
    alert = check_alert_condition(current_aqi['aqi'], predicted_aqi)
    
    # Send update
    emit('aqi_update', {
        'current': current_aqi,
        'predicted': predicted_aqi,
        'alert': alert,
        'timestamp': current_aqi['timestamp']
    })