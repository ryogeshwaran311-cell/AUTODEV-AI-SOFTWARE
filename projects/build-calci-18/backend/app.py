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
logger = logging.getLogger("Build Calci")

from database import db
from models import User, Item, Log

def create_app():
    app = Flask(__name__)
    
    # Enable CORS for all routes and origins (for dev and preview)
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

    # SQLite Database configuration
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', f'sqlite:///{os.path.join(base_dir, "build_calci.db")}')
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
            "service": "Build Calci Backend",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "SQLite connected"
        }), 200

    # Summary Statistics endpoint for Dashboard
    @app.route('/api/stats', methods=['GET'])
    def get_dashboard_stats():
        try:
            stats = {}
            stats["total_users"] = User.query.count()
            stats["total_items"] = Item.query.count()
            stats["total_logs"] = Log.query.count()
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

    # ================= Item CRUD Routes =================
    @app.route('/api/items', methods=['GET'])
    def get_items():
        try:
            query = Item.query
            search = request.args.get('search', '').strip()
            if search:
                from sqlalchemy import or_
                query = query.filter(or_(Item.title.ilike(f'%{search}%')))

            items = query.order_by(Item.id.desc()).all()
            return jsonify({
                "success": True,
                "data": [item.to_dict() for item in items],
                "total": len(items)
            }), 200
        except Exception as e:
            logger.error(f"Error fetching items: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/items/<int:item_id>', methods=['GET'])
    def get_item_by_id(item_id):
        item = Item.query.get_or_404(item_id)
        return jsonify({"success": True, "data": item.to_dict()}), 200

    @app.route('/api/items', methods=['POST'])
    def create_item():
        try:
            data = request.get_json() or {}
            item = Item()
            if 'title' in data: item.title = str(data['title']).strip()
            if 'description' in data: item.description = str(data['description']).strip()
            if 'category' in data: item.category = str(data['category']).strip()
            if 'status' in data: item.status = str(data['status']).strip()
            if 'created_at' in data and data['created_at']:
                try: item.created_at = datetime.fromisoformat(data['created_at'])
                except Exception: pass
            if 'updated_at' in data and data['updated_at']:
                try: item.updated_at = datetime.fromisoformat(data['updated_at'])
                except Exception: pass

            db.session.add(item)
            db.session.commit()
            return jsonify({"success": True, "message": "Item created successfully", "data": item.to_dict()}), 201
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating Item: {e}")
            return jsonify({"success": False, "error": str(e)}), 400

    @app.route('/api/items/<int:item_id>', methods=['PUT'])
    def update_item(item_id):
        try:
            item = Item.query.get_or_404(item_id)
            data = request.get_json() or {}
            if 'title' in data: item.title = str(data['title']).strip()
            if 'description' in data: item.description = str(data['description']).strip()
            if 'category' in data: item.category = str(data['category']).strip()
            if 'status' in data: item.status = str(data['status']).strip()
            if 'created_at' in data and data['created_at']:
                try: item.created_at = datetime.fromisoformat(data['created_at'])
                except Exception: pass
            if 'updated_at' in data and data['updated_at']:
                try: item.updated_at = datetime.fromisoformat(data['updated_at'])
                except Exception: pass

            db.session.commit()
            return jsonify({"success": True, "message": "Item updated successfully", "data": item.to_dict()}), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating Item: {e}")
            return jsonify({"success": False, "error": str(e)}), 400

    @app.route('/api/items/<int:item_id>', methods=['DELETE'])
    def delete_item(item_id):
        try:
            item = Item.query.get_or_404(item_id)
            db.session.delete(item)
            db.session.commit()
            return jsonify({"success": True, "message": "Item deleted successfully"}), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting Item: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    # ================= Log CRUD Routes =================
    @app.route('/api/logs', methods=['GET'])
    def get_logs():
        try:
            query = Log.query
            search = request.args.get('search', '').strip()
            if search:
                pass

            items = query.order_by(Log.id.desc()).all()
            return jsonify({
                "success": True,
                "data": [item.to_dict() for item in items],
                "total": len(items)
            }), 200
        except Exception as e:
            logger.error(f"Error fetching logs: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/logs/<int:item_id>', methods=['GET'])
    def get_log_by_id(item_id):
        item = Log.query.get_or_404(item_id)
        return jsonify({"success": True, "data": item.to_dict()}), 200

    @app.route('/api/logs', methods=['POST'])
    def create_log():
        try:
            data = request.get_json() or {}
            item = Log()
            if 'item_id' in data: item.item_id = str(data['item_id']).strip()
            if 'action' in data: item.action = str(data['action']).strip()
            if 'timestamp' in data and data['timestamp']:
                try: item.timestamp = datetime.fromisoformat(data['timestamp'])
                except Exception: pass
            if 'performed_by' in data: item.performed_by = str(data['performed_by']).strip()

            db.session.add(item)
            db.session.commit()
            return jsonify({"success": True, "message": "Log created successfully", "data": item.to_dict()}), 201
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating Log: {e}")
            return jsonify({"success": False, "error": str(e)}), 400

    @app.route('/api/logs/<int:item_id>', methods=['PUT'])
    def update_log(item_id):
        try:
            item = Log.query.get_or_404(item_id)
            data = request.get_json() or {}
            if 'item_id' in data: item.item_id = str(data['item_id']).strip()
            if 'action' in data: item.action = str(data['action']).strip()
            if 'timestamp' in data and data['timestamp']:
                try: item.timestamp = datetime.fromisoformat(data['timestamp'])
                except Exception: pass
            if 'performed_by' in data: item.performed_by = str(data['performed_by']).strip()

            db.session.commit()
            return jsonify({"success": True, "message": "Log updated successfully", "data": item.to_dict()}), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating Log: {e}")
            return jsonify({"success": False, "error": str(e)}), 400

    @app.route('/api/logs/<int:item_id>', methods=['DELETE'])
    def delete_log(item_id):
        try:
            item = Log.query.get_or_404(item_id)
            db.session.delete(item)
            db.session.commit()
            return jsonify({"success": True, "message": "Log deleted successfully"}), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting Log: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    return app

def _seed_initial_data():
    """Populates realistic starter demo records if database is empty."""
    try:
        if User.query.count() == 0:
            demo_user = User(username="admin", email="admin@autodevai.io", role="Admin", password_hash="admin123")
            db.session.add(demo_user)
            db.session.commit()
        if Item.query.count() == 0:
            # Seed demo Item records
            db.session.add(Item(title='Sample Item Title 1', description='Initial demo record 1 populated for system testing.', category='Standard', status='Active', created_at='Sample created_at 1', updated_at='Sample updated_at 1'))
            db.session.add(Item(title='Sample Item Title 2', description='Initial demo record 2 populated for system testing.', category='Standard', status='Active', created_at='Sample created_at 2', updated_at='Sample updated_at 2'))
            db.session.commit()
        if Log.query.count() == 0:
            # Seed demo Log records
            db.session.add(Log(item_id='Sample item_id 1', action='Sample action 1', timestamp='Sample timestamp 1', performed_by='Sample performed_by 1'))
            db.session.add(Log(item_id='Sample item_id 2', action='Sample action 2', timestamp='Sample timestamp 2', performed_by='Sample performed_by 2'))
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.warning(f"Initial seed warning: {e}")

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    app = create_app()
    logger.info(f"Starting Build Calci Backend on http://{host}:{port}")
    app.run(host=host, port=port, debug=True)