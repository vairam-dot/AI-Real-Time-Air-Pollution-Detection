import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import joblib
import os

def generate_sample_data(n_samples=1000):
    """Generate sample AQI data for training"""
    np.random.seed(42)
    
    # Time features
    hour = np.random.randint(0, 24, n_samples)
    day = np.random.randint(1, 31, n_samples)
    month = np.random.randint(1, 13, n_samples)
    
    # Weather factors
    temperature = np.random.uniform(10, 40, n_samples)
    humidity = np.random.uniform(20, 90, n_samples)
    wind_speed = np.random.uniform(0, 20, n_samples)
    
    # Previous AQI (with some pattern)
    prev_aqi = np.random.uniform(50, 300, n_samples)
    
    # Generate AQI with some pattern
    aqi = (
        prev_aqi * 0.6 +
        temperature * 2 +
        (50 - humidity) * 0.5 +
        wind_speed * (-2) +
        np.sin(hour / 24 * 2 * np.pi) * 20 +
        np.random.normal(0, 15, n_samples)
    )
    
    # Ensure positive values
    aqi = np.maximum(aqi, 0)
    
    df = pd.DataFrame({
        'hour': hour,
        'day': day,
        'month': month,
        'temperature': temperature,
        'humidity': humidity,
        'wind_speed': wind_speed,
        'prev_aqi': prev_aqi,
        'aqi': aqi
    })
    
    return df

def train_model():
    """Train and save AQI prediction model"""
    print("Generating training data...")
    df = generate_sample_data()
    
    # Prepare features and target
    feature_cols = ['hour', 'day', 'month', 'temperature', 
                   'humidity', 'wind_speed', 'prev_aqi']
    X = df[feature_cols]
    y = df['aqi']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train model
    print("Training Random Forest model...")
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        random_state=42
    )
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    print(f"Mean Absolute Error: {mae:.2f}")
    
    # Save model
    model_path = os.path.join('models', 'aqi_model.pkl')
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")
    
    return model

if __name__ == "__main__":
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    train_model()