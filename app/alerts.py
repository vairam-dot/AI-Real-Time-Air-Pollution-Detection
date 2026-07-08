from app.config import Config
import time

def check_alert_condition(current_aqi, predicted_aqi):
    """
    Check if alert needs to be triggered
    Returns: dict with alert info
    """
    alert = {
        'level': 'normal',
        'message': 'Air quality is normal',
        'color': 'green',
        'timestamp': time.time()
    }
    
    # Check current AQI
    if current_aqi >= Config.AQI_THRESHOLD_UNSAFE:
        alert['level'] = 'danger'
        alert['message'] = f'UNSAFE: AQI is {current_aqi} - Avoid outdoor activities!'
        alert['color'] = 'red'
    elif current_aqi >= Config.AQI_THRESHOLD_WARNING:
        alert['level'] = 'warning'
        alert['message'] = f'WARNING: AQI is {current_aqi} - Limit outdoor exposure'
        alert['color'] = 'orange'
    
    # Check predicted spike
    if predicted_aqi > current_aqi * 1.5:  # 50% increase predicted
        alert['level'] = 'warning'
        alert['message'] += ' ⚠️ Pollution predicted to increase soon!'
        alert['color'] = 'orange'
    
    return alert

def get_health_recommendation(aqi):
    """Get health recommendations based on AQI"""
    if aqi <= 50:
        return "Good - No precautions needed"
    elif aqi <= 100:
        return "Moderate - Sensitive individuals should limit outdoor activity"
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups - Wear mask if going out"
    elif aqi <= 200:
        return "Unhealthy - Avoid outdoor activities, wear N95 mask"
    elif aqi <= 300:
        return "Very Unhealthy - Stay indoors, use air purifier"
    else:
        return "Hazardous - Emergency conditions, stay indoors"