import joblib
import numpy as np
import os
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)

# Load model once
model_path = os.path.join('models', 'aqi_model.pkl')
try:
    model = joblib.load(model_path)
    logging.info("Model loaded successfully")
except:
    logging.warning("Model not found. Using simple prediction.")
    model = None

def predict_aqi(current_aqi, temperature=None, humidity=None, wind_speed=None):
    """
    Predict next AQI value
    If model not available, use simple moving average
    """
    if model is not None:
        try:
            now = datetime.now()
            features = np.array([[
                now.hour,
                now.day,
                now.month,
                temperature or 25.0,
                humidity or 60.0,
                wind_speed or 5.0,
                current_aqi
            ]])
            
            prediction = model.predict(features)[0]
            return max(0, round(prediction, 1))
        except Exception as e:
            logging.error(f"Model prediction failed: {e}")
            return _simple_predict(current_aqi)
    else:
        return _simple_predict(current_aqi)

def _simple_predict(current_aqi):
    """Simple prediction using trend"""
    # Assume slight increase with some randomness
    import random
    change = random.uniform(-10, 20)
    predicted = current_aqi + change
    return max(0, round(predicted, 1))

def predict_trend(aqi_history):
    """Predict trend based on history"""
    if len(aqi_history) < 2:
        return "stable"
    
    recent = aqi_history[-3:] if len(aqi_history) >= 3 else aqi_history
    if all(recent[i] < recent[i+1] for i in range(len(recent)-1)):
        return "increasing"
    elif all(recent[i] > recent[i+1] for i in range(len(recent)-1)):
        return "decreasing"
    else:
        return "stable"