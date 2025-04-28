from datetime import datetime, timedelta, timezone
import os
import secrets
from psycopg2 import IntegrityError
import requests
from urllib.parse import urlencode
from flask import abort, current_app, flash, jsonify, redirect, request, send_from_directory, session, url_for
from flask_login import current_user, login_user, logout_user
from sqlalchemy import func, text

from decorators import auth_required, admin_required
from models import db, User, Member, Server, Bans

from pusher_service import trigger_server_status, trigger_event, trigger_new_ban, trigger_ban_removed, trigger_ban_updated, trigger_stats_update
import psycopg2




def init_routes(app):
    @app.route('/')
    @app.route('/bans')
    @app.route('/login')
    def index():
        return send_from_directory(app.static_folder, "index.html")

    
    @app.route('/config-test')
    @admin_required
    def config_test():
        from os import environ
        return jsonify({
            "direct_sentinel_value": environ.get('SENTINEL_SECRET'),
            "config_sentinel_value": current_app.config.get('SENTINEL_SECRET'),
            "env_vars_starting_with_s": [k for k in environ.keys() if k.startswith('S')],
            "vercel_env": environ.get('VERCEL_ENV'),
            "is_production": environ.get('VERCEL_ENV') == 'production'
        })
    
    @app.route('/vercel-env-check')
    @admin_required
    def vercel_env_check():
        from os import environ
        all_keys = list(environ.keys())
        sensitive_keys = [k for k in all_keys if 'SECRET' in k or 'KEY' in k]
        return jsonify({
            "has_sentinel": 'SENTINEL_SECRET' in environ,
            "environment": environ.get('VERCEL_ENV'),
            "sensitive_keys_present": sensitive_keys,
            "deployment_url": environ.get('VERCEL_URL')
        })

    @app.route('/test')
    def test():
        return jsonify({"message": "Hello, World!,"})
    
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
    @app.route('/api/members', methods=['GET'])
    @auth_required
    def get_members():
        members = Member.query.all()
        result = [member.to_json() for member in members]
        return jsonify(result)
    
    # For getting the ban by id
    @app.route('/api/ban/<int:ban_id>', methods=['GET'])
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
    @app.route('/api/ban', methods=['POST'])
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
                db.session.commit()  # Explicitly commit the new server
            
            # Create new ban
            new_ban = Bans(
                member_id = data['memberId'],
                server_id = data['serverId'],
                reason = data.get('reason'),
                captured_message = data['capturedMessage'],
                created_at = datetime.now()
            )

            db.session.add(new_ban)
            db.session.commit()

            # Trigger Pusher event for real-time updates
            ban_json = new_ban.to_json()
            trigger_new_ban(ban_json)

            return jsonify({
                'message': 'Ban created successfully',
                'ban': ban_json
            }), 201
        except IntegrityError:
            db.sesssion.rollback()
            return jsonify({'error': 'Ban already exists'}), 409

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
        
    @app.route('/api/ban/<int:ban_id>', methods=['DELETE'])
    @admin_required
    def delete_ban(ban_id):
        try:
            ban = Bans.query.get(ban_id)
            if not ban:
                return jsonify({'error': 'Ban not found'}), 404
                
            db.session.delete(ban)
            db.session.commit()
            
            # Trigger Pusher event for real-time updates
            trigger_ban_removed(ban_id)
            
            return jsonify({'message': 'Ban deleted successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400


    @app.route('/api/ban/<int:ban_id>', methods=['PUT'])
    @admin_required
    def update_ban(ban_id):
        try:
            ban = Bans.query.get(ban_id)
            if not ban:
                return jsonify({'error': 'Ban not found'}), 404
                
            data = request.get_json()
            
            # Update only allowed fields
            if 'reason' in data:
                ban.reason = data['reason']
            if 'capturedMessage' in data:
                ban.captured_message = data['capturedMessage']
                
            db.session.commit()
            
            # Trigger Pusher event for real-time updates
            ban_json = ban.to_json()
            trigger_ban_updated(ban_json)
            
            return jsonify({
                'message': 'Ban updated successfully',
                'ban': ban_json
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

    @app.route('/api/bans', methods=['GET'])
    @auth_required
    def get_bans():
        try:
            server_id = request.args.get('server_id')
            member_id = request.args.get('member_id')
            
            query = Bans.query
            
            if server_id:
                query = query.filter_by(server_id=server_id)
            if member_id:
                query = query.filter_by(member_id=member_id)
                
            bans = query.all()
            return jsonify({
                'bans': [ban.to_json() for ban in bans]
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 400
        
    @app.route('/api/server/<int:server_id>/banned-members', methods=['GET'])
    @auth_required
    def get_banned_members(server_id):
        try:
            banned_members = db.session.query(Member, Bans)\
                .join(Bans, Member.member_id == Bans.member_id)\
                .filter(Bans.server_id == server_id)\
                .all()
            
            result = [{
                **member.to_json(),
                'ban_info': ban.to_json()
            } for member, ban in banned_members]
            
            return jsonify({
                'banned_members': result
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @app.route('/api/bans/statistics', methods=['GET'])
    @auth_required
    def get_ban_statistics():
        try:
            # Get current date in UTC
            current_date = datetime.now(timezone.utc)
            
            # Calculate the start of today, this month, and this year in UTC
            start_of_today = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
            start_of_month = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            start_of_year = current_date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Combine multiple queries into a single query for better performance
            stats = db.session.query(
                func.count(Bans.ban_id).label('total_bans'),
                func.count(case((Bans.created_at >= start_of_today, 1))).label('total_bans_today'),
                func.count(case((Bans.created_at >= start_of_month, 1))).label('total_bans_month'),
                func.count(case((Bans.created_at >= start_of_year, 1))).label('total_bans_year'),
                func.count(func.distinct(Bans.server_id)).label('total_servers'),
                func.count(func.distinct(Bans.member_id)).label('total_members')
            ).first()
            
            # Get monthly trend (last 6 months) in a separate query since it's more complex
            six_months_ago = current_date - timedelta(days=180)
            monthly_trend = db.session.query(
                func.date_trunc('month', Bans.created_at).label('month'),
                func.count(Bans.ban_id).label('count')
            ).filter(
                Bans.created_at >= six_months_ago
            ).group_by(
                'month'
            ).order_by('month').all()
            
            # Format monthly trend data with UTC dates
            monthly_trend_data = [
                {
                    'month': month.astimezone(timezone.utc).strftime('%Y-%m'),
                    'count': count
                }
                for month, count in monthly_trend
            ]
            
            stats_data = {
                'totalBans': stats.total_bans or 0,
                'totalBansToday': stats.total_bans_today or 0,
                'totalBansMonth': stats.total_bans_month or 0,
                'totalBansYear': stats.total_bans_year or 0,
                'totalServers': stats.total_servers or 0,
                'totalMembers': stats.total_members or 0,
                'monthlyTrend': monthly_trend_data,
                'currentServerTime': current_date.isoformat()
            }
            
            # Only trigger Pusher event if there are significant changes
            # This reduces unnecessary Pusher events
            if hasattr(current_app, 'last_stats'):
                last_stats = current_app.last_stats
                if (last_stats['totalBans'] != stats_data['totalBans'] or
                    last_stats['totalBansToday'] != stats_data['totalBansToday'] or
                    last_stats['totalBansMonth'] != stats_data['totalBansMonth']):
                    trigger_stats_update(stats_data)
            else:
                trigger_stats_update(stats_data)
            
            # Cache the current stats
            current_app.last_stats = stats_data
            
            return jsonify(stats_data), 200
                
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    



    @app.route('/api/status', methods=['GET'])
    def server_status():
        """API endpoint to check server status and trigger a Pusher event"""
        trigger_server_status()
        return jsonify({'status': 'online'})
    

    @app.route('/api/healthcheck', methods=['GET'])
    def health_check():
        """API endpoint to check system health and trigger a Pusher event"""
        
        # Initialize health data
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),  # Use datetime.now() directly
            'components': {
                'server': 'connected',
                'database': 'connected',
                # Add other components as needed
            }
        }
        
        # Check database connection
        try:
            # Use SQLAlchemy 2.0 compatible syntax
            with db.engine.connect() as connection:
                # Execute a simple query using proper syntax for SQLAlchemy 2.0
                connection.execute(text("SELECT 1")).scalar()
                # If we get here, the database is connected
                health_data['components']['database'] = 'connected'
        except Exception as e:
            print(f"Database health check failed: {e}")
            health_data['components']['database'] = 'disconnected'
            health_data['status'] = 'degraded'
        
        # Determine overall status based on component statuses
        if any(status == 'disconnected' for status in health_data['components'].values()):
            health_data['status'] = 'degraded'
            
        if all(status == 'disconnected' for status in health_data['components'].values()):
            health_data['status'] = 'unhealthy'
        
        # Trigger a Pusher event with the health status
        trigger_event('sentinel-status', 'health-update', health_data)
        
        return jsonify(health_data)
    
    # Handles the routes for static files
    # @app.route('/', defaults={'path': ''})
    # @app.route('/<path:path>')
    # def catch_all(path):
    #        # First check if this is one of our API endpoints
    #     try:
    #         # Try to dispatch to the matching route handler
    #         return app.dispatch_request()
    #     except:
    #         # If no matching route is found, serve the React app
    #         return send_from_directory(app.static_folder, 'index.html')
