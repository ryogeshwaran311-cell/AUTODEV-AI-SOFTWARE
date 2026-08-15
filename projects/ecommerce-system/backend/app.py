import os
import io
import sys
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Windows UTF-8 console output safety
if sys.stdout is not None and hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("E-Commerce Management System")

from database import db
from models import User, Product, Order, Orderitem

def create_app():
    app = Flask(__name__)
    
    # Enable CORS for all routes and origins (for dev and preview)
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

    # SQLite Database configuration
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', f'sqlite:///{os.path.join(base_dir, "e-commerce_management_system.db")}')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()
        _seed_initial_data()

    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            "status": "healthy",
            "service": "E-Commerce Management System Backend",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "SQLite connected"
        }), 200

    # Summary Statistics endpoint for Dashboard
    @app.route('/api/stats', methods=['GET'])
    def get_dashboard_stats():
        try:
            stats = {}
            stats["total_users"] = User.query.count()
            stats["total_products"] = Product.query.count()
            stats["total_orders"] = Order.query.count()
            stats["total_orderitems"] = Orderitem.query.count()
            stats["system_status"] = "Operational"
            stats["last_updated"] = datetime.utcnow().isoformat()
            return jsonify({"success": True, "stats": stats}), 200
        except Exception as e:
            logger.error(f"Error fetching stats: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    # Authentication demo endpoint
    @app.route('/api/auth/login', methods=['POST'])
    def auth_login():
        data = request.get_json() or {}
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        if not username or not password:
            return jsonify({"success": False, "error": "Username and password are required"}), 400

        # Allow demo login or verify in DB
        user = User.query.filter((User.username == username) | (User.email == username)).first() if 'User' in globals() else None
        if user or (username in ['admin', 'demo'] and password in ['admin123', 'demo123', 'admin', 'password']):
            role = user.role if user else ("Admin" if username == 'admin' else "User")
            user_data = user.to_dict() if user else {"id": 1, "username": username, "role": role, "email": f"{username}@example.com"}
            return jsonify({
                "success": True,
                "message": "Login successful",
                "token": "demo_token_autodevai_jwt_secure",
                "user": user_data
            }), 200

        return jsonify({"success": False, "error": "Invalid username or password. Demo: admin / admin123"}), 401

    # ================= User CRUD Routes =================
    @app.route('/api/users', methods=['GET'])
    def get_users():
        try:
            query = User.query
            search = request.args.get('search', '').strip()
            if search:
                from sqlalchemy import or_
                query = query.filter(or_(User.username.ilike(f'%{search}%'), User.email.ilike(f'%{search}%')))

            items = query.order_by(User.id.desc()).all()
            return jsonify({
                "success": True,
                "data": [item.to_dict() for item in items],
                "total": len(items)
            }), 200
        except Exception as e:
            logger.error(f"Error fetching users: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/users/<int:item_id>', methods=['GET'])
    def get_user_by_id(item_id):
        item = User.query.get_or_404(item_id)
        return jsonify({"success": True, "data": item.to_dict()}), 200

    @app.route('/api/users', methods=['POST'])
    def create_user():
        try:
            data = request.get_json() or {}
            item = User()
            if 'username' in data: item.username = str(data['username']).strip()
            if 'email' in data: item.email = str(data['email']).strip()
            if 'role' in data: item.role = str(data['role']).strip()
            if 'created_at' in data and data['created_at']:
                try: item.created_at = datetime.fromisoformat(data['created_at'])
                except Exception: pass

            db.session.add(item)
            db.session.commit()
            return jsonify({"success": True, "message": "User created successfully", "data": item.to_dict()}), 201
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating User: {e}")
            return jsonify({"success": False, "error": str(e)}), 400

    @app.route('/api/users/<int:item_id>', methods=['PUT'])
    def update_user(item_id):
        try:
            item = User.query.get_or_404(item_id)
            data = request.get_json() or {}
            if 'username' in data: item.username = str(data['username']).strip()
            if 'email' in data: item.email = str(data['email']).strip()
            if 'role' in data: item.role = str(data['role']).strip()
            if 'created_at' in data and data['created_at']:
                try: item.created_at = datetime.fromisoformat(data['created_at'])
                except Exception: pass

            db.session.commit()
            return jsonify({"success": True, "message": "User updated successfully", "data": item.to_dict()}), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating User: {e}")
            return jsonify({"success": False, "error": str(e)}), 400

    @app.route('/api/users/<int:item_id>', methods=['DELETE'])
    def delete_user(item_id):
        try:
            item = User.query.get_or_404(item_id)
            db.session.delete(item)
            db.session.commit()
            return jsonify({"success": True, "message": "User deleted successfully"}), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting User: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    # ================= Product CRUD Routes =================
    @app.route('/api/products', methods=['GET'])
    def get_products():
        try:
            query = Product.query
            search = request.args.get('search', '').strip()
            if search:
                from sqlalchemy import or_
                query = query.filter(or_(Product.name.ilike(f'%{search}%')))

            items = query.order_by(Product.id.desc()).all()
            return jsonify({
                "success": True,
                "data": [item.to_dict() for item in items],
                "total": len(items)
            }), 200
        except Exception as e:
            logger.error(f"Error fetching products: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/products/<int:item_id>', methods=['GET'])
    def get_product_by_id(item_id):
        item = Product.query.get_or_404(item_id)
        return jsonify({"success": True, "data": item.to_dict()}), 200

    @app.route('/api/products', methods=['POST'])
    def create_product():
        try:
            data = request.get_json() or {}
            item = Product()
            if 'name' in data: item.name = str(data['name']).strip()
            if 'category' in data: item.category = str(data['category']).strip()
            if 'price' in data: item.price = float(data['price'])
            if 'stock' in data: item.stock = int(data['stock'])
            if 'description' in data: item.description = str(data['description']).strip()
            if 'image_url' in data: item.image_url = str(data['image_url']).strip()

            db.session.add(item)
            db.session.commit()
            return jsonify({"success": True, "message": "Product created successfully", "data": item.to_dict()}), 201
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating Product: {e}")
            return jsonify({"success": False, "error": str(e)}), 400

    @app.route('/api/products/<int:item_id>', methods=['PUT'])
    def update_product(item_id):
        try:
            item = Product.query.get_or_404(item_id)
            data = request.get_json() or {}
            if 'name' in data: item.name = str(data['name']).strip()
            if 'category' in data: item.category = str(data['category']).strip()
            if 'price' in data: item.price = float(data['price'])
            if 'stock' in data: item.stock = int(data['stock'])
            if 'description' in data: item.description = str(data['description']).strip()
            if 'image_url' in data: item.image_url = str(data['image_url']).strip()

            db.session.commit()
            return jsonify({"success": True, "message": "Product updated successfully", "data": item.to_dict()}), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating Product: {e}")
            return jsonify({"success": False, "error": str(e)}), 400

    @app.route('/api/products/<int:item_id>', methods=['DELETE'])
    def delete_product(item_id):
        try:
            item = Product.query.get_or_404(item_id)
            db.session.delete(item)
            db.session.commit()
            return jsonify({"success": True, "message": "Product deleted successfully"}), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting Product: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    # ================= Order CRUD Routes =================
    @app.route('/api/orders', methods=['GET'])
    def get_orders():
        try:
            query = Order.query
            search = request.args.get('search', '').strip()
            if search:
                pass

            items = query.order_by(Order.id.desc()).all()
            return jsonify({
                "success": True,
                "data": [item.to_dict() for item in items],
                "total": len(items)
            }), 200
        except Exception as e:
            logger.error(f"Error fetching orders: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/orders/<int:item_id>', methods=['GET'])
    def get_order_by_id(item_id):
        item = Order.query.get_or_404(item_id)
        return jsonify({"success": True, "data": item.to_dict()}), 200

    @app.route('/api/orders', methods=['POST'])
    def create_order():
        try:
            data = request.get_json() or {}
            item = Order()
            if 'user_id' in data: item.user_id = int(data['user_id'])
            if 'total_amount' in data: item.total_amount = str(data['total_amount']).strip()
            if 'status' in data: item.status = str(data['status']).strip()
            if 'created_at' in data and data['created_at']:
                try: item.created_at = datetime.fromisoformat(data['created_at'])
                except Exception: pass

            db.session.add(item)
            db.session.commit()
            return jsonify({"success": True, "message": "Order created successfully", "data": item.to_dict()}), 201
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating Order: {e}")
            return jsonify({"success": False, "error": str(e)}), 400

    @app.route('/api/orders/<int:item_id>', methods=['PUT'])
    def update_order(item_id):
        try:
            item = Order.query.get_or_404(item_id)
            data = request.get_json() or {}
            if 'user_id' in data: item.user_id = int(data['user_id'])
            if 'total_amount' in data: item.total_amount = str(data['total_amount']).strip()
            if 'status' in data: item.status = str(data['status']).strip()
            if 'created_at' in data and data['created_at']:
                try: item.created_at = datetime.fromisoformat(data['created_at'])
                except Exception: pass

            db.session.commit()
            return jsonify({"success": True, "message": "Order updated successfully", "data": item.to_dict()}), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating Order: {e}")
            return jsonify({"success": False, "error": str(e)}), 400

    @app.route('/api/orders/<int:item_id>', methods=['DELETE'])
    def delete_order(item_id):
        try:
            item = Order.query.get_or_404(item_id)
            db.session.delete(item)
            db.session.commit()
            return jsonify({"success": True, "message": "Order deleted successfully"}), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting Order: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    # ================= Orderitem CRUD Routes =================
    @app.route('/api/orderitems', methods=['GET'])
    def get_orderitems():
        try:
            query = Orderitem.query
            search = request.args.get('search', '').strip()
            if search:
                pass

            items = query.order_by(Orderitem.id.desc()).all()
            return jsonify({
                "success": True,
                "data": [item.to_dict() for item in items],
                "total": len(items)
            }), 200
        except Exception as e:
            logger.error(f"Error fetching orderitems: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/orderitems/<int:item_id>', methods=['GET'])
    def get_orderitem_by_id(item_id):
        item = Orderitem.query.get_or_404(item_id)
        return jsonify({"success": True, "data": item.to_dict()}), 200

    @app.route('/api/orderitems', methods=['POST'])
    def create_orderitem():
        try:
            data = request.get_json() or {}
            item = Orderitem()
            if 'order_id' in data: item.order_id = str(data['order_id']).strip()
            if 'product_id' in data: item.product_id = str(data['product_id']).strip()
            if 'quantity' in data: item.quantity = int(data['quantity'])
            if 'unit_price' in data: item.unit_price = str(data['unit_price']).strip()

            db.session.add(item)
            db.session.commit()
            return jsonify({"success": True, "message": "Orderitem created successfully", "data": item.to_dict()}), 201
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating Orderitem: {e}")
            return jsonify({"success": False, "error": str(e)}), 400

    @app.route('/api/orderitems/<int:item_id>', methods=['PUT'])
    def update_orderitem(item_id):
        try:
            item = Orderitem.query.get_or_404(item_id)
            data = request.get_json() or {}
            if 'order_id' in data: item.order_id = str(data['order_id']).strip()
            if 'product_id' in data: item.product_id = str(data['product_id']).strip()
            if 'quantity' in data: item.quantity = int(data['quantity'])
            if 'unit_price' in data: item.unit_price = str(data['unit_price']).strip()

            db.session.commit()
            return jsonify({"success": True, "message": "Orderitem updated successfully", "data": item.to_dict()}), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating Orderitem: {e}")
            return jsonify({"success": False, "error": str(e)}), 400

    @app.route('/api/orderitems/<int:item_id>', methods=['DELETE'])
    def delete_orderitem(item_id):
        try:
            item = Orderitem.query.get_or_404(item_id)
            db.session.delete(item)
            db.session.commit()
            return jsonify({"success": True, "message": "Orderitem deleted successfully"}), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting Orderitem: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    return app

def _seed_initial_data():
    """Populates realistic starter demo records if database is empty."""
    try:
        if User.query.count() == 0:
            demo_user = User(username="admin", email="admin@autodevai.io", role="Admin", password_hash="admin123")
            db.session.add(demo_user)
            db.session.commit()
        if Product.query.count() == 0:
            # Seed demo Product records
            db.session.add(Product(name='Demo Product 1', category='Standard', price=25.5, stock=10, description='Initial demo record 1 populated for system testing.', image_url='Sample image_url 1'))
            db.session.add(Product(name='Demo Product 2', category='Standard', price=51.0, stock=20, description='Initial demo record 2 populated for system testing.', image_url='Sample image_url 2'))
            db.session.commit()
        if Order.query.count() == 0:
            # Seed demo Order records
            db.session.add(Order(user_id=10, total_amount='Sample total_amount 1', status='Active', created_at='Sample created_at 1'))
            db.session.add(Order(user_id=20, total_amount='Sample total_amount 2', status='Active', created_at='Sample created_at 2'))
            db.session.commit()
        if Orderitem.query.count() == 0:
            # Seed demo Orderitem records
            db.session.add(Orderitem(order_id='Sample order_id 1', product_id='Sample product_id 1', quantity=10, unit_price='Sample unit_price 1'))
            db.session.add(Orderitem(order_id='Sample order_id 2', product_id='Sample product_id 2', quantity=20, unit_price='Sample unit_price 2'))
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.warning(f"Initial seed warning: {e}")

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    app = create_app()
    logger.info(f"Starting E-Commerce Management System Backend on http://{host}:{port}")
    app.run(host=host, port=port, debug=True)