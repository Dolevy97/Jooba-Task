from flask import Flask
import firebase_admin
from firebase_admin import credentials

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'DoliJooba' # In production - this will be hidden
    
    # Firebase setup
    cred = credentials.Certificate("firebase-key.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://jooba-756d9-default-rtdb.firebaseio.com/'
    })
    
    # Register Blueprints
    from .routes import routes
    from .auth import auth_blueprint as auth
    app.register_blueprint(routes, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    
    return app