"""
Authentication module for E-Commerce application
Handles user registration, login, JWT tokens, and password hashing
"""
import jwt
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from config import Config
import uuid
import logging

logger = logging.getLogger(__name__)


class AuthManager:
    """Manages authentication and JWT tokens"""
    
    @staticmethod
    def hash_password(password):
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password, hashed_password):
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    @staticmethod
    def generate_token(user_id, email):
        """Generate JWT token for authenticated user"""
        expiry = datetime.utcnow() + timedelta(hours=Config.JWT_EXPIRY_HOURS)
        
        payload = {
            'user_id': user_id,
            'email': email,
            'exp': expiry,
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')
        return token
    
    @staticmethod
    def decode_token(token):
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    def generate_user_id():
        """Generate unique user ID"""
        return f"USER-{uuid.uuid4().hex[:12].upper()}"


def token_required(f):
    """Decorator to protect routes that require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid authorization header format'
                }), 401
        
        if not token:
            return jsonify({
                'success': False,
                'error': 'Authentication token is missing'
            }), 401
        
        # Decode and validate token
        payload = AuthManager.decode_token(token)
        
        if not payload:
            return jsonify({
                'success': False,
                'error': 'Invalid or expired token'
            }), 401
        
        # Pass user info to the route
        return f(current_user=payload, *args, **kwargs)
    
    return decorated


def optional_token(f):
    """Decorator for routes where auth is optional"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        current_user = None
        
        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
                payload = AuthManager.decode_token(token)
                if payload:
                    current_user = payload
            except (IndexError, Exception):
                pass
        
        return f(current_user=current_user, *args, **kwargs)
    
    return decorated


def validate_email(email):
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    return True, "Password is valid"
