import os
from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager

from models import db
from routes import init_routes
from dotenv import load_dotenv

load_dotenv()



app = Flask(__name__, static_folder='static', static_url_path='/')
def create_app():
    # app = Flask(__name__, static_folder='static', static_url_path='/')

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
            "max_age": 3600
        }
    })

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'top secret!')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres.cpeyxarnnshkhhjfffsp:VOoLSxZeDkFRymUs@aws-0-us-west-1.pooler.supabase.com:6543/postgres')
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
    }
    app.config['ADMIN_EMAILS'] = os.environ.get('ADMIN_EMAILS', '').split(',')
    app.config['API_KEY_SENTINEL'] = os.environ.get('API_KEY_SENTINEL')
    app.config['SENTINEL_SECRET'] = os.environ.get('SENTINEL_SECRET')
    if not app.config['SENTINEL_SECRET']:
        print("Warning: SENTINEL_SECRET not found in environment")
        # Try loading from dotenv as fallback
        from dotenv import load_dotenv
        load_dotenv()
        app.config['SENTINEL_SECRET'] = os.getenv('SENTINEL_SECRET')

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
    
    with app.app_context():
        db.create_all()

    return app

# Create app for Vercel
application = create_app()

if __name__ == '__main__':
    # Optional: Create tables on startup (careful with this in production)

    application.run(debug=True)