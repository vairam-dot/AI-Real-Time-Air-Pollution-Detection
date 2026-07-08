"""
Database models for AirPollutionAI
Uses SQLAlchemy with SQLite database
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    phone = db.Column(db.String(20), unique=True, nullable=True)
    full_name = db.Column(db.String(100), nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    otp_code = db.Column(db.String(6), nullable=True)
    otp_expires = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'full_name': self.full_name,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active
        }


class AQIRecord(db.Model):
    """AQI records stored in database"""
    __tablename__ = 'aqi_records'
    
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    location_name = db.Column(db.String(200), nullable=True)
    aqi = db.Column(db.Float, nullable=False)
    pm25 = db.Column(db.Float, nullable=True)
    pm10 = db.Column(db.Float, nullable=True)
    no2 = db.Column(db.Float, nullable=True)
    so2 = db.Column(db.Float, nullable=True)
    o3 = db.Column(db.Float, nullable=True)
    co = db.Column(db.Float, nullable=True)
    source = db.Column(db.String(50), default='OpenWeather')
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AQIRecord {self.location_name}: {self.aqi}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'location_name': self.location_name,
            'aqi': self.aqi,
            'pm25': self.pm25,
            'pm10': self.pm10,
            'no2': self.no2,
            'so2': self.so2,
            'o3': self.o3,
            'co': self.co,
            'source': self.source,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None
        }


class UserPreference(db.Model):
    """User preferences for language, location, alerts"""
    __tablename__ = 'user_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    language = db.Column(db.String(10), default='en')
    default_latitude = db.Column(db.Float, nullable=True)
    default_longitude = db.Column(db.Float, nullable=True)
    alert_threshold = db.Column(db.Integer, default=150)
    dark_mode = db.Column(db.Boolean, default=False)
    notify_email = db.Column(db.Boolean, default=True)
    notify_sms = db.Column(db.Boolean, default=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserPreference user_id={self.user_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'language': self.language,
            'default_latitude': self.default_latitude,
            'default_longitude': self.default_longitude,
            'alert_threshold': self.alert_threshold,
            'dark_mode': self.dark_mode,
            'notify_email': self.notify_email,
            'notify_sms': self.notify_sms
        }


class Alert(db.Model):
    """Alert records for AQI thresholds"""
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    aqi_value = db.Column(db.Integer, nullable=False)
    location_name = db.Column(db.String(200), nullable=True)
    alert_type = db.Column(db.String(20), nullable=False)  # warning, danger, severe
    message = db.Column(db.Text, nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Alert user_id={self.user_id} aqi={self.aqi_value}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'aqi_value': self.aqi_value,
            'location_name': self.location_name,
            'alert_type': self.alert_type,
            'message': self.message,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
