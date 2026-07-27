from flask import Blueprint, request, jsonify, session
from app import db, bcrypt
from app.models import User
from sqlalchemy.exc import IntegrityError

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/signup', methods=['POST'])
def signup():
    """Register a new user and set session"""
    try:
        data = request.get_json()
        
        # Validate input
        if not data or not all(k in data for k in ('username', 'password', 'password_confirmation')):
            return jsonify({'errors': ['Username, password, and password confirmation are required']}), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        password_confirmation = data.get('password_confirmation', '')
        
        # Validate username
        if len(username) < 3:
            return jsonify({'errors': ['Username must be at least 3 characters']}), 400
        
        # Validate password
        if len(password) < 6:
            return jsonify({'errors': ['Password must be at least 6 characters']}), 400
        
        if password != password_confirmation:
            return jsonify({'errors': ['Passwords do not match']}), 400
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            return jsonify({'errors': ['Username already exists']}), 422
        
        # Create new user
        user = User(username=username)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Set session
        session['user_id'] = user.id
        
        return jsonify(user.to_dict()), 201
    
    except IntegrityError:
        db.session.rollback()
        return jsonify({'errors': ['Username already exists']}), 422
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and set session"""
    try:
        data = request.get_json()
        
        # Validate input
        if not data or not all(k in data for k in ('username', 'password')):
            return jsonify({'errors': ['Username and password are required']}), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        # Find user
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            return jsonify({'errors': ['Invalid username or password']}), 401
        
        # Set session
        session['user_id'] = user.id
        
        return jsonify(user.to_dict()), 200
    
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@auth_bp.route('/check_session', methods=['GET'])
def check_session():
    """Check if user is logged in"""
    try:
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({}), 200
        
        user = User.query.get(user_id)
        
        if not user:
            session.pop('user_id', None)
            return jsonify({}), 200
        
        return jsonify(user.to_dict()), 200
    
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@auth_bp.route('/logout', methods=['DELETE'])
def logout():
    """End user session"""
    try:
        session.pop('user_id', None)
        return jsonify({}), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500
