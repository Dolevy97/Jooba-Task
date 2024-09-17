from flask import Blueprint, request, jsonify
from firebase_admin import auth, db

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    id_token = data.get('idToken')
    
    if not id_token:
        return jsonify({'message': 'ID Token is required'})
    try:        
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        user = auth.get_user(uid)
        email = user.email
        
        ref = db.reference('products')
        all_products = ref.get()
        
        if all_products:
            user_products = [p for p in all_products if p.get('created_by') == email]
        else:
            user_products = []
            
        user_data = {
            'email': email,
            'products': user_products
        }
        return jsonify({'message': 'Login successful!', 'user': user_data}), 200
    
    except auth.InvalidIdTokenError:
        return jsonify({'message': 'Invalid ID token'}), 401

    except Exception as e:
        return jsonify({'message': f'Login failed: {str(e)}'}), 500

@bp.route('/logout', methods=['POST'])
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

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    try:
        user = auth.create_user(
            email=email,
            password=password
        )
        
        custom_token = auth.create_custom_token(user.uid)
        user_info = auth.get_user(user.uid)
        
        user_data = {
            'uid': user.uid,
            'email': user_info.email,
            'products': []
        }

        return jsonify({
            'message': 'User registered and logged in successfully!',
            'user': user_data,
            'customToken': custom_token.decode('utf-8'),
            'expiresIn': 3600
        }), 201
    except Exception as e:
        print(f"Unexpected error during registration:")
        return jsonify({'message': f'Registration failed: {str(e)}'}), 500