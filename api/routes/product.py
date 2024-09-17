from flask import Blueprint, request, jsonify
from firebase_admin import auth, db
from datetime import datetime, timezone

bp = Blueprint('product', __name__)

@bp.route('/product_info/<string:product_id>', methods=['GET'])
def product_info(product_id):
    data = request.get_json()
    id_token = data.get('idToken')
    
    if not id_token:
        return jsonify({'message': 'ID Token is required'}), 400
    
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        
        ref = db.reference('products')
        current_products = ref.get()
        
        product = current_products.get(product_id, None)
        
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
    
@bp.route('/search_products', methods=["GET"])
def search_products():
    data = request.get_json()
    id_token = data.get('idToken')
    
    if not id_token:
        return jsonify({'message': 'ID Token is required.'}), 400
    
    search_query = request.args.get('query', '')
    
    if not search_query:
        return jsonify({'message': 'Search query is required.'})
    
    try:
        ref = db.reference('products')
        all_products = ref.get()
        
        if all_products is None:
            return jsonify({'message': 'No products found'}), 404
        
        products_list = list(all_products.values())
        
        matching_products = [
            p for p in products_list if search_query in p.get('name','').lower()
        ]
        return jsonify({
            'message': f'Found {len(matching_products)} matching products',
            'products': matching_products
        }), 200
    
    except auth.InvalidIdTokenError:
        return jsonify({'message': 'Invalid ID Token'}), 401
    except Exception as e:
        print(f"Error in search_products: {str(e)}")
        return jsonify({'message': 'An error occurred while searching products'}), 500
    
@bp.route('/products_by_category', methods=["GET"])
def products_by_category():
    category_name = request.args.get('category_name', '').lower()
    
    if not category_name:
        return jsonify({'message':'Category name is required'}), 400
    
    try:
        ref = db.reference('products')
        all_products = ref.get()
        
        if all_products is None:
            return jsonify({'message':'No products found in the database'}), 404
        
        products_list = list(all_products.values())
        
        matching_products = [
            p for p in products_list
            if p.get('category','').lower() == category_name
        ]
        return jsonify({
            'message': f'Found {len(matching_products)} matching products',
            'products': matching_products
        }), 200
    except Exception as e:
        print(f"Error in search_products: {str(e)}")
        return jsonify({'message': 'An error occurred while searching products'}), 500

@bp.route('/upload_product', methods=['POST'])
def upload_product():
    data = request.get_json()
    id_token = data.get('idToken')
    product = data.get('product')
    
    if not id_token or not product:
        return jsonify({'message': 'ID Token and product data are required.'}), 400
    
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']

        user = auth.get_user(uid)
        email = user.email
        
        ref = db.reference('products')
        current_products = ref.get()
        
        if current_products is None:
            current_products = {}

        new_product = {
            'name': product.get('name'),
            'price': product.get('price'),
            'category': product.get('category'),
            'description': product.get('description'),
            'created_by': email,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat(),
        }
        new_product_ref = ref.push(new_product)
        product_id = new_product_ref.key
        
        print(f"Saved product with ID: {product_id} and data: {new_product}")
        
        return jsonify({'message': 'Product added successfully!', 'product_id': product_id}), 201

    except auth.InvalidIdTokenError:
        return jsonify({'message': 'Invalid ID Token'}), 401

    except Exception as e:
        return jsonify({'message': f'Failed to add product: {str(e)}'}), 500

@bp.route('/bulk_upload_products', methods=['POST'])
def bulk_upload_products():
    data = request.get_json()
    id_token = data.get('idToken')
    products = data.get('products')
    if not data or not isinstance(products, list):
        return jsonify({'message': 'Invalid data format, Expected a list of products.'}), 400
    if not id_token:
        return jsonify({'message': 'ID Token is required.'}), 400
    
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']

        user = auth.get_user(uid)
        email = user.email

        ref = db.reference('products')
        uploaded_products = []
        for product in products:
            if 'name' not in product or 'price' not in product or 'description' not in product or 'category' not in product:
                return jsonify({'message': 'Missing product fields'}), 400
            product['created_at'] = datetime.now(timezone.utc).isoformat()
            product['updated_at'] = datetime.now(timezone.utc).isoformat()
            product['created_by'] = email
            new_product_ref = ref.push(product)
            product['id'] = new_product_ref.key
            uploaded_products.append(product)
        return jsonify({'message': 'Products uploaded successfully', 'products':uploaded_products})
    except auth.InvalidIdTokenError:
        return jsonify({'message': 'Invalid ID Token'}), 401

    except Exception as e:
        return jsonify({'message': f'Failed to add product: {str(e)}'}), 500
    
@bp.route('/delete_product/<string:product_id>', methods=['DELETE'])
def delete_product(product_id):
    data = request.get_json()
    id_token = data.get('idToken')
    
    if not id_token:
        return jsonify({'message': 'ID Token is required.'}), 400
    
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        user = auth.get_user(uid)
        email = user.email
        
        ref = db.reference('products')
        current_products = ref.get()
        
        if current_products is None:
            current_products = {}
        
        product_to_delete = current_products.get(product_id)
            
        if not product_to_delete:
            return jsonify({'message': 'Product not found'}), 404
        
        if product_to_delete.get('created_by') != email:
            return jsonify({'message': 'Unauthorized to delete this product'}), 403
        
        ref.child(product_id).delete()
        return jsonify({'message':'Product deleted successfully'}), 200
    
    except auth.InvalidIdTokenError:
        return jsonify({'message': 'Invalid ID Token'}), 401

    except Exception as e:
        return jsonify({'message': f'Failed to delete product: {str(e)}'}), 500

@bp.route('/bulk_delete_products', methods=['DELETE'])
def bulk_delete_products():
    data = request.get_json()
    id_token = data.get('idToken')
    product_ids = data.get('product_ids')
    
    if not id_token or not isinstance(product_ids, list):
        return jsonify({'message': 'ID Token and list of product IDs are required.'}), 400
    
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        user = auth.get_user(uid)
        email = user.email
        
        ref = db.reference('products')
        products = ref.get()
        
        if products is None or not isinstance(products, dict):
            return jsonify({'message':'No products found'}), 404
        
        deleted_products = []
        for product_id in product_ids:
            product = products.get(product_id)
            if product and product.get('created_by') == email:
                ref.child(product_id).delete()
                deleted_products.append(product_id)
                
        return jsonify({
            'message': f'Successfully deleted {len(deleted_products)} products',
            'deleted_product_ids': deleted_products
        }), 200
    except auth.InvalidIdTokenError:
        return jsonify({'message': 'Invalid ID Token'}), 401

    except Exception as e:
        return jsonify({'message': f'Failed to delete product: {str(e)}'}), 500

@bp.route('/update_product/<string:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.get_json()
    id_token = data.get('idToken')
    
    if not id_token:
        return jsonify({'message': 'ID Token is required.'}), 400
    
    if not data:
        return jsonify({'messsage':'No data provided for update'}), 400
    
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        user = auth.get_user(uid)
        email = user.email
        
        ref = db.reference('products')
        
        current_product = ref.child(product_id).get()
        
        if current_product is None:
            return jsonify({'message': 'Product not found'}), 404
        
        if current_product.get('created_by') != email:
            return jsonify({'message': 'Unauthorized to update this product'}), 403
        
        updates = {}
        if 'name' in data:
            updates['name'] = data['name']
        if 'description' in data:
            updates['description'] = data['description']
        if 'category' in data:
            updates['category'] = data['category']
        if 'price' in data:
            updates['price'] = data['price']
        if updates:
            updates['updated_at'] = datetime.now(timezone.utc).isoformat()
            ref.child(product_id).update(updates)
            
        updated_product = ref.child(product_id).get()
        return jsonify({'message': 'Product updated successfully', 'product': updated_product}), 200
    
    except auth.InvalidIdTokenError:
        return jsonify({'message': 'Invalid ID Token'}), 401
    except Exception as e:
        return jsonify({'message': f'Failed to update product: {str(e)}'}), 500