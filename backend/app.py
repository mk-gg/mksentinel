import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS

load_dotenv()

db = SQLAlchemy()
login = LoginManager()

def create_app():
    app = Flask(__name__)

    # CORS(app, supports_credentials=True, origins=[
    #     "http://localhost:5173"
    # ])

    CORS(app, 
         supports_credentials=True, 
         origins=[os.environ.get('FRONTEND_URL', 'http://localhost:5173')])
    
    app.config['SECRET_KEY'] = 'top secret!'

    # Database configuration
    postgres_url = os.environ.get('POSTGRES_URL')
    if postgres_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:VOoLSxZeDkFRymUs@db.cpeyxarnnshkhhjfffsp.supabase.co:5432/postgres'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres.cpeyxarnnshkhhjfffsp:VOoLSxZeDkFRymUs@aws-0-us-west-1.pooler.supabase.com:6543/postgres'

    # OAuth configuration
    app.config['OAUTH2_PROVIDERS'] = {
        'google': {
            'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
            'client_secret': os.environ.get('GOOGLE_CLIENT_SECRET'),
            'authorize_url': 'https://accounts.google.com/o/oauth2/auth',
            'token_url': 'https://accounts.google.com/o/oauth2/token',
            'userinfo': {
                'url': 'https://www.googleapis.com/oauth2/v3/userinfo',
                'email': lambda json: json['email'],
            },
            'scopes': ['https://www.googleapis.com/auth/userinfo.email'],
        },
        'github': {
            'client_id': os.environ.get('GITHUB_CLIENT_ID'),
            'client_secret': os.environ.get('GITHUB_CLIENT_SECRET'),
            'authorize_url': 'https://github.com/login/oauth/authorize',
            'token_url': 'https://github.com/login/oauth/access_token',
            'userinfo': {
                'url': 'https://api.github.com/user/emails',
                'email': lambda json: json[0]['email'],
            },
            'scopes': ['user:email'],
        },
    }
    app.config['ADMIN_EMAILS'] = os.environ.get('ADMIN_EMAILS', '').split(',')
    app.config['FRONTEND_URL'] = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
    app.config.update(
        SESSION_COOKIE_SECURE=False, # For https
        SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_HTTPONLY=True
    )
    # Initialize extensions
    db.init_app(app)
    login.init_app(app)

    # login.login_view = 'main.index'

    # Register blueprints
    from routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # Create database tables
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)