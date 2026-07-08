import requests
from app.config import Config
import logging

logging.basicConfig(level=logging.INFO)

def get_weather(lat, lon):
    """Fetch current weather data"""
    try:
        url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': Config.OPENWEATHER_API_KEY,
            'units': 'metric'
        }
        
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            weather_data = {
                'temperature': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'wind_speed': data['wind']['speed'],
                'wind_direction': data['wind']['deg'],
                'description': data['weather'][0]['description'],
                'icon': data['weather'][0]['icon']
            }
            return weather_data
        else:
            return _get_simulated_weather()
            
    except Exception as e:
        logging.error(f"Weather API error: {e}")
        return _get_simulated_weather()

def _get_simulated_weather():
    """Generate simulated weather data"""
    import random
    return {
        'temperature': round(random.uniform(15, 35), 1),
        'humidity': round(random.uniform(30, 80), 1),
        'pressure': round(random.uniform(980, 1020), 1),
        'wind_speed': round(random.uniform(0, 15), 1),
        'wind_direction': random.randint(0, 360),
        'description': 'simulated data',
        'icon': '01d'
    }