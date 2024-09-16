from flask import Blueprint, request, jsonify, current_app
from firebase_admin import auth, db

auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    id_token = data.get('idToken')
    
    if not id_token:
        return jsonify({'message': 'ID Token is missing'})
    try:
        # Verify the ID token using firebase admin SDK
        
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        
        # Get the data (products list) from the DB
        ref = db.reference(f'users/{uid}')
        user_data = ref.get()
        
        return jsonify({'message': 'Login successful!', 'user': user_data}), 200
    
    except auth.InvalidIdTokenError:
        return jsonify({'message': 'Invalid ID token'}), 401

    except Exception as e:
        return jsonify({'message': f'Login failed: {str(e)}'}), 500

@auth_blueprint.route('/logout', methods=['POST'])
def logout():
    data = request.get_json()
    id_token = data.get('idToken')
    if not id_token:
        return jsonify({'message': 'ID token is required for logout'}), 400
    
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        
        auth.revoke_refresh_tokens(uid)
        
        return jsonify({'message': 'Logout successful, tokens revoked'}), 200
    
    except Exception as e:
        return jsonify({'message': f'Logout failed: {str(e)}'}), 500

@auth_blueprint.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    try:
        # Here, I create a new user with Firebase Auth
        user = auth.create_user(
            email=email,
            password=password
        )
        
        # and here, I create a new entry in the Realtime Database to save the email and the products
        ref = db.reference('users')
        user_ref = ref.child(user.uid)
        user_data = {
            'email': email,
            'products': [{"name": "Sample Product", "price": 0, "category": "Test" , "description": "This is a sample product"}]
        }
        user_ref.set(user_data)
        return jsonify({'message': 'User registered successfully!', 'uid': user.uid}), 201
    except Exception as e:
        print(f"Unexpected error during registration:")
        return jsonify({'message': f'Registration failed: {str(e)}'}), 500