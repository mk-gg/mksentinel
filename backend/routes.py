import secrets
from urllib.parse import urlencode
from flask import Blueprint, redirect, url_for, session, current_app, request, abort, jsonify
from flask_login import login_user, logout_user, current_user
import requests
from models import User
from app import db, login

api_bp = Blueprint('api', __name__)

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

@api_bp.route('/user')
def get_user():
    if current_user.is_authenticated:
        return jsonify({
            'status': 'success',
            'data': {
                'id': current_user.id,
                'username': current_user.username,
                'email': current_user.email,
                'is_admin': current_user.is_admin,
            }
        })
    return jsonify({
        'status': 'error',
        'message': 'Not authenticated'
    })

@api_bp.route('/test')
def test():
    return jsonify({
        'status': 'success',
        'message': 'Flask server is running'
    })

@api_bp.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
        return jsonify({
            'status': 'success',
            'message': 'Logged out successfully'
        })
    return jsonify({
        'status': 'error',
        'message': 'No user to logout'
    })

@api_bp.route('/authorize/<provider>')
def oauth2_authorize(provider):
    try:
        if not current_user.is_anonymous:
            return jsonify({
                'status': 'error',
                'message': 'Already authenticated'
            })

        provider_data = current_app.config['OAUTH2_PROVIDERS'].get(provider)
        if provider_data is None:
            return jsonify({
                'status': 'error',
                'message': f'Unknown provider: {provider}'
            }), 404

        session['oauth2_state'] = secrets.token_urlsafe(16)

        qs = urlencode({
            'client_id': provider_data['client_id'],
            'redirect_uri': url_for('api.oauth2_callback', provider=provider, _external=True),
            'response_type': 'code',
            'scope': ' '.join(provider_data['scopes']),
            'state': session['oauth2_state'],
        })

        return jsonify({
            'status': 'success',
            'data': {
                'authUrl': provider_data['authorize_url'] + '?' + qs
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_bp.route('/callback/<provider>')
def oauth2_callback(provider):
    try:
        if not current_user.is_anonymous:
            return jsonify({
                'status': 'error',
                'message': 'Already authenticated'
            })

        provider_data = current_app.config['OAUTH2_PROVIDERS'].get(provider)
        if provider_data is None:
            return jsonify({
                'status': 'error',
                'message': f'Unknown provider: {provider}'
            }), 404

        if 'error' in request.args:
            return jsonify({
                'status': 'error',
                'message': request.args['error']
            }), 400

        if request.args.get('state') != session.get('oauth2_state'):
            return jsonify({
                'status': 'error',
                'message': 'Invalid state parameter'
            }), 401

        if 'code' not in request.args:
            return jsonify({
                'status': 'error',
                'message': 'No code parameter'
            }), 401

        # Exchange authorization code for access token
        response = requests.post(provider_data['token_url'], data={
            'client_id': provider_data['client_id'],
            'client_secret': provider_data['client_secret'],
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': url_for('api.oauth2_callback', provider=provider, _external=True),
        }, headers={'Accept': 'application/json'})

        if response.status_code != 200:
            return jsonify({
                'status': 'error',
                'message': 'Failed to get access token'
            }), 401

        oauth2_token = response.json().get('access_token')
        if not oauth2_token:
            return jsonify({
                'status': 'error',
                'message': 'No access token received'
            }), 401

        # Get user info
        response = requests.get(provider_data['userinfo']['url'], headers={
            'Authorization': 'Bearer ' + oauth2_token,
            'Accept': 'application/json',
        })

        if response.status_code != 200:
            return jsonify({
                'status': 'error',
                'message': 'Failed to get user info'
            }), 401

        email = provider_data['userinfo']['email'](response.json())

        # Create or get user
        user = db.session.scalar(db.select(User).where(User.email == email))
        if user is None:
            user = User(
                email=email, 
                username=email.split('@')[0],
                is_admin=email in current_app.config['ADMIN_EMAILS']
            )
            db.session.add(user)
            db.session.commit()

        login_user(user)
        return redirect(current_app.config['FRONTEND_URL'])
       

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500