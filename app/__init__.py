from flask import Flask
from flask_socketio import SocketIO
from flask_session import Session
from app.config import Config
import logging
import os

socketio = SocketIO(cors_allowed_origins="*")
sess = Session()

def create_app():
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    app.config.from_object(Config)
    
    # Configure Flask-Session for persistent chat sessions
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_KEY_PREFIX'] = 'airpollutionai:'
    app.config['SECRET_KEY'] = app.config.get('SECRET_KEY', 'airpollutionai-secret-key-2024')
    
    # Initialize Flask-Session
    sess.init_app(app)
    
    # Configure SQLite database
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, '..', 'data', 'airpollution.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    from app.models import db
    db.init_app(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        # Create default admin user if not exists
        from app.models import User
        from werkzeug.security import generate_password_hash
        
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                password_hash=generate_password_hash('password'),
                email='admin@airpollutionai.com'
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Default admin user created (admin/password)")
        else:
            print("✅ Admin user already exists")
    
    # Import routes and register them with the app
    from app.routes import register_routes
    register_routes(app)
    
    # Import and register chatbot blueprint
    from app.chatbot import chatbot_bp
    app.register_blueprint(chatbot_bp)
    
    # Import socket events
    from app import socket_events
    
    socketio.init_app(app)
    
    # Start scheduler
    from app.scheduler import start_scheduler
    start_scheduler(app)
    
    logging.info("✅ App created successfully with database")
    return app
