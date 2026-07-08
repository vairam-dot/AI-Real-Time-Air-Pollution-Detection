"""AirPollutionAI Chatbot with real-time AQI/Weather + 50 Manual Q&A support."""
import os
import re
import requests
from flask import Blueprint, request, jsonify, session, current_app
from datetime import datetime

chatbot_bp = Blueprint('chatbot', __name__)

# Helper function to get config values
def get_config(key, default=''):
    """Get configuration value from Config class"""
    try:
        from app.config import Config
        return getattr(Config, key, default)
    except:
        return default

# ============= 50 MANUAL QUESTIONS AND ANSWERS =============
QA_DATABASE = {
    # General Pollution Questions (1-10)
    "what is air pollution": "Air pollution is the presence of harmful substances in the air that can harm humans, animals, and the environment. These substances include gases, particles, and biological molecules.",
    
    "what causes air pollution": "Main causes of air pollution include: vehicle emissions, industrial factories, burning of fossil fuels, agricultural activities, dust from construction, and natural sources like wildfires.",
    
    "how does pollution affect health": "Air pollution can cause respiratory problems like asthma, bronchitis, lung cancer, heart disease, stroke, and can worsen existing health conditions. Children and elderly are most vulnerable.",
    
    "what is pm2.5": "PM2.5 refers to fine particulate matter that is 2.5 micrometers or smaller in diameter. These tiny particles can enter deep into your lungs and even bloodstream, causing serious health issues.",
    
    "what is pm10": "PM10 are inhalable particles with diameters 10 micrometers or smaller. They can penetrate the lungs and cause respiratory problems, but are larger than PM2.5.",
    
    "what is aqi": "AQI stands for Air Quality Index. It's a scale used to communicate how polluted the air currently is and what associated health effects might be a concern. It ranges from 0 (good) to 500 (hazardous).",
    
    "how to check aqi": "You can check AQI through: 1) Government websites like CPCB, 2) Apps like AirVisual or Safar, 3) Our AirPollutionAI dashboard, 4) Local news weather reports.",
    
    "best air purifier": "Top air purifier brands in India include: Philips, Dyson, Sharp, Mi, Honeywell, and Blueair. Look for HEPA filters, activated carbon, and CADR rating suitable for your room size.",
    
    "which mask is best for pollution": "N95 and N99 masks are best for protection against air pollution. They filter out at least 95% of airborne particles. Avoid surgical or cloth masks for pollution protection.",
    
    "does pollution cause cancer": "Yes, long-term exposure to air pollution is linked to lung cancer and may increase risk of bladder cancer. WHO classifies air pollution as Group 1 carcinogen.",
    
    # Indian City Specific (11-25)
    "aqi in delhi": "Delhi's AQI varies by season. In winter, it often ranges from 300-500 (Hazardous). In summer/monsoon, it's better at 100-200 (Moderate to Unhealthy). Check our dashboard for real-time data!",
    
    "delhi pollution reason": "Delhi's pollution comes from: vehicle emissions, stubble burning in Punjab/Haryana, industrial pollution, construction dust, and weather conditions like low wind speed in winter.",
    
    "mumbai air quality": "Mumbai generally has moderate AQI (100-200) due to coastal location. However, areas near industries may have worse air. Marine Drive and South Mumbai typically have better air.",
    
    "chennai air quality": "Chennai usually has good to moderate AQI (50-150) due to coastal winds. Summer tends to have more dust, while monsoon brings cleaner air.",
    
    "bangalore air quality": "Bangalore's AQI ranges from good to moderate (50-150). Traffic congestion in areas like Silk Board, MG Road can cause local hotspots of pollution.",
    
    "kolkata pollution": "Kolkata's AQI varies from moderate to unhealthy (100-250). Major sources: vehicle emissions, industry, and burning of biomass. Winter sees higher pollution due to temperature inversion.",
    
    "hyderabad air quality": "Hyderabad generally has moderate AQI (100-200). IT corridor and Hitec City areas have better air due to more greenery, while industrial areas have higher pollution.",
    
    "pune air quality": "Pune has moderate AQI (100-200) most of the year. Winter months see higher pollution. Katraj, Hadapsar industrial areas have poorer air quality.",
    
    "coimbatore pollution": "Coimbatore has good to moderate AQI (50-150). Being a textile hub, some industrial areas may have localized pollution, but overall air is cleaner than metro cities.",
    
    "sivakasi air quality": "Sivakasi, known for fireworks industry, has moderate AQI (100-200). During festival seasons, fireworks can temporarily spike pollution levels.",
    
    "madurai air quality": "Madurai has moderate AQI (100-200). Summer months see more dust, while air quality improves during monsoon. Old city areas with narrow streets may have higher vehicle pollution.",
    
    "ooty air quality": "Ooty, being a hill station, generally has good AQI (0-100). The cool climate and greenery help maintain clean air, making it a healthy getaway.",
    
    "kodaikanal air quality": "Kodaikanal has excellent air quality (0-100) due to its high altitude, forests, and low industrial activity. Perfect for those seeking clean air.",
    
    "kanyakumari air quality": "Kanyakumari has good AQI (50-100) due to coastal location and strong winds. The air is generally clean with sea breeze helping disperse pollutants.",
    
    "pondicherry air quality": "Pondicherry has good to moderate AQI (50-150). Coastal breeze keeps air relatively clean, though tourist season may see temporary increases.",
    
    # Health Advice (26-35)
    "when to wear mask": "Wear a mask when: 1) AQI above 150, 2) Near construction sites, 3) In heavy traffic, 4) If you have respiratory issues, 5) During crop burning season (Oct-Nov).",
    
    "can exercise in pollution": "Avoid outdoor exercise when AQI is above 150. Exercise indoors in air-conditioned spaces. If AQI is 100-150, exercise in early morning or after sunset when pollution is lower.",
    
    "pollution symptoms": "Common symptoms of pollution exposure: coughing, wheezing, shortness of breath, eye irritation, headache, fatigue, chest pain, and throat irritation.",
    
    "how to protect children": "Protect children by: keeping windows closed on high AQI days, using air purifiers, ensuring they wear masks outdoors, limiting outdoor play when AQI is high, and maintaining good nutrition.",
    
    "best plants for air purification": "NASA recommended plants: Areca Palm, Snake Plant, Peace Lily, Spider Plant, Aloe Vera, and Boston Fern. These remove toxins like formaldehyde and benzene.",
    
    "does air purifier help": "Yes, air purifiers with HEPA filters can remove up to 99.97% of airborne particles. They're especially helpful for people with allergies, asthma, or living in high-pollution areas.",
    
    "how to check room air quality": "You can check room air quality with: 1) Portable air quality monitors, 2) Smart home devices with AQI sensors, 3) Our mobile app with indoor recommendations.",
    
    "pollution during pregnancy": "Pregnant women should avoid high pollution areas as it may affect fetal development. Use masks, air purifiers, and consult doctor for precautions during high AQI days.",
    
    "asthma and pollution": "Pollution triggers asthma attacks. Keep rescue inhaler handy, check daily AQI, stay indoors on high pollution days, and use air purifiers at home.",
    
    "food to fight pollution": "Foods that help combat pollution effects: Vitamin C rich foods (oranges, amla), omega-3 (fish, walnuts), turmeric, green tea, jaggery, and foods high in antioxidants.",
    
    # Weather Related (36-40)
    "how weather affects pollution": "Weather greatly affects pollution: 1) Winter: Cold air traps pollution (inversion), 2) Rain: Cleans air, 3) Wind: Disperses pollutants, 4) Summer heat: Can create ground-level ozone.",
    
    "why winter more pollution": "Winter has more pollution due to: temperature inversion (cold air traps pollutants near ground), lower wind speed, more biomass burning for heating, and fog trapping particles.",
    
    "does rain reduce pollution": "Yes, rain 'washes' pollutants from the air (wet deposition). A good rainfall can reduce AQI by 30-50%, giving us clean, fresh air afterward.",
    
    "temperature and aqi": "Temperature affects AQI: High temperatures can increase ozone formation. Cold temperatures trap pollution. Moderate temperatures with good wind give the best air quality.",
    
    "humidity and pollution": "High humidity can increase particle formation (secondary aerosols). Low humidity with dry conditions can increase dust. Moderate humidity (40-60%) is best for air quality.",
    
    # Masks and Protection (41-45)
    "n95 vs n99 mask": "N95 filters 95% of particles, N99 filters 99%. N99 offers better protection but makes breathing slightly harder. N95 is sufficient for most daily use in cities.",
    
    "how long to use n95 mask": "N95 masks can be used for about 8 hours continuously or up to 3-5 days if stored properly. Discard if damp, dirty, or deformed. Don't wash reusable ones.",
    
    "can kids wear masks": "Yes, but only N95 masks designed for children (proper fit is crucial). Children under 2 should NOT wear masks. Supervise kids wearing masks and take breaks.",
    
    "mask for bike riding": "For bike riders, use N95 with exhalation valve for easier breathing. Some prefer pollution masks with activated carbon for additional protection from vehicle exhaust.",
    
    "surgical mask vs n95": "Surgical masks protect others from your droplets, N95 protects YOU from particles. For pollution, N95 is effective, surgical masks offer minimal protection.",
    
    # General Knowledge (46-50)
    "most polluted city in india": "According to recent data, Delhi, Ghaziabad, Patna, and Lucknow often top the list. But AQI varies by season - check our dashboard for current rankings!",
    
    "least polluted city in india": "Shillong, Aizawl, Mysore, Coimbatore, and many coastal cities like Chennai often have better air quality. Hill stations like Ooty and Kodaikanal also have clean air.",
    
    "india aqi standard": "India's National AQI standards: Good(0-50), Satisfactory(51-100), Moderate(101-200), Poor(201-300), Very Poor(301-400), Severe(401-500). CPCB sets these standards.",
    
    "who aqi guidelines": "WHO guidelines are stricter: Good(0-25), Moderate(25-50), Unhealthy for sensitive(50-75), Unhealthy(75-100), Very unhealthy(100+). India's standards allow higher pollution levels.",
    
    "history of air pollution": "Major air pollution disasters: 1952 London Smog (killed 12,000), 1948 Donora Smog (20 deaths). India's pollution crisis gained attention in 1990s with industrialization.",
}

# List of common questions for suggestions
QUICK_QUESTIONS = [
    "What is air pollution?",
    "How does pollution affect health?",
    "What is PM2.5?",
    "What is AQI?",
    "Best mask for pollution?",
    "AQI in Delhi?",
    "Mumbai air quality?",
    "Chennai pollution?",
    "Bangalore AQI?",
    "Coimbatore air quality?",
    "Why winter more pollution?",
    "Does rain reduce pollution?",
    "How to protect children?",
    "Best plants for purification?",
    "N95 vs N99 mask?",
    "Most polluted city in India?",
    "Least polluted city in India?",
    "Food to fight pollution?",
    "Can exercise in pollution?",
    "When to wear mask?",
]

# Indian cities with coordinates (keeping for real-time data)
INDIAN_CITIES = {
    'delhi': {'lat': 28.6139, 'lon': 77.2090, 'name': 'Delhi'},
    'new delhi': {'lat': 28.6139, 'lon': 77.2090, 'name': 'New Delhi'},
    'mumbai': {'lat': 19.0760, 'lon': 72.8777, 'name': 'Mumbai'},
    'bangalore': {'lat': 12.9716, 'lon': 77.5946, 'name': 'Bangalore'},
    'bengaluru': {'lat': 12.9716, 'lon': 77.5946, 'name': 'Bengaluru'},
    'chennai': {'lat': 13.0827, 'lon': 80.2707, 'name': 'Chennai'},
    'kolkata': {'lat': 22.5726, 'lon': 88.3639, 'name': 'Kolkata'},
    'hyderabad': {'lat': 17.3850, 'lon': 78.4867, 'name': 'Hyderabad'},
    'pune': {'lat': 18.5204, 'lon': 73.8567, 'name': 'Pune'},
    'ahmedabad': {'lat': 23.0225, 'lon': 72.5714, 'name': 'Ahmedabad'},
    'jaipur': {'lat': 26.9124, 'lon': 75.7873, 'name': 'Jaipur'},
    'lucknow': {'lat': 26.8467, 'lon': 80.9462, 'name': 'Lucknow'},
    'chandigarh': {'lat': 30.7333, 'lon': 76.7794, 'name': 'Chandigarh'},
    'coimbatore': {'lat': 11.0168, 'lon': 76.9558, 'name': 'Coimbatore'},
    'sivakasi': {'lat': 9.4745, 'lon': 77.7053, 'name': 'Sivakasi'},
    'madurai': {'lat': 9.9252, 'lon': 78.1198, 'name': 'Madurai'},
    'ooty': {'lat': 11.4102, 'lon': 76.6950, 'name': 'Ooty'},
    'kodaikanal': {'lat': 10.2381, 'lon': 77.4892, 'name': 'Kodaikanal'},
    'kanyakumari': {'lat': 8.0883, 'lon': 77.5385, 'name': 'Kanyakumari'},
    'pondicherry': {'lat': 11.9416, 'lon': 79.8083, 'name': 'Puducherry'},
}


def get_aqi_category(aqi):
    """Get AQI category and color"""
    if aqi <= 50:
        return {'text': 'Good', 'color': '🟢', 'desc': 'Air quality is satisfactory'}
    elif aqi <= 100:
        return {'text': 'Moderate', 'color': '🟡', 'desc': 'Acceptable for most'}
    elif aqi <= 150:
        return {'text': 'Unhealthy for Sensitive', 'color': '🟠', 'desc': 'Sensitive groups may experience effects'}
    elif aqi <= 200:
        return {'text': 'Unhealthy', 'color': '🔴', 'desc': 'Everyone may experience health effects'}
    elif aqi <= 300:
        return {'text': 'Very Unhealthy', 'color': '🟣', 'desc': 'Health warnings of emergency conditions'}
    else:
        return {'text': 'Hazardous', 'color': '⚫', 'desc': 'Emergency warning'}


def get_aqi_from_waqi(lat, lon):
    """Fetch real-time AQI from WAQI API"""
    try:
        waqi_api_key = get_config('WAQI_API_KEY', '')
        if not waqi_api_key:
            return None
        
        url = f"https://api.waqi.info/feed/geo:{lat};{lon}/?token={waqi_api_key}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'ok':
                return {
                    'aqi': data['data']['aqi'],
                    'city': data['data'].get('city', {}).get('name', 'Unknown'),
                    'dominant': data['data'].get('dominantpol', 'pm25'),
                    'pm25': data['data'].get('iaqi', {}).get('pm25', {}).get('v', None),
                    'pm10': data['data'].get('iaqi', {}).get('pm10', {}).get('v', None),
                    'o3': data['data'].get('iaqi', {}).get('o3', {}).get('v', None),
                    'no2': data['data'].get('iaqi', {}).get('no2', {}).get('v', None),
                    'so2': data['data'].get('iaqi', {}).get('so2', {}).get('v', None),
                    'co': data['data'].get('iaqi', {}).get('co', {}).get('v', None),
                    'time': data['data'].get('time', {}).get('s', '')
                }
    except Exception as e:
        print(f"WAQI API error: {e}")
    return None


def get_weather_from_openweather(lat, lon):
    """Fetch real-time weather from OpenWeather API"""
    try:
        weather_api_key = get_config('OPENWEATHER_API_KEY', '')
        if not weather_api_key:
            return None
        
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={weather_api_key}&units=metric"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'temperature': round(data['main']['temp'], 1),
                'feels_like': round(data['main']['feels_like'], 1),
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'wind_speed': round(data['wind']['speed'] * 3.6, 1),
                'wind_deg': data['wind'].get('deg', 0),
                'description': data['weather'][0]['description'],
                'icon': data['weather'][0]['icon'],
                'visibility': round(data.get('visibility', 10000) / 1000, 1),
                'clouds': data['clouds']['all'],
                'sunrise': data['sys']['sunrise'],
                'sunset': data['sys']['sunset']
            }
    except Exception as e:
        print(f"OpenWeather API error: {e}")
    return None


def extract_city_from_message(message):
    """Extract city name from user message"""
    message_lower = message.lower()
    
    for city_key, city_data in INDIAN_CITIES.items():
        if city_key in message_lower:
            return city_data
    
    return None


def format_aqi_response(aqi_data, weather_data, city_name):
    """Format AQI and weather data into a nice response"""
    aqi = aqi_data['aqi']
    category = get_aqi_category(aqi)
    
    response = f"📍 *Current Air Quality in {city_name}*\n\n"
    response += f"🧠 **AQI: {aqi}** ({category['text']})\n"
    response += f"{category['color']} {category['desc']}\n\n"
    
    response += "📊 *Pollutant Levels:*\n"
    if aqi_data.get('pm25'):
        response += f"• PM2.5: {aqi_data['pm25']} µg/m³\n"
    if aqi_data.get('pm10'):
        response += f"• PM10: {aqi_data['pm10']} µg/m³\n"
    if aqi_data.get('o3'):
        response += f"• O₃: {aqi_data['o3']} µg/m³\n"
    if aqi_data.get('no2'):
        response += f"• NO₂: {aqi_data['no2']} µg/m³\n"
    
    if weather_data:
        response += f"\n🌡️ *Weather:*\n"
        response += f"• Temperature: {weather_data['temperature']}°C\n"
        response += f"• Humidity: {weather_data['humidity']}%\n"
        response += f"• Wind: {weather_data['wind_speed']} km/h\n"
        response += f"• Condition: {weather_data['description'].title()}\n"
    
    response += f"\n💚 *Health Advice:*\n"
    if aqi <= 50:
        response += "✅ No precautions needed. Enjoy outdoor activities!"
    elif aqi <= 100:
        response += "⚠️ Sensitive individuals should limit prolonged outdoor exertion."
    elif aqi <= 150:
        response += "😷 Sensitive groups should wear masks outdoors."
    elif aqi <= 200:
        response += "⛔ Avoid outdoor exercise. Wear N95 mask if going out."
    else:
        response += "🚨 Stay indoors with air purifier on."
    
    return response


def find_best_match(user_message):
    """Find the best matching question from our database"""
    user_message = user_message.lower().strip()
    user_message = re.sub(r'[^\w\s]', '', user_message)  # Remove punctuation
    
    # Direct match
    if user_message in QA_DATABASE:
        return QA_DATABASE[user_message]
    
    # Check if message contains key phrases
    for question, answer in QA_DATABASE.items():
        # If user message contains the question or vice versa
        if question in user_message or user_message in question:
            return answer
        
        # Check for partial matches (split into words)
        question_words = set(question.split())
        user_words = set(user_message.split())
        common_words = question_words.intersection(user_words)
        
        # If they share at least 2 important words, consider a match
        if len(common_words) >= 2 and len(question_words) > 0:
            # Avoid very short matches like "is" "the"
            important_words = [w for w in common_words if len(w) > 3]
            if len(important_words) >= 1:
                return answer
    
    return None


def get_manual_response(user_message):
    """Get response from manual Q&A database"""
    
    # Special handling for greetings
    greetings = ['hi', 'hello', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening']
    if any(greet in user_message.lower() for greet in greetings):
        return "Hello! 👋 I'm AirPollutionAI Assistant. I can answer questions about air quality, pollution, health tips, and Indian cities. What would you like to know?"
    
    # Thank you responses
    thanks = ['thank', 'thanks', 'appreciate', 'grateful']
    if any(word in user_message.lower() for word in thanks):
        return "You're welcome! 😊 Feel free to ask me more questions about air quality, pollution, or Indian cities."
    
    # Help command
    if 'help' in user_message.lower() or 'what can you do' in user_message.lower():
        return (
            "I can help you with:\n\n"
            "🌍 **Real-time Data**: Ask about AQI in any Indian city\n"
            "   • 'AQI in Delhi?'\n"
            "   • 'Mumbai air quality?'\n"
            "   • 'Weather in Chennai?'\n\n"
            "📚 **50+ Manual Q&A**: Questions about pollution, health, masks\n"
            "   • 'What is PM2.5?'\n"
            "   • 'Best mask for pollution?'\n"
            "   • 'How to protect children?'\n\n"
            "🏥 **Health Advice**: Precautions and tips\n"
            "   • 'Can I exercise today?'\n"
            "   • 'Food to fight pollution?'\n\n"
            "Just ask me anything about air quality!"
        )
    
    # Try to find a match in our database
    answer = find_best_match(user_message)
    
    if answer:
        return answer
    
    # If no match found
    return (
        "I don't have a specific answer for that question yet. 😊\n\n"
        "Try asking one of these:\n"
        "• What is air pollution?\n"
        "• How does pollution affect health?\n"
        "• Best mask for pollution?\n"
        "• AQI in Delhi?\n"
        "• Weather in Mumbai?\n"
        "• What is PM2.5?\n"
        "• Does rain reduce pollution?\n\n"
        "Or check our dashboard for real-time AQI data!"
    )


@chatbot_bp.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint - processes user messages"""
    data = request.get_json()
    user_message = data.get('message', '').strip()
    chat_history = session.get('chat_history', [])
    
    if not user_message:
        return jsonify({'error': 'Message cannot be empty'}), 400
    
    response_text = None
    city_data = extract_city_from_message(user_message)
    
    # If asking about a specific city, try to get real-time data
    if city_data:
        aqi_data = get_aqi_from_waqi(city_data['lat'], city_data['lon'])
        weather_data = get_weather_from_openweather(city_data['lat'], city_data['lon'])
        
        if aqi_data:
            response_text = format_aqi_response(aqi_data, weather_data, city_data['name'])
        elif weather_data:
            response_text = f"🌤️ *Weather in {city_data['name']}*\n\n"
            response_text += f"Temperature: {weather_data['temperature']}°C\n"
            response_text += f"Humidity: {weather_data['humidity']}%\n"
            response_text += f"Condition: {weather_data['description'].title()}"
    
    # If no real-time data or not a city question, use manual Q&A
    if not response_text:
        response_text = get_manual_response(user_message)
    
    # Update chat history
    chat_history.append({"role": "user", "content": user_message})
    chat_history.append({"role": "assistant", "content": response_text})
    
    if len(chat_history) > 100:
        chat_history = chat_history[-100:]
    
    session['chat_history'] = chat_history
    
    return jsonify({
        'response': response_text,
        'timestamp': datetime.now().isoformat()
    })


@chatbot_bp.route('/api/chat/history', methods=['GET'])
def get_chat_history():
    """Get chat history for the current session"""
    chat_history = session.get('chat_history', [])
    return jsonify({
        'history': chat_history,
        'count': len(chat_history)
    })


@chatbot_bp.route('/api/chat/clear', methods=['POST'])
def clear_chat():
    """Clear chat history for the current session"""
    session['chat_history'] = []
    return jsonify({'success': True, 'message': 'Chat history cleared'})


@chatbot_bp.route('/api/chat/quick-questions', methods=['GET'])
def get_quick_questions():
    """Get quick question suggestions for the user"""
    return jsonify({'questions': QUICK_QUESTIONS})


@chatbot_bp.route('/api/chat/status', methods=['GET'])
def chat_status():
    """Check chatbot status"""
    waqi_key = bool(get_config('WAQI_API_KEY', ''))
    weather_key = bool(get_config('OPENWEATHER_API_KEY', ''))
    
    return jsonify({
        'configured': True,
        'waqi_api': waqi_key,
        'weather_api': weather_key,
        'real_time_data': waqi_key or weather_key,
        'manual_qa_count': len(QA_DATABASE),
        'mode': 'Manual Q&A + Real-time Data'
    })