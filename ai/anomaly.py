import numpy as np
from scipy import stats
import logging

logging.basicConfig(level=logging.INFO)

def detect_anomaly(aqi_value, historical_values, threshold=2.5):
    """
    Detect if current AQI is anomalous
    Uses z-score method
    """
    if len(historical_values) < 5:
        return False, 0
    
    # Calculate z-score
    mean = np.mean(historical_values)
    std = np.std(historical_values)
    
    if std == 0:
        return False, 0
    
    z_score = abs(aqi_value - mean) / std
    
    # Check if anomaly
    is_anomaly = z_score > threshold
    
    if is_anomaly:
        logging.warning(f"Anomaly detected! AQI: {aqi_value}, Z-score: {z_score:.2f}")
    
    return is_anomaly, round(z_score, 2)

def get_anomaly_reason(aqi_value, mean, std):
    """Get explanation for anomaly"""
    if aqi_value > mean + 2*std:
        return "Sudden pollution spike detected! Possible local source."
    elif aqi_value < mean - 2*std:
        return "Unusually clean air! Weather conditions are favorable."
    else:
        return "Normal fluctuation"