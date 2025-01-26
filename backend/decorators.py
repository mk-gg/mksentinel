import os
from functools import wraps
from flask import request, jsonify
from flask_login import current_user

def verify_api_key():
    """Check if the provided API key is valid."""
    api_key = request.headers.get('X-API-Key')
    return api_key == os.environ.get('API_KEY_SENTINEL')

def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # API key takes precedence
        if verify_api_key():
            return f(*args, **kwargs)
            
        # Otherwise, require OAuth login
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
            
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # API key takes precedence
        if verify_api_key():
            return f(*args, **kwargs)
            
        # Otherwise, require admin OAuth login
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        if not current_user.is_admin:
            return jsonify({"error": "Admin access required"}), 403
            
        return f(*args, **kwargs)
    return decorated_function