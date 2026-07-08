import requests
from app.config import Config
import time
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)

def get_current_aqi(lat, lon):
    """
    Fetch current AQI and Weather 
    Prioritizes IQAir (WAQI) for pollution data - better for air quality
    Falls back to OpenWeather then simulated data if APIs fail
    """
    # First try: IQAir (WAQI) - best for air pollution data
    aqi_result = _fetch_aqi_from_waqi(lat, lon)
    
    # Second try: OpenWeather if WAQI fails
    if not aqi_result:
        aqi_result = _fetch_aqi_from_openweather(lat, lon)
    
    # Get weather from OpenWeather
    weather_result = _fetch_weather_from_openweather(lat, lon)
    
    # Combine results
    if aqi_result:
        aqi_result['weather'] = weather_result
        return aqi_result
    else:
        result = _get_simulated_aqi(lat, lon)
        result['weather'] = weather_result or _get_simulated_weather()
        return result

def get_nearby_stations(lat, lon, limit=10):
    """
    Fetch nearby pollution monitoring stations from WAQI (IQAir) API
    Returns list of stations with AQI data for the map
    """
    stations = _fetch_stations_from_waqi(lat, lon, limit)
    if stations:
        return stations
    return _get_simulated_stations(lat, lon)

def _fetch_aqi_from_waqi(lat, lon):
    """Fetch AQI from WAQI (IQAir) API - better for pollution detection"""
    try:
        if not Config.WAQI_API_KEY:
            logging.warning("WAQI API key not configured")
            return None
            
        url = f"https://api.waqi.info/feed/geo:{lat};{lon}/"
        params = {
            'token': Config.WAQI_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'ok' and data.get('data'):
                aqi_data = data['data']
                iaqi = aqi_data.get('iaqi', {})
                
                # Extract AQI value
                aqi = aqi_data.get('aqi')
                
                # Extract individual pollutant components
                components = {
                    'pm2_5': _get_iaqi_value(iaqi, 'pm25'),
                    'pm10': _get_iaqi_value(iaqi, 'pm10'),
                    'no2': _get_iaqi_value(iaqi, 'no2'),
                    'so2': _get_iaqi_value(iaqi, 'so2'),
                    'o3': _get_iaqi_value(iaqi, 'o3'),
                    'co': _get_iaqi_value(iaqi, 'co')
                }
                
                result = {
                    'aqi': aqi,
                    'components': components,
                    'timestamp': datetime.now().isoformat(),
                    'source': 'IQAir (WAQI)'
                }
                
                logging.info(f"Fetched AQI from IQAir: {aqi}")
                return result
        return None
    except Exception as e:
        logging.error(f"IQAir AQI API error: {e}")
        return None

def _get_iaqi_value(iaqi, pollutant):
    """Extract IAQI value from WAQI response"""
    try:
        if pollutant in iaqi and 'v' in iaqi[pollutant]:
            return iaqi[pollutant]['v']
    except:
        pass
    return None

def _fetch_stations_from_waqi(lat, lon, limit):
    """Fetch nearby stations from WAQI (IQAir) API"""
    try:
        if not Config.WAQI_API_KEY:
            logging.warning("WAQI API key not configured")
            return None
            
        url = f"https://api.waqi.info/map/bounds/"
        # WAQI uses bounding box: lon-left,lat-bottom,lon-right,lat-top
        # Get a 0.5 degree box around the location
        params = {
            'token': Config.WAQI_API_KEY,
            'latlng': f'{lat-0.5},{lon-0.5},{lat+0.5},{lon+0.5}'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'ok' and data.get('data'):
                stations = []
                for station in data['data'][:limit]:
                    stations.append({
                        'uid': station.get('uid'),
                        'name': station.get('station', {}).get('name', 'Unknown'),
                        'lat': station.get('lat'),
                        'lon': station.get('lon'),
                        'aqi': station.get('aqi'),
                        'time': station.get('time')
                    })
                logging.info(f"Fetched {len(stations)} stations from WAQI")
                return stations
        return None
    except Exception as e:
        logging.error(f"WAQI stations API error: {e}")
        return None

def _fetch_aqi_from_openweather(lat, lon):
    """Fetch AQI from OpenWeather Air Pollution API"""
    try:
        url = "http://api.openweathermap.org/data/2.5/air_pollution"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': Config.OPENWEATHER_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            aqi_data = {
                'aqi': data['list'][0]['main']['aqi'] * 50,  # Convert 1-5 scale to ~50-250
                'components': data['list'][0]['components'],
                'timestamp': datetime.now().isoformat(),
                'source': 'OpenWeather'
            }
            logging.info(f"Fetched AQI from OpenWeather: {aqi_data['aqi']}")
            return aqi_data
        else:
            return None
            
    except Exception as e:
        logging.error(f"OpenWeather AQI API error: {e}")
        return None

def _fetch_weather_from_openweather(lat, lon):
    """Fetch weather from OpenWeather Weather API"""
    try:
        url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': Config.OPENWEATHER_API_KEY,
            'units': 'metric'  # Celsius
        }
        
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            # Get visibility (default to 10km if not available)
            visibility = data.get('visibility', 10000) / 1000  # Convert m to km
            
            weather_data = {
                'temperature': round(data['main']['temp'], 1),
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'wind_speed': round(data['wind']['speed'] * 3.6, 1),  # Convert m/s to km/h
                'visibility': round(visibility, 1),
                'description': data['weather'][0]['description'],
                'icon': data['weather'][0]['icon']
            }
            
            # Calculate UV index estimate based on time of day and cloud cover
            try:
                uv_url = "http://api.openweathermap.org/data/2.5/uvi"
                uv_params = {
                    'lat': lat,
                    'lon': lon,
                    'appid': Config.OPENWEATHER_API_KEY
                }
                uv_response = requests.get(uv_url, params=uv_params, timeout=5)
                if uv_response.status_code == 200:
                    uv_data = uv_response.json()
                    weather_data['uv_index'] = round(uv_data.get('value', 0), 1)
                else:
                    # Estimate UV based on time
                    hour = datetime.now().hour
                    cloud_factor = data.get('clouds', {}).get('all', 50) / 100
                    base_uv = 10 if 10 <= hour <= 16 else 2
                    weather_data['uv_index'] = round(base_uv * (1 - cloud_factor * 0.7), 1)
            except:
                # Estimate UV based on time
                hour = datetime.now().hour
                cloud_factor = data.get('clouds', {}).get('all', 50) / 100
                base_uv = 10 if 10 <= hour <= 16 else 2
                weather_data['uv_index'] = round(base_uv * (1 - cloud_factor * 0.7), 1)
            
            logging.info(f"Fetched Weather from OpenWeather: {weather_data['temperature']}°C, UV: {weather_data.get('uv_index', 'N/A')}")
            return weather_data
        else:
            return None
            
    except Exception as e:
        logging.error(f"OpenWeather Weather API error: {e}")
        return None

def _get_simulated_weather():
    """Generate simulated weather data for testing"""
    import random
    # Simulate UV based on time of day
    hour = datetime.now().hour
    base_uv = 10 if 10 <= hour <= 16 else 2
    return {
        'temperature': round(20 + random.uniform(0, 15), 1),
        'humidity': round(50 + random.uniform(0, 30)),
        'pressure': round(1010 + random.uniform(-20, 20)),
        'wind_speed': round(5 + random.uniform(0, 10), 1),
        'visibility': round(8 + random.uniform(0, 7), 1),
        'uv_index': round(base_uv + random.uniform(-2, 2), 1),
        'description': 'clear sky',
        'icon': '01d'
    }

def _get_simulated_aqi(lat, lon):
    """Generate simulated AQI data for testing"""
    import random
    import math
    
    # Base AQI with some geographic variation
    base_aqi = 100 + abs(lat - 28.6) * 10 + abs(lon - 77.2) * 5
    
    # Add time-based variation
    hour = datetime.now().hour
    time_factor = 20 * math.sin(hour / 24 * 2 * math.pi)
    
    # Add randomness
    random_factor = random.uniform(-15, 15)
    
    aqi = base_aqi + time_factor + random_factor
    aqi = max(20, min(400, aqi))  # Clamp between 20-400
    
    return {
        'aqi': round(aqi, 1),
        'components': {
            'pm2_5': round(aqi * 0.4, 1),
            'pm10': round(aqi * 0.6, 1),
            'no2': round(aqi * 0.3, 1),
            'so2': round(aqi * 0.2, 1),
            'o3': round(100 - aqi * 0.2, 1),
            'co': round(aqi * 0.01, 2)
        },
        'timestamp': datetime.now().isoformat(),
        'source': 'Simulated'
    }

def _get_simulated_stations(lat, lon):
    """Generate simulated nearby stations for map display"""
    import random
    
    stations = []
    city_names = ['Central Station', 'North Zone', 'South Zone', 'East Area', 'West District', 
                  'Industrial Area', 'Residential Zone', 'Commercial District', 'Park Area', 'Highway Station']
    
    for i, name in enumerate(city_names[:8]):
        # Random offset from center
        offset_lat = (random.random() - 0.5) * 0.4
        offset_lon = (random.random() - 0.5) * 0.4
        
        # Base AQI with variation
        station_aqi = round(50 + random.uniform(0, 150))
        
        stations.append({
            'uid': i + 1,
            'name': name,
            'lat': lat + offset_lat,
            'lon': lon + offset_lon,
            'aqi': station_aqi,
            'time': datetime.now().isoformat()
        })
    
    logging.info(f"Generated {len(stations)} simulated stations")
    return stations
