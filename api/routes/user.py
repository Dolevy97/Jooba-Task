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
        
        user_products = []
        if isinstance(products, dict):
            user_products = [
                p for p in products.values()
                if p.get('created_by') == email
            ]
        else:
            user_products = []
        
        return jsonify({'products': user_products}), 200
    except auth.InvalidIdTokenError:
        return jsonify({'message': 'Invalid ID Token'}), 401

    except Exception as e:
        return jsonify({'message': f'Failed to get products: {str(e)}'}), 500

