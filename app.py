"""
E-Commerce Flask Application
Premium online store with AWS integration
Users: RDS PostgreSQL | Products, Orders, Cart: DynamoDB
"""
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from config import Config
from aws_rds import rds_manager
from aws_dynamodb import dynamodb_manager
from auth import AuthManager, token_required, optional_token, validate_email, validate_password
import logging
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY
CORS(app)

# Initialize databases on startup
def initialize_databases():
    """Initialize RDS and DynamoDB tables"""
    try:
        logger.info("Initializing databases...")
        Config.validate()
        
        logger.info("Creating RDS tables (Users)...")
        rds_manager.create_tables_if_not_exist()
        
        logger.info("Creating DynamoDB tables (Products, Orders, Cart)...")
        dynamodb_manager.create_tables_if_not_exist()
        
        logger.info("All databases initialized successfully!")
        
    except Exception as e:
        logger.error(f"Error initializing databases: {e}")
        logger.warning("App will start but database operations may fail")


# ==================== PAGES ====================

@app.route('/')
def index():
    """Homepage with product catalog"""
    return render_template('index.html')


@app.route('/product/<product_id>')
def product_detail(product_id):
    """Product detail page"""
    return render_template('product.html')


@app.route('/cart')
def cart_page():
    """Shopping cart page"""
    return render_template('cart.html')


@app.route('/checkout')
def checkout_page():
    """Checkout page (requires login)"""
    return render_template('checkout.html')


@app.route('/auth')
def auth_page():
    """Login/Register page"""
    return render_template('auth.html')


@app.route('/orders')
def orders_page():
    """Order history page (requires login)"""
    return render_template('orders.html')


# ==================== AUTHENTICATION ENDPOINTS ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('email') or not data.get('password') or not data.get('name'):
            return jsonify({
                'success': False,
                'error': 'Email, password, and name are required'
            }), 400
        
        email = data['email'].lower()
        password = data['password']
        name = data['name']
        
        # Validate email
        if not validate_email(email):
            return jsonify({
                'success': False,
                'error': 'Invalid email format'
            }), 400
        
        # Validate password
        is_valid, message = validate_password(password)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': message
            }), 400
        
        # Check if user already exists
        existing_user = rds_manager.get_user_by_email(email)
        if existing_user:
            return jsonify({
                'success': False,
                'error': 'Email already registered'
            }), 400
        
        # Create new user in RDS
        user_id = AuthManager.generate_user_id()
        password_hash = AuthManager.hash_password(password)
        
        user = rds_manager.create_user(
            user_id=user_id,
            email=email,
            password_hash=password_hash,
            name=name
        )
        
        # Generate JWT token
        token = AuthManager.generate_token(user_id, email)
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'token': token,
            'user': {
                'user_id': user_id,
                'email': email,
                'name': name
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Error in registration: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({
                'success': False,
                'error': 'Email and password are required'
            }), 400
        
        email = data['email'].lower()
        password = data['password']
        
        # Get user from RDS by email
        user = rds_manager.get_user_by_email(email)
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'Invalid email or password'
            }), 401
        
        # Verify password
        if not AuthManager.verify_password(password, user['password_hash']):
            return jsonify({
                'success': False,
                'error': 'Invalid email or password'
            }), 401
        
        # Generate JWT token
        token = AuthManager.generate_token(user['user_id'], email)
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'token': token,
            'user': {
                'user_id': user['user_id'],
                'email': email,
                'name': user['name']
            }
        })
        
    except Exception as e:
        logger.error(f"Error in login: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/auth/verify', methods=['GET'])
@token_required
def verify_token(current_user):
    """Verify JWT token and get user info"""
    try:
        user = rds_manager.get_user(current_user['user_id'])
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'user': {
                'user_id': user['user_id'],
                'email': user['email'],
                'name': user['name']
            }
        })
        
    except Exception as e:
        logger.error(f"Error verifying token: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== PRODUCTS ENDPOINTS (PUBLIC) ====================

@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all products (public endpoint)"""
    try:
        category = request.args.get('category')
        products = dynamodb_manager.get_all_products(category=category)
        
        return jsonify({
            'success': True,
            'data': products,
            'count': len(products)
        })
        
    except Exception as e:
        logger.error(f"Error getting products: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/products/<product_id>', methods=['GET'])
def get_product(product_id):
    """Get single product details (public endpoint)"""
    try:
        product = dynamodb_manager.get_product(product_id)
        
        if not product:
            return jsonify({
                'success': False,
                'error': 'Product not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': product
        })
        
    except Exception as e:
        logger.error(f"Error getting product: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== PRODUCTS MANAGEMENT (ADMIN) ====================

@app.route('/api/admin/products', methods=['POST'])
@token_required
def create_product(current_user):
    """Create a new product (admin only)"""
    try:
        data = request.get_json()
        
        required_fields = ['name', 'description', 'price', 'category']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'{field} is required'
                }), 400
        
        product_id = f"PROD-{uuid.uuid4().hex[:8].upper()}"
        
        product = dynamodb_manager.create_product(
            product_id=product_id,
            name=data['name'],
            description=data['description'],
            price=data['price'],
            category=data['category'],
            image_url=data.get('image_url', ''),
            stock=data.get('stock', 0)
        )
        
        return jsonify({
            'success': True,
            'data': product,
            'message': 'Product created successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/admin/products/<product_id>', methods=['PUT'])
@token_required
def update_product(current_user, product_id):
    """Update a product (admin only)"""
    try:
        data = request.get_json()
        
        product = dynamodb_manager.update_product(product_id, **data)
        
        return jsonify({
            'success': True,
            'data': product,
            'message': 'Product updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error updating product: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/admin/products/<product_id>', methods=['DELETE'])
@token_required
def delete_product(current_user, product_id):
    """Delete a product (admin only)"""
    try:
        deleted = dynamodb_manager.delete_product(product_id)
        
        if deleted:
            return jsonify({
                'success': True,
                'message': 'Product deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Product not found'
            }), 404
            
    except Exception as e:
        logger.error(f"Error deleting product: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== CART ENDPOINTS ====================

@app.route('/api/cart', methods=['GET'])
@token_required
def get_cart(current_user):
    """Get user's cart"""
    try:
        cart = dynamodb_manager.get_cart(current_user['user_id'])
        
        if not cart:
            return jsonify({
                'success': True,
                'data': {'items': []}
            })
        
        return jsonify({
            'success': True,
            'data': cart
        })
        
    except Exception as e:
        logger.error(f"Error getting cart: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/cart', methods=['POST'])
@token_required
def save_cart(current_user):
    """Save cart items"""
    try:
        data = request.get_json()
        
        if 'items' not in data:
            return jsonify({
                'success': False,
                'error': 'items are required'
            }), 400
        
        cart = dynamodb_manager.save_cart(
            user_id=current_user['user_id'],
            items=data['items']
        )
        
        return jsonify({
            'success': True,
            'data': cart,
            'message': 'Cart saved successfully'
        })
        
    except Exception as e:
        logger.error(f"Error saving cart: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/cart', methods=['DELETE'])
@token_required
def clear_cart(current_user):
    """Clear user's cart"""
    try:
        dynamodb_manager.clear_cart(current_user['user_id'])
        
        return jsonify({
            'success': True,
            'message': 'Cart cleared successfully'
        })
        
    except Exception as e:
        logger.error(f"Error clearing cart: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== ORDERS ENDPOINTS ====================

@app.route('/api/orders', methods=['POST'])
@token_required
def create_order(current_user):
    """Create a new order (checkout)"""
    try:
        data = request.get_json()
        
        required_fields = ['items', 'total_amount', 'shipping_address']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'{field} is required'
                }), 400
        
        order_id = f"ORD-{uuid.uuid4().hex[:12].upper()}"
        
        order = dynamodb_manager.create_order(
            order_id=order_id,
            user_id=current_user['user_id'],
            items=data['items'],
            total_amount=data['total_amount'],
            shipping_address=data['shipping_address'],
            status='pending'
        )
        
        # Clear cart after successful order
        dynamodb_manager.clear_cart(current_user['user_id'])
        
        return jsonify({
            'success': True,
            'data': order,
            'message': 'Order placed successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/orders', methods=['GET'])
@token_required
def get_user_orders(current_user):
    """Get all orders for current user"""
    try:
        orders = dynamodb_manager.get_user_orders(current_user['user_id'])
        
        return jsonify({
            'success': True,
            'data': orders,
            'count': len(orders)
        })
        
    except Exception as e:
        logger.error(f"Error getting orders: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== HEALTH CHECK ====================

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'e-commerce-api'
    })


# Error handlers

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


if __name__ == '__main__':
    # Initialize databases
    initialize_databases()
    
    # Run Flask app
    logger.info(f"Starting E-Commerce app on {Config.HOST}:{Config.PORT}")
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
