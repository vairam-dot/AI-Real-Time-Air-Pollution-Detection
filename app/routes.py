from flask import render_template, request, jsonify, current_app, g, make_response, session, redirect, url_for, flash
from app import socketio
from services.aqi_service import get_current_aqi, get_nearby_stations
from services.route_service import get_safe_route
from app.translations import t, get_current_language, set_language, get_language_list

import logging
import requests                    # used by manual-search
import random
import string


def generate_otp(length=6):
    """Generate a random OTP code"""
    return ''.join(random.choices(string.digits, k=length))

logging.basicConfig(level=logging.INFO)

def register_routes(app):
    """Register all routes with the app instance"""

    # user cookie / profile middleware removed – no more user_service calls

    # inject login status and language into templates
    @app.context_processor
    def _inject_user():
        return dict(
            logged_in=session.get('logged_in', False), 
            username=session.get('username'),
            current_language=get_current_language(),
            languages=get_language_list(),
            t=t
        )
    
    # Language switching endpoint
    @app.route('/api/set-language', methods=['POST'])
    def set_language_route():
        data = request.get_json()
        lang = data.get('language', 'en')
        if set_language(lang):
            return jsonify({'success': True, 'language': lang})
        return jsonify({'success': False, 'error': 'Invalid language'}), 400
    
    # Get translations endpoint
    @app.route('/api/translations')
    def get_translations():
        lang = request.args.get('lang', get_current_language())
        from app.translations import TRANSLATIONS
        translations = TRANSLATIONS.get(lang, TRANSLATIONS.get('en', {}))
        return jsonify(translations)

    @app.route('/')
    def index():
        # First page: Login page
        if session.get('logged_in'):
            return redirect(url_for('home'))
        return render_template('login.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        # Login page - handles POST authentication
        if session.get('logged_in'):
            return redirect(url_for('home'))
        
        if request.method == 'POST':
            from app.models import db, User, UserPreference
            from werkzeug.security import check_password_hash
            from datetime import datetime
            
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            
            user = User.query.filter_by(username=username).first()
            
            if user and user.is_active and check_password_hash(user.password_hash, password):
                # Check if user is verified
                if not user.is_verified:
                    flash('Please verify your account using OTP sent to your email/phone', 'warning')
                    return render_template('login.html')
                user.last_login = datetime.utcnow()
                db.session.commit()
                
                session['logged_in'] = True
                session['username'] = user.username
                session['user_id'] = user.id
                
                pref = UserPreference.query.filter_by(user_id=user.id).first()
                if not pref:
                    pref = UserPreference(user_id=user.id)
                    db.session.add(pref)
                    db.session.commit()
                
                flash('Logged in successfully', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid username or password', 'danger')
        
        return render_template('login.html')

    @app.route('/home')
    def home():
        # Second page: Home page (after login)
        if not session.get('logged_in'):
            return redirect(url_for('index'))
        return render_template('index.html')

    @app.route('/dashboard')
    def dashboard():
        # Third page: Dashboard
        if not session.get('logged_in'):
            return redirect(url_for('index'))
        return render_template('dashboard.html')

    @app.route('/signup')
    def signup():
        """Signup page"""
        if session.get('logged_in'):
            return redirect(url_for('home'))
        return render_template('signup.html')

    @app.route('/verify-otp')
    def verify_otp_page():
        """OTP verification page"""
        if session.get('logged_in'):
            return redirect(url_for('home'))
        return render_template('signup.html')

    @app.route('/api/signup', methods=['POST'])
    def api_signup():
        """Handle signup and send OTP"""
        from app.models import db, User
        from werkzeug.security import generate_password_hash
        from datetime import datetime, timedelta
        
        data = request.get_json()
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        phone = data.get('phone', '').strip()
        full_name = data.get('full_name', '').strip()
        password = data.get('password', '')
        
        # Validate inputs
        if not username or not email or not password:
            return jsonify({'success': False, 'message': 'All fields are required'}), 400
        
        # Check if username exists
        if User.query.filter_by(username=username).first():
            return jsonify({'success': False, 'message': 'Username already exists'}), 400
        
        # Check if email exists
        if User.query.filter_by(email=email).first():
            return jsonify({'success': False, 'message': 'Email already registered'}), 400
        
        # Check if phone exists
        if phone and User.query.filter_by(phone=phone).first():
            return jsonify({'success': False, 'message': 'Phone number already registered'}), 400
        
        # Generate OTP
        otp = generate_otp()
        
        # Create user (not verified yet)
        user = User(
            username=username,
            email=email,
            phone=phone,
            full_name=full_name,
            password_hash=generate_password_hash(password),
            is_verified=False,
            otp_code=otp,
            otp_expires=datetime.utcnow() + timedelta(minutes=10)
        )
        
        db.session.add(user)
        
        try:
            db.session.commit()
            
            # Log OTP to console (for testing - in production, integrate with SMS/email service)
            print(f"\n" + "="*50)
            print(f"📧 OTP for {username}")
            print(f"   Email: {email}")
            print(f"   Phone: {phone}")
            print(f"   OTP: {otp}")
            print(f"="*50 + "\n")
            
            logging.info(f"OTP sent for {username}: {otp}")
            
            return jsonify({
                'success': True, 
                'message': 'OTP sent successfully!',
                'otp': otp,
                'username': username
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/api/verify-otp', methods=['POST'])
    def api_verify_otp():
        """Verify OTP and complete registration"""
        from app.models import db, User
        from datetime import datetime
        
        data = request.get_json()
        
        username = data.get('username', '').strip()
        otp = data.get('otp', '').strip()
        
        if not username or not otp:
            return jsonify({'success': False, 'message': 'Username and OTP are required'}), 400
        
        # Find user
        user = User.query.filter_by(username=username).first()
        
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        # Check if already verified
        if user.is_verified:
            return jsonify({'success': False, 'message': 'Account already verified'}), 400
        
        # Verify OTP
        if user.otp_code != otp:
            return jsonify({'success': False, 'message': 'Invalid OTP'}), 400
        
        # Check expiration
        if user.otp_expires and user.otp_expires < datetime.utcnow():
            return jsonify({'success': False, 'message': 'OTP expired. Please resend.'}), 400
        
        # Mark as verified
        user.is_verified = True
        user.otp_code = None
        user.otp_expires = None
        
        try:
            db.session.commit()
            return jsonify({'success': True, 'message': 'Account verified successfully!'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/api/resend-otp', methods=['POST'])
    def api_resend_otp():
        """Resend OTP"""
        from app.models import db, User
        from datetime import datetime, timedelta
        
        data = request.get_json()
        username = data.get('username', '').strip()
        
        if not username:
            return jsonify({'success': False, 'message': 'Username is required'}), 400
        
        # Find user
        user = User.query.filter_by(username=username).first()
        
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        if user.is_verified:
            return jsonify({'success': False, 'message': 'Account already verified'}), 400
        
        # Generate new OTP
        otp = generate_otp()
        user.otp_code = otp
        user.otp_expires = datetime.utcnow() + timedelta(minutes=10)
        
        try:
            db.session.commit()
            
            # Log OTP to console
            print(f"\n" + "="*50)
            print(f"📧 OTP Resend for {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Phone: {user.phone}")
            print(f"   OTP: {otp}")
            print(f"="*50 + "\n")
            
            logging.info(f"OTP resent for {username}: {otp}")
            
            return jsonify({'success': True, 'message': 'OTP resent successfully!', 'otp': otp})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/logout')
    def logout():
        session.clear()
        flash('You have been logged out', 'info')
        return redirect(url_for('login'))

    @app.route('/api/current-aqi')
    def current_aqi():
        lat = request.args.get('lat', app.config['DEFAULT_LAT'], type=float)
        lon = request.args.get('lon', app.config['DEFAULT_LON'], type=float)

        aqi_data = get_current_aqi(lat, lon)
        return jsonify(aqi_data)

    @app.route('/api/nearby-stations')
    def nearby_stations():
        """Get nearby pollution monitoring stations from WAQI (IQAir) API"""
        lat = request.args.get('lat', app.config['DEFAULT_LAT'], type=float)
        lon = request.args.get('lon', app.config['DEFAULT_LON'], type=float)
        limit = request.args.get('limit', 10, type=int)

        stations = get_nearby_stations(lat, lon, limit)
        return jsonify({'stations': stations, 'count': len(stations)})

    @app.route('/api/safe-route')
    def safe_route():
        start_lat = request.args.get('start_lat', type=float)
        start_lon = request.args.get('start_lon', type=float)
        end_lat = request.args.get('end_lat', type=float)
        end_lon = request.args.get('end_lon', type=float)

        route = get_safe_route(start_lat, start_lon, end_lat, end_lon)
        return jsonify(route)

    @app.route('/api/manual-search')
    def manual_search():
        """Search for a place in Tamil Nadu (or accept lat,lon) and return AQI info."""
        q = request.args.get('q', '').strip()
        if not q:
            return jsonify({'error': 'Missing query parameter q'}), 400

        # coordinates?
        if ',' in q:
            parts = q.split(',')
            try:
                lat = float(parts[0].strip())
                lon = float(parts[1].strip())
                aqi = get_current_aqi(lat, lon)
                return jsonify({'query': q, 'results': [{'lat': lat, 'lon': lon, 'aqi': aqi}]})
            except Exception:
                pass

        # forward geocode with Nominatim
        try:
            params = {
                'q': f"{q}, Tamil Nadu, India",
                'format': 'json',
                'limit': 5,
                'countrycodes': 'in',
                'addressdetails': 0
            }
            headers = {'User-Agent': 'AirPollutionAI/1.0 (contact@localhost)'}
            resp = requests.get('https://nominatim.openstreetmap.org/search',
                                params=params, headers=headers, timeout=6)
            results = []
            if resp.status_code == 200:
                places = resp.json()
                for p in places:
                    try:
                        lat = float(p.get('lat'))
                        lon = float(p.get('lon'))
                    except Exception:
                        continue
                    aqi = get_current_aqi(lat, lon)
                    results.append({'name': p.get('display_name'),
                                    'lat': lat, 'lon': lon, 'aqi': aqi})

            if not results:
                return jsonify({'query': q, 'results': [], 'message': 'No matches found'}), 404

            return jsonify({'query': q, 'results': results})
        except Exception as e:
            logging.exception('Geocoding error')
            return jsonify({'error': 'Geocoding error', 'details': str(e)}), 500

    # ========== Database API Endpoints ==========
    
    @app.route('/api/save-aqi', methods=['POST'])
    def save_aqi():
        """Save AQI record to database"""
        from app.models import db, AQIRecord
        
        data = request.get_json()
        
        try:
            record = AQIRecord(
                latitude=data.get('latitude'),
                longitude=data.get('longitude'),
                location_name=data.get('location_name'),
                aqi=data.get('aqi'),
                pm25=data.get('pm25'),
                pm10=data.get('pm10'),
                no2=data.get('no2'),
                so2=data.get('so2'),
                o3=data.get('o3'),
                co=data.get('co'),
                source=data.get('source', 'OpenWeather')
            )
            db.session.add(record)
            db.session.commit()
            
            return jsonify({'success': True, 'id': record.id})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/aqi-history')
    def aqi_history():
        """Get AQI history from database"""
        from app.models import AQIRecord
        from datetime import datetime, timedelta
        
        hours = request.args.get('hours', 24, type=int)
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        
        # Calculate time range
        since = datetime.utcnow() - timedelta(hours=hours)
        
        # Build query
        query = AQIRecord.query.filter(AQIRecord.recorded_at >= since)
        
        # Filter by location if provided
        if lat and lon:
            # Within ~50km radius
            query = query.filter(
                AQIRecord.latitude.between(lat - 0.5, lat + 0.5),
                AQIRecord.longitude.between(lon - 0.5, lon + 0.5)
            )
        
        records = query.order_by(AQIRecord.recorded_at.desc()).limit(100).all()
        
        return jsonify({
            'records': [r.to_dict() for r in records],
            'count': len(records)
        })
    
    @app.route('/api/user/preferences', methods=['GET', 'POST'])
    def user_preferences():
        """Get or update user preferences"""
        from app.models import db, UserPreference
        
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not logged in'}), 401
        
        if request.method == 'GET':
            pref = UserPreference.query.filter_by(user_id=user_id).first()
            if pref:
                return jsonify(pref.to_dict())
            return jsonify({})
        
        # POST - update preferences
        data = request.get_json()
        pref = UserPreference.query.filter_by(user_id=user_id).first()
        
        if not pref:
            pref = UserPreference(user_id=user_id)
            db.session.add(pref)
        
        # Update fields
        if 'language' in data:
            pref.language = data['language']
        if 'default_latitude' in data:
            pref.default_latitude = data['default_latitude']
        if 'default_longitude' in data:
            pref.default_longitude = data['default_longitude']
        if 'alert_threshold' in data:
            pref.alert_threshold = data['alert_threshold']
        if 'dark_mode' in data:
            pref.dark_mode = data['dark_mode']
        if 'notify_email' in data:
            pref.notify_email = data['notify_email']
        if 'notify_sms' in data:
            pref.notify_sms = data['notify_sms']
        
        try:
            db.session.commit()
            return jsonify({'success': True, 'preferences': pref.to_dict()})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/alerts', methods=['GET', 'POST'])
    def alerts():
        """Get or create alerts"""
        from app.models import db, Alert
        
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not logged in'}), 401
        
        if request.method == 'GET':
            unread_only = request.args.get('unread', 'false').lower() == 'true'
            query = Alert.query.filter_by(user_id=user_id)
            if unread_only:
                query = query.filter_by(is_read=False)
            
            alerts = query.order_by(Alert.created_at.desc()).limit(50).all()
            return jsonify({'alerts': [a.to_dict() for a in alerts]})
        
        # POST - create alert
        data = request.get_json()
        alert = Alert(
            user_id=user_id,
            aqi_value=data.get('aqi_value'),
            location_name=data.get('location_name'),
            alert_type=data.get('alert_type', 'warning'),
            message=data.get('message')
        )
        db.session.add(alert)
        
        try:
            db.session.commit()
            return jsonify({'success': True, 'id': alert.id})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/alerts/<int:alert_id>/read', methods=['POST'])
    def mark_alert_read(alert_id):
        """Mark an alert as read"""
        from app.models import db, Alert
        
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not logged in'}), 401
        
        alert = Alert.query.filter_by(id=alert_id, user_id=user_id).first()
        if alert:
            alert.is_read = True
            db.session.commit()
            return jsonify({'success': True})
        
        return jsonify({'success': False, 'error': 'Alert not found'}), 404

    logging.info("✅ Routes registered successfully with database support")
