from flask import Blueprint, request, jsonify
from firebase_admin import auth, db
import uuid
from datetime import datetime, timezone

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
        # Verify the ID token to authenticate the user
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']

        user = auth.get_user(uid)
        email = user.email
        
        # Reference products directly in the Realtime DB
        ref = db.reference('products')
        
        # Fetch current products
        current_products = ref.get()
        
        if current_products is None:
            current_products = []

        if not isinstance(current_products, list):
            return jsonify({'message': 'Error: Product data is corrupted'}), 500

        # Check if the sample product exists and filter it out
        updated_products = [p for p in current_products if isinstance(p, dict) and p.get('name') != 'Sample Product']

        # Create new product with unique ID
        product_id = str(uuid.uuid4())  # Generate a unique ID
        new_product = {
            'id': product_id,
            'name': product.get('name'),
            'price': product.get('price'),
            'category': product.get('category'),
            'description': product.get('description'),
            'created_by': email,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat(),
        }
        
        # Append the new product to the list
        updated_products.append(new_product)
        ref.set(updated_products)
        
        # Debugging: Print to console
        print(f"Saved product with ID: {product_id} and data: {new_product}")
        
        return jsonify({'message': 'Product added successfully!', 'product_id': product_id}), 201

    except auth.InvalidIdTokenError:
        return jsonify({'message': 'Invalid ID Token'}), 401

    except Exception as e:
        return jsonify({'message': f'Failed to add product: {str(e)}'}), 500
    
@routes.route('/user_products', methods=['GET'])
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


@routes.route('/delete_product/<string:product_id>', methods=['DELETE'])
def delete_product(product_id):
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
        current_products = ref.get()
        
        if current_products is None:
            current_products = []
        
        product_to_delete = next((p for p in current_products if p.get('id') == product_id), None)
            
        if not product_to_delete:
            return jsonify({'message': 'Product not found'}), 404
        
        if product_to_delete.get('created_by') != email:
            return jsonify({'message': 'Unauthorized to delete this product'}), 403
        
        updated_products = [p for p in current_products if p.get('id') != product_id]
        
        if len(updated_products) == len(current_products):
            return jsonify({'message': 'Product not found'}), 404
        ref.set(updated_products)
        return jsonify({'message':'Product deleted successfully'}), 200
    
    except auth.InvalidIdTokenError:
        return jsonify({'message': 'Invalid ID Token'}), 401

    except Exception as e:
        return jsonify({'message': f'Failed to delete product: {str(e)}'}), 500
    
@routes.route('/product_info/<string:product_id>', methods=['GET'])
def product_info(product_id):
    data = request.get_json()
    id_token = data.get('idToken')
    
    if not id_token:
        return jsonify({'message': 'ID Token is required'}), 400
    
    try:
        ref = db.reference('products')
        current_products = ref.get()
        product = next((p for p in current_products if p.get('id') == product_id), None)
        return jsonify(product)
    
    except auth.InvalidIdTokenError:
        return jsonify({'message': 'Invalid ID Token'}), 401

    except Exception as e:
        return jsonify({'message': f'Failed to get product info: {str(e)}'}), 500