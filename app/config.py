import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key-change-me')
    
    # API Keys
    OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY', '')
    ORS_API_KEY = os.getenv('ORS_API_KEY', '')
    WAQI_API_KEY = os.getenv('WAQI_API_KEY', '')
    
    # Alert thresholds
    AQI_THRESHOLD_UNSAFE = int(os.getenv('AQI_THRESHOLD_UNSAFE', 150))
    AQI_THRESHOLD_WARNING = int(os.getenv('AQI_THRESHOLD_WARNING', 100))
    
    # Update interval (seconds)
    UPDATE_INTERVAL = int(os.getenv('UPDATE_INTERVAL', 120))
    
    # Default location (Delhi, India)
    DEFAULT_LAT = float(os.getenv('DEFAULT_LAT', 28.6139))
    DEFAULT_LON = float(os.getenv('DEFAULT_LON', 77.2090))
    
    # Server settings
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))

    # Admin login (defaults for development)
    ADMIN_USER = os.getenv('ADMIN_USER', 'admin')
    ADMIN_PASS = os.getenv('ADMIN_PASS', 'password')
    
    @classmethod
    def validate(cls):
        """Check if all required keys are present"""
        missing = []
        
        if not cls.OPENWEATHER_API_KEY:
            missing.append('OPENWEATHER_API_KEY')
        else:
            print(f"✅ OpenWeather API Key loaded: {cls.OPENWEATHER_API_KEY[:5]}...")
            
        if not cls.ORS_API_KEY:
            missing.append('ORS_API_KEY')
        else:
            print(f"✅ OpenRouteService API Key loaded: {cls.ORS_API_KEY[:20]}...")
            
        if not cls.WAQI_API_KEY:
            print("⚠️  WAQI API Key not found (optional)")
        else:
            print(f"✅ WAQI API Key loaded: {cls.WAQI_API_KEY[:5]}...")
        
        if missing:
            print(f"⚠️  Missing API keys: {', '.join(missing)}")
            print("   Some features may use simulated data")
            return False
        
        print("✅ All required API keys loaded successfully!")
        return True
