from flask import Blueprint, request, jsonify
from firebase_admin import auth, db
import uuid
from datetime import datetime, timezone

bp = Blueprint('product', __name__)

@bp.route('/upload_product', methods=['POST'])
def upload_product():
    data = request.get_json()
    id_token = data.get('idToken')
    product = data.get('product')
    
    if not id_token or not product:
        return jsonify({'message': 'ID Token and product data are required'}), 400
    
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']

        user = auth.get_user(uid)
        email = user.email
        
        ref = db.reference('products')
        current_products = ref.get()
        
        if current_products is None:
            current_products = []

        if not isinstance(current_products, list):
            return jsonify({'message': 'Error: Product data is corrupted'}), 500

        updated_products = [p for p in current_products if isinstance(p, dict) and p.get('name') != 'Sample Product']

        product_id = str(uuid.uuid4())
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
        
        updated_products.append(new_product)
        ref.set(updated_products)
        
        print(f"Saved product with ID: {product_id} and data: {new_product}")
        
        return jsonify({'message': 'Product added successfully!', 'product_id': product_id}), 201

    except auth.InvalidIdTokenError:
        return jsonify({'message': 'Invalid ID Token'}), 401

    except Exception as e:
        return jsonify({'message': f'Failed to add product: {str(e)}'}), 500

@bp.route('/delete_product/<string:product_id>', methods=['DELETE'])
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
    
@bp.route('/product_info/<string:product_id>', methods=['GET'])
def product_info(product_id):
    data = request.get_json()
    id_token = data.get('idToken')
    
    if not id_token:
        return jsonify({'message': 'ID Token is required'}), 400
    
    try:
        ref = db.reference('products')
        current_products = ref.get()
        product = next((p for p in current_products if p.get('id') == product_id), None)
        
        if product is None:
            return jsonify({'message': 'Product not found'}), 404
        
        return jsonify(product), 200
    
    except auth.InvalidIdTokenError:
        return jsonify({'message': 'Invalid ID Token'}), 401

    except Exception as e:
        return jsonify({'message': f'Failed to get product info: {str(e)}'}), 500
    
@bp.route('/all_products', methods=['GET'])
def all_products():
    data = request.get_json()
    id_token = data.get('idToken')
    
    if not id_token:
        return jsonify({'message': 'ID Token is required'}), 400
    
    try:
        ref = db.reference('products')
        current_products = ref.get()

        if current_products is None:
            return jsonify({'message': 'No products found'}), 404

        return jsonify(current_products), 200
    except auth.InvalidIdTokenError:
        return jsonify({'message': 'Invalid ID Token'}), 401

    except Exception as e:
        return jsonify({'message': f'Failed to get all products: {str(e)}'}), 500
    
@bp.route('/update_product/<string:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.get_json()
    id_token = data.get('idToken')
    if not data:
        return jsonify({'messsage':'No data provided for update'}), 400
    
    try:
        ref = db.reference('products')
        current_products = ref.get()
        
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        
        user = auth.get_user(uid)
        email = user.email
        
        if not current_products:
            return jsonify({'message': 'No products found'}), 404
        
        product_to_update = next((p for p in current_products if p.get('id') == product_id), None)
        
        if not product_to_update:
            return jsonify({'message': 'Product not found'}), 404
        
        if product_to_update.get('created_by') != email:
            return jsonify({'message': 'Unauthorized to update this product'}), 403
        
        if 'name' in data:
            product_to_update['name'] = data['name']
        if 'description' in data:
            product_to_update['description'] = data['description']
        if 'category' in data:
            product_to_update['category'] = data['category']
        if 'price' in data:
            product_to_update['price'] = data['price']
            
        product_to_update['updated_at'] = datetime.now(timezone.utc).isoformat()
        updated_products = [p if p.get('id') != product_id else product_to_update for p in current_products]
        ref.set(updated_products)
        return jsonify({'message': 'Product updated successfully', 'product': product_to_update}), 200
    except auth.InvalidIdTokenError:
        return jsonify({'message': 'Invalid ID Token'}), 401
    except Exception as e:
        return jsonify({'message': f'Failed to update product: {str(e)}'}), 500