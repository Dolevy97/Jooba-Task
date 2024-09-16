from flask import Blueprint, request, jsonify
from firebase_admin import auth, db
import uuid
from datetime import datetime

routes = Blueprint('routes', __name__)

@routes.route('/')
def home():
    return "<h1>Welcome to my product page!</h1>"


@routes.route('/upload_product', methods=['POST'])
def upload_product():
    data = request.get_json()
    id_token = data.get('idToken')
    product = data.get('product')
    
    if not id_token or not product:
        return jsonify({'message': 'ID Token and product data are required'}), 400
    
    try:
        # First, lets check the ID token to see if the user is authenticated
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        
        # Now, we go to the realtime DB to reference the user's products
        ref = db.reference(f'users/{uid}/products')
        
        current_products = ref.get()
        # Now lets check if our sample product is there, and if so we delete it
        
        if current_products:
            updated_products = {k: v for k, v in current_products.items() if v['name'] != 'Sample Product'}
            ref.set(updated_products)
        
        # After all the checks and methods, now we can add the products
        
        product_id = str(uuid.uuid4()) # Generate a unique ID
        new_product = {
            'name': product.get('name'),
            'price': product.get('price'),
            'category': product.get('category'),
            'description': product.get('description'),
            'created_at': datetime.utcnow().isoformat()
        }
        
        ref.child(product_id).set(new_product)
        return jsonify({'message': 'Product added successfully!', 'product_id': product_id}), 201

    except auth.InvalidIdTokenError:
        return jsonify({'message': 'Invalid ID Token'}), 401

    except Exception as e:
        return jsonify({'message': f'Failed to add product: {str(e)}'}), 500