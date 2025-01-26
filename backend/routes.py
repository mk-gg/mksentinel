import datetime
import os
import secrets
from psycopg2 import IntegrityError
import requests
from urllib.parse import urlencode
from flask import abort, current_app, flash, jsonify, redirect, request, send_from_directory, session, url_for
from flask_login import current_user, login_user, logout_user

from decorators import auth_required, admin_required
from models import db, User, Member, Server, Bans

def init_routes(app):
    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, "index.html")

    @app.route('/test')
    def test():
        return jsonify({"message": "Hello, World!"})
    
    @app.route('/current_user')
    def get_current_user():
        if current_user.is_authenticated:
            return jsonify({
                'user': {
                    'id': current_user.id,
                    'username': current_user.username,
                    'email': current_user.email,
                    'is_admin': current_user.is_admin
                }
            })
        return jsonify({'user': None}), 401
    
    @app.route('/logout')
    def logout():
        logout_user()
        return jsonify({"status": "success"})
    
    @app.route('/authorize/<provider>')
    def oauth2_authorize(provider):
        if not current_user.is_anonymous:
            return redirect(url_for('index'))

        provider_data = current_app.config['OAUTH2_PROVIDERS'].get(provider)
        if provider_data is None:
            abort(404)

        # generate a random string for the state parameter
        session['oauth2_state'] = secrets.token_urlsafe(16)

        # create a query string with all the OAuth2 parameters
        qs = urlencode({
            'client_id': provider_data['client_id'],
            'redirect_uri': url_for('oauth2_callback', provider=provider, _external=True, _scheme='https'),
            'response_type': 'code',
            'scope': ' '.join(provider_data['scopes']),
            'state': session['oauth2_state'],
        })

        # redirect the user to the OAuth2 provider authorization URL
        return redirect(provider_data['authorize_url'] + '?' + qs)

    @app.route('/callback/<provider>')
    def oauth2_callback(provider):
        if not current_user.is_anonymous:
            return redirect(url_for('index'))

        provider_data = current_app.config['OAUTH2_PROVIDERS'].get(provider)
        if provider_data is None:
            abort(404)

        # if there was an authentication error, flash the error messages and exit
        if 'error' in request.args:
            for k, v in request.args.items():
                if k.startswith('error'):
                    flash(f'{k}: {v}')
            return redirect(url_for('index'))

        # make sure that the state parameter matches the one we created in the
        # authorization request
        if request.args['state'] != session.get('oauth2_state'):
            abort(401)

        # make sure that the authorization code is present
        if 'code' not in request.args:
            abort(401)

        # exchange the authorization code for an access token
        response = requests.post(provider_data['token_url'], data={
            'client_id': provider_data['client_id'],
            'client_secret': provider_data['client_secret'],
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': url_for('oauth2_callback', provider=provider, _external=True, _scheme='https')
        }, headers={'Accept': 'application/json'})
        if response.status_code != 200:
            abort(401)
        oauth2_token = response.json().get('access_token')
        if not oauth2_token:
            abort(401)

        # use the access token to get the user's email address
        response = requests.get(provider_data['userinfo']['url'], headers={
            'Authorization': 'Bearer ' + oauth2_token,
            'Accept': 'application/json',
        })
        if response.status_code != 200:
            abort(401)
        email = provider_data['userinfo']['email'](response.json())

        # find or create the user in the database
        user = db.session.scalar(db.select(User).where(User.email == email))
        if user is None:
            user = User(email=email, username=email.split('@')[0], is_admin=email in current_app.config['ADMIN_EMAILS'])
            db.session.add(user)
            db.session.commit()

        # log the user in
        login_user(user)
        return redirect(url_for('index'))
    
    # For getting the members
    @app.route('/members', methods=['GET'])
    @auth_required
    def get_members():
        members = Member.query.all()
        result = [member.to_json() for member in members]
        return jsonify(result)

    @app.route('/ban/<int:ban_id>', methods=['GET'])
    @auth_required
    def get_ban(ban_id):
        try:
            ban = Bans.query.get(ban_id)
            if not ban:
                return jsonify({'error': 'Ban not found'}), 404
                
            return jsonify(ban.to_json()), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    # Route for banning
    @app.route('/ban', methods=['POST'])
    @admin_required
    def create_ban():
        try:
            data = request.get_json()

            # Check if the member does exist
            # If not, create a new member
            member = Member.query.filter_by(member_id=data['memberId']).first()
            if not member:
                member = Member(
                    member_id = data['memberId'],
                    username = data['username'],
                    display_name = data['displayName']
                )
                db.session.add(member)
            
            # Check if server exists or create it
            server = Server.query.filter_by(server_id=data['serverId']).first()
            if not server:
                server = Server(
                    server_id=data['serverId'],
                    server_name=data['serverName']
                )
                db.session.add(server)
            
            # Create new ban
            new_ban = Bans(
                member_id = data['memberId'],
                server_id = data['serverId'],
                reason = data.get('reason'),
                captured_message = data['capturedMessage'],
                created_at = datetime.utcnow()
            )

            db.session.add(new_ban)
            db.session.commit()

            return jsonify({
                'message': 'Ban created successfully',
                'ban': new_ban.to_json()
            }), 201
        except IntegrityError:
            db.sesssion.rollback()
            return jsonify({'error': 'Ban already exists'}), 409

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400