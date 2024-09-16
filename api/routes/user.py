from flask import Blueprint, request, jsonify
from firebase_admin import auth, db

bp = Blueprint('user', __name__)
    
@bp.route('/user_products', methods=['GET'])
def user_products():
    data = request.get_json()
    id_token = data.get('idToken')

    if not id_token:
        return jsonify({'message': 'ID Token is required'}), 400
    
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        
        user = auth.get_user(uid)
        email = user.email
        
        ref = db.reference('products')
        products = ref.get()
        
        # Filtering to remove none or nulls due to placeholders
        if isinstance(products, list):
            user_products = [p for p in products if p.get('created_by') == email]
        else:
            user_products = []
        
        user_products = [p for p in user_products if p is not None]
        return jsonify({'products': user_products}), 200
    except auth.InvalidIdTokenError:
        return jsonify({'message': 'Invalid ID Token'}), 401

    except Exception as e:
        return jsonify({'message': f'Failed to get products: {str(e)}'}), 500

