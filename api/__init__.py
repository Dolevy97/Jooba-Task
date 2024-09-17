from flask import Flask
from firebase_admin import credentials, initialize_app

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'DoliJooba' # In production - this will be hidden as an env var
    
    cred = credentials.Certificate("key.json")
    initialize_app(cred, {
        'databaseURL': 'https://jooba-756d9-default-rtdb.firebaseio.com/'
    })
    
    from .routes import user, auth, product
    app.register_blueprint(user.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(product.bp)
    
    return app