import os
from functools import wraps
from flask import request, jsonify
from flask_login import current_user

def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for API key first
        api_key = request.headers.get('X-API-Key')
        if api_key == os.environ.get('API_KEY'):
            return f(*args, **kwargs)
            
        # If no API key, check for OAuth login
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
            
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for API key first
        api_key = request.headers.get('X-API-Key')
        if api_key == os.environ.get('API_KEY'):
            return f(*args, **kwargs)
            
        # If no API key, check for OAuth admin
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        if not current_user.is_admin:
            return jsonify({"error": "Admin access required"}), 403
            
        return f(*args, **kwargs)
    return decorated_function