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
    from .routes import user, auth, product
    app.register_blueprint(user.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(product.bp)
    
    return app