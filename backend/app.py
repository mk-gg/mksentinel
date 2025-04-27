import os
from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager

from models import db
from routes import init_routes
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='/')

    # CORS Configuration
    CORS(app, supports_credentials=True, resources={
        r"/*": {
            "origins": [
                "http://localhost:5173", 
                "http://localhost:5000", 
                "https://mksentinel.vercel.app"
            ],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "max_age": 3600  # Cache preflight request
        }
    })

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'top secret!')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///dev.db') 
    app.config['OAUTH2_PROVIDERS'] = {
        # Google OAuth Provider
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

        # Github OAuth Provider
        # Documentation:  https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps
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
    app.config['API_KEY_SENTINEL'] = os.environ.get('API_KEY_SENTINEL')
    app.config['SENTINEL_SECRET'] = os.environ.get('SENTINEL_SECRET')
    
    app.config['PUSHER_APP_ID'] = os.environ.get('PUSHER_APP_ID')
    app.config['PUSHER_KEY'] = os.environ.get('PUSHER_KEY')
    app.config['PUSHER_SECRET'] = os.environ.get('PUSHER_SECRET')
    app.config['PUSHER_CLUSTER'] = os.environ.get('PUSHER_CLUSTER') 

    # Security configurations
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    # Initialize extensions
    db.init_app(app)
    login = LoginManager(app)
    login.login_view = 'index'

    # Import User model for user loader
    from models import User

    @login.user_loader
    def load_user(id):
        return db.session.get(User, int(id))

    # Initialize routes
    init_routes(app)

    return app

# Create app and database tables
app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)