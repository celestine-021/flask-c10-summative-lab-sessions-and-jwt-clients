from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
import os

try:
    from flask_cors import CORS
except ImportError:
    CORS = None

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_SORT_KEYS'] = False
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    
    # Enable CORS if available
    if CORS:
        CORS(app, 
             origins=['http://localhost:3000', 'http://localhost:5555', 'http://127.0.0.1:3000', 'http://127.0.0.1:5555'],
             supports_credentials=True,
             allow_headers=['Content-Type', 'Authorization'],
             methods=['GET', 'POST', 'PATCH', 'DELETE', 'OPTIONS'])
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.resources import resources_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(resources_bp)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app
