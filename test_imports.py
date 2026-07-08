print("=" * 50)
print("🔍 Testing AirPollutionAI Imports")
print("=" * 50)

packages_to_test = [
    ('flask', 'Flask'),
    ('flask_socketio', 'SocketIO'),
    ('requests', 'requests'),
    ('numpy', 'np'),
    ('pandas', 'pd'),
    ('sklearn', 'sklearn'),
    ('joblib', 'joblib'),
    ('apscheduler', 'scheduler'),
    ('folium', 'folium'),
    ('geopy', 'geopy'),
    ('dotenv', 'dotenv'),
    ('openrouteservice', 'ors'),
    ('networkx', 'nx'),
    ('osmnx', 'ox'),
]

for package, alias in packages_to_test:
    try:
        if package == 'osmnx':
            import osmnx as ox
            print(f"✅ {package:15} - version: {ox.__version__}")
        elif package == 'networkx':
            import networkx as nx
            print(f"✅ {package:15} - version: {nx.__version__}")
        elif package == 'sklearn':
            import sklearn
            print(f"✅ {package:15} - version: {sklearn.__version__}")
        elif package == 'dotenv':
            from dotenv import load_dotenv
            print(f"✅ {package:15} - found")
        else:
            module = __import__(package)
            print(f"✅ {package:15} - found")
    except ImportError as e:
        print(f"❌ {package:15} - missing: {e}")

print("=" * 50)