"""
Internationalization (i18n) module for AirPollutionAI
Supports: English, Hindi (हिंदी), Tamil (தமிழ்), Telugu (తెలుగు)
"""

from flask import session, request, g
import json
import os

# Translation dictionaries
TRANSLATIONS = {}

def load_translations():
    """Load all translation files"""
    global TRANSLATIONS
    
    # English (default)
    TRANSLATIONS['en'] = {
        # Navigation
        'nav.home': 'Home',
        'nav.dashboard': 'Dashboard',
        'nav.login': 'Login',
        'nav.logout': 'Logout',
        'nav.profile': 'Profile',
        
        # Home page
        'home.title': 'AirPollutionAI',
        'home.subtitle': 'Real-time Air Quality Monitoring',
        'home.get_started': 'Get Started',
        'home.login': 'Login to Dashboard',
        'home.features': 'Features',
        'home.live_aqi': 'Live AQI Updates',
        'home.voice_commands': 'Voice Commands',
        'home.dark_mode': 'Dark/Light Mode',
        'home.safe_routes': 'Safe Routes',
        
        # Dashboard
        'dashboard.title': 'Dashboard',
        'dashboard.current_aqi': 'Current Air Quality',
        'dashboard.prediction': 'AI Prediction',
        'dashboard.weather': 'Weather Conditions',
        'dashboard.pollution_map': 'Live Pollution Map',
        'dashboard.aqi_history': 'AQI History',
        'dashboard.route_planner': 'Safe Route Planner',
        'dashboard.health_advice': 'Personalized Health Advice',
        
        # AQI Categories
        'aqi.good': 'Good',
        'aqi.moderate': 'Moderate',
        'aqi.unhealthy_sensitive': 'Unhealthy for Sensitive Groups',
        'aqi.unhealthy': 'Unhealthy',
        'aqi.very_unhealthy': 'Very Unhealthy',
        'aqi.hazardous': 'Hazardous',
        
        # AQI Values
        'aqi.value': 'AQI Value',
        'aqi.source': 'Source',
        
        # Pollutants
        'pollutant.pm25': 'PM2.5',
        'pollutant.pm10': 'PM10',
        'pollutant.no2': 'NO₂',
        'pollutant.so2': 'SO₂',
        'pollutant.o3': 'O₃',
        'pollutant.co': 'CO',
        
        # Weather
        'weather.temperature': 'Temperature',
        'weather.humidity': 'Humidity',
        'weather.wind': 'Wind Speed',
        'weather.pressure': 'Pressure',
        
        # Health
        'health.mask': 'Mask Needed',
        'health.exercise': 'Outdoor Exercise',
        'health.purifier': 'Air Purifier',
        'health.yes': 'Yes',
        'health.no': 'No',
        'health.limited': 'Limited',
        'health.avoid': 'Avoid',
        'health.allowed': 'Allowed',
        
        # Alerts
        'alert.normal': 'Air quality is good',
        'alert.good': 'Good air quality',
        'alert.moderate': 'Moderate air quality',
        'alert.warning': 'Unhealthy for sensitive groups',
        'alert.danger': 'Unhealthy air quality',
        'alert.severe': 'Very unhealthy - Take precautions',
        
        # Location
        'location.detecting': 'Detecting your location...',
        'location.default': 'Using default location',
        'location.refresh': 'Refresh Location',
        'location.track': 'Track Me',
        'location.correct': 'Correct Location',
        
        # Route
        'route.start': 'Start location',
        'route.end': 'Destination',
        'route.plan': 'Plan Route',
        'route.safe': 'Safe Route',
        'route.shortest': 'Shortest Route',
        'route.distance': 'Distance',
        'route.reduction': 'exposure reduction',
        
        # Voice
        'voice.listening': 'Listening...',
        'voice.speak': 'Click to speak',
        'voice.error': 'Voice recognition error',
        'voice.not_supported': 'Voice recognition not supported',
        'voice.commands': 'Available commands',
        
        # Common
        'common.loading': 'Loading...',
        'common.error': 'Error',
        'common.success': 'Success',
        'common.search': 'Search',
        'common.share': 'Share',
        'common.close': 'Close',
        'common.save': 'Save',
        'common.cancel': 'Cancel',
        
        # Login
        'login.title': 'Administrator Login',
        'login.username': 'Username',
        'login.password': 'Password',
        'login.submit': 'Login',
        'login.error': 'Invalid username or password',
        
        # Time
        'time.hour': 'Hour',
        'time.day': 'Day',
        'time.week': 'Week',
        'time.month': 'Month',
        
        # Prediction
        'prediction.trend': 'Trend',
        'prediction.increasing': 'Increasing',
        'prediction.decreasing': 'Decreasing',
        'prediction.stable': 'Stable',
        'prediction.confidence': 'Confidence',
        'prediction.next_hour': 'Predicted for next hour',
        
        # Stats
        'stats.updates': 'Updates Today',
        'stats.alerts': 'Alerts Today',
        'stats.avg_aqi': 'Avg AQI',
        'stats.data_points': 'Data Points',
    }
    
    # Hindi (हिंदी)
    TRANSLATIONS['hi'] = {
        # Navigation
        'nav.home': 'होम',
        'nav.dashboard': 'डैशबोर्ड',
        'nav.login': 'लॉगिन',
        'nav.logout': 'लॉगआउट',
        'nav.profile': 'प्रोफ़ाइल',
        
        # Home page
        'home.title': 'एयरपॉल्यूशनएआई',
        'home.subtitle': 'वास्तविक समय वायु गुणवत्ता निगरानी',
        'home.get_started': 'शुरू करें',
        'home.login': 'डैशबोर्ड में लॉगिन करें',
        'home.features': 'विशेषताएं',
        'home.live_aqi': 'लाइव AQI अपडेट',
        'home.voice_commands': 'आवाज़ निर्देश',
        'home.dark_mode': 'डार्क/लाइट मोड',
        'home.safe_routes': 'सुरक्षित मार्ग',
        
        # Dashboard
        'dashboard.title': 'डैशबोर्ड',
        'dashboard.current_aqi': 'वर्तमान वायु गुणवत्ता',
        'dashboard.prediction': 'एआई पूर्वानुमान',
        'dashboard.weather': 'मौसम की स्थिति',
        'dashboard.pollution_map': 'लाइव प्रदूषण मानचित्र',
        'dashboard.aqi_history': 'AQI इतिहास',
        'dashboard.route_planner': 'सुरक्षित मार्ग योजनाकार',
        'dashboard.health_advice': 'व्यक्तिगत स्वास्थ्य सलाह',
        
        # AQI Categories
        'aqi.good': 'अच्छी',
        'aqi.moderate': 'मध्यम',
        'aqi.unhealthy_sensitive': 'संवेदनशील समूहों के लिए अस्वस्थ',
        'aqi.unhealthy': 'अस्वस्थ',
        'aqi.very_unhealthy': 'बहुत अस्वस्थ',
        'aqi.hazardous': 'खतरनाक',
        
        # AQI Values
        'aqi.value': 'AQI मान',
        'aqi.source': 'स्रोत',
        
        # Pollutants
        'pollutant.pm25': 'PM2.5',
        'pollutant.pm10': 'PM10',
        'pollutant.no2': 'NO₂',
        'pollutant.so2': 'SO₂',
        'pollutant.o3': 'O₃',
        'pollutant.co': 'CO',
        
        # Weather
        'weather.temperature': 'तापमान',
        'weather.humidity': 'नमी',
        'weather.wind': 'हवा की गति',
        'weather.pressure': 'दबाव',
        
        # Health
        'health.mask': 'मास्क आवश्यक',
        'health.exercise': 'बाहरी व्यायाम',
        'health.purifier': 'एयर प्यूरीफायर',
        'health.yes': 'हाँ',
        'health.no': 'नहीं',
        'health.limited': 'सीमित',
        'health.avoid': 'से बचें',
        'health.allowed': 'अनुमति है',
        
        # Alerts
        'alert.normal': 'वायु गुणवत्ता अच्छी है',
        'alert.good': 'वायु गुणवत्ता अच्छी है',
        'alert.moderate': 'वायु गुणवत्ता मध्यम है',
        'alert.warning': 'संवेदनशील समूहों के लिए अस्वस्थ',
        'alert.danger': 'वायु गुणवत्ता अस्वस्थ है',
        'alert.severe': 'बहुत अस्वस्थ - सावधानी बरतें',
        
        # Location
        'location.detecting': 'आपका स्थान पता लगा रहे हैं...',
        'location.default': 'डिफ़ॉल्ट स्थान का उपयोग',
        'location.refresh': 'स्थान रीफ्रेश करें',
        'location.track': 'मुझे ट्रैक करें',
        'location.correct': 'स्थान सुधारें',
        
        # Route
        'route.start': 'प्रारंभ स्थान',
        'route.end': 'गंतव्य',
        'route.plan': 'मार्ग की योजना',
        'route.safe': 'सुरक्षित मार्ग',
        'route.shortest': 'सबसे छोटा मार्ग',
        'route.distance': 'दूरी',
        'route.reduction': 'एक्सपोज़र में कमी',
        
        # Voice
        'voice.listening': 'सुन रहे हैं...',
        'voice.speak': 'बोलने के लिए क्लिक करें',
        'voice.error': 'आवाज़ पहचान त्रुटि',
        'voice.not_supported': 'आवाज़ पहचान समर्थित नहीं',
        'voice.commands': 'उपलब्ध आदेश',
        
        # Common
        'common.loading': 'लोड हो रहा है...',
        'common.error': 'त्रुटि',
        'common.success': 'सफल',
        'common.search': 'खोजें',
        'common.share': 'साझा करें',
        'common.close': 'बंद करें',
        'common.save': 'सहेजें',
        'common.cancel': 'रद्द करें',
        
        # Login
        'login.title': 'प्रशासक लॉगिन',
        'login.username': 'उपयोगकर्ता नाम',
        'login.password': 'पासवर्ड',
        'login.submit': 'लॉगिन',
        'login.error': 'अमान्य उपयोगकर्ता नाम या पासवर्ड',
        
        # Time
        'time.hour': 'घंटा',
        'time.day': 'दिन',
        'time.week': 'सप्ताह',
        'time.month': 'महीना',
        
        # Prediction
        'prediction.trend': 'रुझान',
        'prediction.increasing': 'बढ़ रहा है',
        'prediction.decreasing': 'घट रहा है',
        'prediction.stable': 'स्थिर',
        'prediction.confidence': 'विश्वास',
        'prediction.next_hour': 'अगले घंटे के लिए पूर्वानुमान',
        
        # Stats
        'stats.updates': 'आज के अपडेट',
        'stats.alerts': 'आज के अलर्ट',
        'stats.avg_aqi': 'औसत AQI',
        'stats.data_points': 'डेटा पॉइंट्स',
    }
    
    # Tamil (தமிழ்)
    TRANSLATIONS['ta'] = {
        # Navigation
        'nav.home': 'முகப்பு',
        'nav.dashboard': 'டैश்போர்டு',
        'nav.login': 'உள் நுழை',
        'nav.logout': 'வெளி நுழை',
        'nav.profile': 'சுயவிவரம்',
        
        # Home page
        'home.title': 'ஏர்போல்யூஷன்ஏஐ',
        'home.subtitle': 'திரைமீது வாயு தரம் கண்காணிப்பு',
        'home.get_started': 'தொடங்கு',
        'home.login': 'டெஷ்போர்டுக்கு உள் நுழை',
        'home.features': 'அம்சங்கள்',
        'home.live_aqi': 'நேரடி AQI புதுப்பிப்புகள்',
        'home.voice_commands': 'குரல் கட்டளைகள்',
        'home.dark_mode': 'இருட்டு/வெளிச்ச பயன்முறை',
        'home.safe_routes': 'பாதுகாப்பான வழிகள்',
        
        # Dashboard
        'dashboard.title': 'டெஷ்போர்டு',
        'dashboard.current_aqi': 'தற்போதைய வாயு தரம்',
        'dashboard.prediction': 'AI கணிப்பு',
        'dashboard.weather': 'வான நிலை',
        'dashboard.pollution_map': 'நேரடி மாசு வரைபடம்',
        'dashboard.aqi_history': 'AQI வரலாறு',
        'dashboard.route_planner': 'பாதுகாப்பான பயண திட்டம்',
        'dashboard.health_advice': 'தனிப்பட்ட ஆலோசனை',
        
        # AQI Categories
        'aqi.good': 'நல்ல',
        'aqi.moderate': 'மிதமான',
        'aqi.unhealthy_sensitive': 'உணர்திறன் குழுவுக்கு ஆரோக்கியமற்ற',
        'aqi.unhealthy': 'ஆரோக்கியமற்ற',
        'aqi.very_unhealthy': 'மிகவும் ஆரோக்கியமற்ற',
        'aqi.hazardous': 'ஆபத்தான',
        
        # AQI Values
        'aqi.value': 'AQI மதிப்பு',
        'aqi.source': 'மூலம்',
        
        # Pollutants
        'pollutant.pm25': 'PM2.5',
        'pollutant.pm10': 'PM10',
        'pollutant.no2': 'NO₂',
        'pollutant.so2': 'SO₂',
        'pollutant.o3': 'O₃',
        'pollutant.co': 'CO',
        
        # Weather
        'weather.temperature': 'வெப்பநிலை',
        'weather.humidity': 'ஈரப்பதம்',
        'weather.wind': 'காற்று வேகம்',
        'weather.pressure': 'அழுத்தம்',
        
        # Health
        'health.mask': 'முகக்கவசம் தேவை',
        'health.exercise': 'வெளி உடற்பயிற்சி',
        'health.purifier': 'காற்று சுத்திகரிப்பான்',
        'health.yes': 'ஆம்',
        'health.no': 'இல்லை',
        'health.limited': 'வரம்பு',
        'health.avoid': 'தவிர்க்க',
        'health.allowed': 'அனுமதி',
        
        # Alerts
        'alert.normal': 'காற்று தரம் நல்லது',
        'alert.good': 'காற்று தரம் நல்லது',
        'alert.moderate': 'காற்று தரம் மிதமானது',
        'alert.warning': 'உணர்திறன் குழுவுக்கு ஆரோக்கியமற்ற',
        'alert.danger': 'காற்று தரம் ஆரோக்கியமற்றது',
        'alert.severe': 'மிகவும் ஆரோக்கியமற்ற - முன்னெச்சரிக்கை தேவை',
        
        # Location
        'location.detecting': 'உங்கள் இடம் கண்டறியப்படுகிறது...',
        'location.default': 'இயல்புநிலை இடம் பயன்படுத்தப்படுகிறது',
        'location.refresh': 'இடம் புதுப்பி',
        'location.track': 'என்னைக் கண்காணி',
        'location.correct': 'இடத்தைத் திருத்து',
        
        # Route
        'route.start': 'தொடக்க இடம்',
        'route.end': 'இலக்கு',
        'route.plan': 'பயணத் திட்டம்',
        'route.safe': 'பாதுகாப்பான வழி',
        'route.shortest': 'குறுகிய வழி',
        'route.distance': 'தூரம்',
        'route.reduction': 'வெளிப்பாடு குறைப்பு',
        
        # Voice
        'voice.listening': 'கேட்கிறது...',
        'voice.speak': 'பேச கிளிக் செய்யவும்',
        'voice.error': 'குரல் recognition பிழை',
        'voice.not_supported': 'குரல் recognition ஆதரவு இல்லை',
        'voice.commands': 'கிடைக்கக்கூடிய கட்டளைகள்',
        
        # Common
        'common.loading': 'ஏற்றுகிறது...',
        'common.error': 'பிழை',
        'common.success': 'வெற்றி',
        'common.search': 'தேடு',
        'common.share': 'பகிர்',
        'common.close': 'மூடு',
        'common.save': 'சேமி',
        'common.cancel': 'ரத்து',
        
        # Login
        'login.title': 'நிர்வாகி உள் நுழை',
        'login.username': 'பயனர்ப் பெயர்',
        'login.password': 'கடவுச்சொல்',
        'login.submit': 'உள் நுழை',
        'login.error': 'தவறான பயனர்ப் பெயர் அல்லது கடவுச்சொல்',
        
        # Time
        'time.hour': 'மணி',
        'time.day': 'நாள்',
        'time.week': 'வாரம்',
        'time.month': 'மாதம்',
        
        # Prediction
        'prediction.trend': 'போக்கு',
        'prediction.increasing': 'அதிகரிக்கிறது',
        'prediction.decreasing': 'குறைகிறது',
        'prediction.stable': 'स्थिर',
        'prediction.confidence': 'நம்பகம்',
        'prediction.next_hour': 'அடுத்த மணி நேரத்திற்கு கணித்தது',
        
        # Stats
        'stats.updates': 'இன்றைய புதுப்பிப்புகள்',
        'stats.alerts': 'இன்றைய எச்சரிக்கைகள்',
        'stats.avg_aqi': 'சராசரி AQI',
        'stats.data_points': 'தரவு புள்ளிகள்',
    }
    
    # Malayalam (മലയാളം)
    TRANSLATIONS['ml'] = {
        # Navigation
        'nav.home': 'ഹോം',
        'nav.dashboard': 'ഡാഷ്‌ബോഡ്',
        'nav.login': 'ലോഗിൻ',
        'nav.logout': 'ലോഗൗട്ട്',
        'nav.profile': 'പ്രൊഫൈല്',
        
        # Dashboard
        'dashboard.title': 'ഡാഷ്‌ബോഡ്',
        'dashboard.current_aqi': 'നിലവിലെ വായു ഗുണം',
        'dashboard.prediction': 'AI പ്രവചനം',
        'dashboard.weather': 'കാലാവസ്ഥ',
        'dashboard.pollution_map': 'മാലിന്് മാപ്പ്',
        'dashboard.aqi_history': 'AQI ചരിത്രം',
        'dashboard.route_planner': 'സുരക്ഷിത റൂട്ട് പ്ലാനറിലെ',
        
        # AQI Categories
        'aqi.good': 'നല്ലത്',
        'aqi.moderate': 'മിതമായ',
        'aqi.unhealthy_sensitive': 'സംവേദനാകുന്നവര്ക്ക് ആരോഗ്യകരമല്ല',
        'aqi.unhealthy': 'ആരോഗ്യകരമല്ല',
        'aqi.very_unhealthy': 'വളരെ ആരോഗ്യകരമല്ല',
        'aqi.hazardous': 'അപകടകരം',
        
        # Weather
        'weather.temperature': 'താപനില',
        'weather.humidity': 'ഈര്‍പ്പം',
        'weather.wind': 'കാറ്റിന്റെ വേഗത',
        'weather.pressure': 'സമ്മര്‍ദം',
        
        # Health
        'health.mask': 'മാസ്ക് ആവശ്യമാണ്',
        'health.exercise': 'പുറത്ത് വ്യായാമം',
        'health.purifier': 'വായു ശുദ്ധികരണ യന്ത്രം',
        'health.yes': 'അതെ',
        'health.no': 'ഇല്ല',
        'health.limited': 'പരിമിതമായ',
        'health.avoid': 'ഒഴിവാക്കുക',
        'health.allowed': 'അനുവദിച്ചിരിക്കുന്നത്',
        
        # Alert
        'alert.normal': 'വായു ഗുണം നല്ലതാണ്',
        'alert.good': 'വായു ഗുണം നല്ലതാണ്',
        
        # Stats
        'stats.updates': 'ഇന്നത്തെ അപ്ഡേറ്റുകള്‍',
        'stats.alerts': 'ഇന്നത്തെ മുന്നറിയിപ്പുകള്‍',
        'stats.avg_aqi': 'ശരാശരി AQI',
        'stats.data_points': 'ഡാറ്റാ പോയിന്റുകള്‍',
    }

    # Telugu (తెలుగు)
    TRANSLATIONS['te'] = {
        # Navigation
        'nav.home': 'హోం',
        'nav.dashboard': 'डैशबोर्ड్',
        'nav.login': 'लాగిన్',
        'nav.logout': 'लాగౌట్',
        'nav.profile': 'प्रोफाइल',
        
        # Dashboard
        'dashboard.title': 'डैशबोर्ड్',
        'dashboard.current_aqi': 'Current Air Quality',
        'dashboard.prediction': 'AI Prediction',
        'dashboard.weather': 'Weather',
        'dashboard.pollution_map': 'Live Map',
        
        # AQI Categories
        'aqi.good': 'Good',
        'aqi.moderate': 'Moderate',
        'aqi.unhealthy_sensitive': 'Sensitive',
        'aqi.unhealthy': 'Unhealthy',
        'aqi.very_unhealthy': 'Very Unhealthy',
        'aqi.hazardous': 'Hazardous',
        
        # Health
        'health.yes': 'Yes',
        'health.no': 'No',
        'health.limited': 'Limited',
        'health.avoid': 'Avoid',
        'health.allowed': 'Allowed',
        
        # Common
        'common.loading': 'Loading...',
        'common.error': 'Error',
        'common.success': 'Success',
    }


def get_current_language():
    """Get the current language from session or request"""
    return session.get('language', 'en')


def set_language(lang):
    """Set the current language in session"""
    if lang in TRANSLATIONS:
        session['language'] = lang
        return True
    return False


def t(key, lang=None):
    """
    Translate a key to the current language
    Usage: t('nav.home') -> 'Home' or 'होम' or 'முகப்பு'
    """
    if lang is None:
        lang = get_current_language()
    
    # Fallback to English if language not found
    if lang not in TRANSLATIONS:
        lang = 'en'
    
    # Get translation or return key if not found
    return TRANSLATIONS.get(lang, {}).get(key, TRANSLATIONS.get('en', {}).get(key, key))


def get_language_list():
    """Get list of available languages"""
    return [
        {'code': 'en', 'name': 'English', 'native': 'English', 'flag': '🇺🇸'},
        {'code': 'hi', 'name': 'Hindi', 'native': 'हिंदी', 'flag': '🇮🇳'},
        {'code': 'ta', 'name': 'Tamil', 'native': 'தமிழ்', 'flag': '🇮🇳'},
        {'code': 'ml', 'name': 'Malayalam', 'native': 'മലയാളം', 'flag': '🇮🇳'},
        {'code': 'te', 'name': 'Telugu', 'native': 'తెలుగు', 'flag': '🇮🇳'},
    ]


def get_voice_language_code(lang):
    """Get the Web Speech API language code for a given language"""
    voice_codes = {
        'en': 'en-US',
        'hi': 'hi-IN',
        'ta': 'ta-IN',
        'te': 'te-IN',
    }
    return voice_codes.get(lang, 'en-US')


# Initialize translations on module load
load_translations()
