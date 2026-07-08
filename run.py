#!/usr/bin/env python3
"""
AirPollutionAI - Main Entry Point
Run this file to start the application
"""

from app import create_app, socketio
from app.config import Config
import logging
from dotenv import load_dotenv
import os
import webbrowser
from threading import Timer

# Load .env file at startup
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create the Flask app
app = create_app()

def open_browser():
    """Open browser automatically after server starts"""
    try:
        port = getattr(Config, 'PORT', 5000)
        webbrowser.open_new(f'http://localhost:{port}/')
    except:
        print("📊 Please open browser manually to http://localhost:5000/")

if __name__ == '__main__':
    print("=" * 60)
    print("🌍 AirPollutionAI Starting...")
    print("=" * 60)
    
    # Safely get port with default
    port = getattr(Config, 'PORT', 5000)
    host = getattr(Config, 'HOST', '0.0.0.0')
    update_interval = getattr(Config, 'UPDATE_INTERVAL', 120)
    
    print(f"🔐 Login: http://localhost:{port}/")
    print(f"🔄 Updates every {update_interval} seconds")
    print()
    
    # Show API status with your keys
    print("🔑 API Key Status:")
    if hasattr(Config, 'OPENWEATHER_API_KEY') and Config.OPENWEATHER_API_KEY:
        print(f"  ✅ OpenWeather: {Config.OPENWEATHER_API_KEY[:5]}... (active)")
    else:
        print("  ❌ OpenWeather: Missing")
        
    if hasattr(Config, 'ORS_API_KEY') and Config.ORS_API_KEY:
        print(f"  ✅ OpenRouteService: {Config.ORS_API_KEY[:20]}... (active)")
    else:
        print("  ❌ OpenRouteService: Missing")
        
    if hasattr(Config, 'WAQI_API_KEY') and Config.WAQI_API_KEY:
        print(f"  ✅ WAQI: {Config.WAQI_API_KEY[:5]}... (active)")
    else:
        print("  ⚠️  WAQI: Optional - not configured")
    
    print()
    print("🚀 Running with REAL DATA from APIs!")
    print("=" * 60)
    
    # Open browser automatically after 2 seconds (opens login page)
    # Timer(2, open_browser).start()  # Disabled - opens login page manually
    
    # Run the application
    try:
        socketio.run(
            app,
            host=host,
            port=port,
            debug=True
        )
    except Exception as e:
        print(f"⚠️ Error starting server: {e}")
        print("🔄 Trying with default settings...")
        socketio.run(
            app,
            host='0.0.0.0',
            port=5000,
            debug=True
        )