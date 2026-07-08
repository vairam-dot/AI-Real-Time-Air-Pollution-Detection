from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.config import Config
from services.aqi_service import get_current_aqi
from ai.predict import predict_aqi
from app.alerts import check_alert_condition
from flask_socketio import emit
import atexit
import logging

logging.basicConfig(level=logging.INFO)
scheduler = BackgroundScheduler()

def scheduled_update():
    """Run every 2 minutes to fetch and broadcast AQI data"""
    try:
        logging.info("Running scheduled AQI update")
        
        # Get current AQI
        current_aqi = get_current_aqi(
            Config.DEFAULT_LAT, 
            Config.DEFAULT_LON
        )
        
        # Predict next AQI
        predicted_aqi = predict_aqi(current_aqi['aqi'])
        
        # Check alerts
        alert = check_alert_condition(current_aqi['aqi'], predicted_aqi)
        
        # Import socketio here to avoid circular imports
        from app import socketio
        
        # Broadcast to all connected clients
        socketio.emit('scheduled_update', {
            'current': current_aqi,
            'predicted': predicted_aqi,
            'alert': alert,
            'timestamp': current_aqi['timestamp']
        })
        
        logging.info(f"Broadcasted AQI: {current_aqi['aqi']}")
        
    except Exception as e:
        logging.error(f"Scheduler error: {str(e)}")

def start_scheduler(app):
    """Start the background scheduler"""
    if not scheduler.running:
        scheduler.add_job(
            func=scheduled_update,
            trigger=IntervalTrigger(seconds=Config.UPDATE_INTERVAL),
            id='aqi_update_job',
            name='Update AQI every 2 minutes',
            replace_existing=True
        )
        scheduler.start()
        logging.info("Scheduler started")
        
        # Shutdown scheduler when exiting the app
        atexit.register(lambda: scheduler.shutdown())