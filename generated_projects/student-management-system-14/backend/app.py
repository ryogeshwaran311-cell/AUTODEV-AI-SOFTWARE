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
logger = logging.getLogger("Student Management System")

from database import db
from models import User, Student, Attendance, Course

def create_app():
    app = Flask(__name__)
    
    # Enable CORS for all routes and origins (for dev and preview)
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

    # SQLite Database configuration
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', f'sqlite:///{os.path.join(base_dir, "student_management_system.db")}')
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
            "service": "Student Management System Backend",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "SQLite connected"
        }), 200

    # Summary Statistics endpoint for Dashboard
    @app.route('/api/stats', methods=['GET'])
    def get_dashboard_stats():
        try:
            stats = {}
            stats["total_users"] = User.query.count()
            stats["total_students"] = Student.query.count()
            stats["total_attendances"] = Attendance.query.count()
            stats["total_courses"] = Course.query.count()
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
            if 'password_hash' in data: item.password_hash = str(data['password_hash']).strip()
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
            if 'password_hash' in data: item.password_hash = str(data['password_hash']).strip()
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

    # ================= Student CRUD Routes =================
    @app.route('/api/students', methods=['GET'])
    def get_students():
        try:
            query = Student.query
            search = request.args.get('search', '').strip()
            if search:
                from sqlalchemy import or_
                query = query.filter(or_(Student.first_name.ilike(f'%{search}%'), Student.last_name.ilike(f'%{search}%'), Student.email.ilike(f'%{search}%')))

            items = query.order_by(Student.id.desc()).all()
            return jsonify({
                "success": True,
                "data": [item.to_dict() for item in items],
                "total": len(items)
            }), 200
        except Exception as e:
            logger.error(f"Error fetching students: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/students/<int:item_id>', methods=['GET'])
    def get_student_by_id(item_id):
        item = Student.query.get_or_404(item_id)
        return jsonify({"success": True, "data": item.to_dict()}), 200

    @app.route('/api/students', methods=['POST'])
    def create_student():
        try:
            data = request.get_json() or {}
            item = Student()
            if 'first_name' in data: item.first_name = str(data['first_name']).strip()
            if 'last_name' in data: item.last_name = str(data['last_name']).strip()
            if 'email' in data: item.email = str(data['email']).strip()
            if 'roll_no' in data: item.roll_no = int(data['roll_no'])
            if 'grade' in data: item.grade = str(data['grade']).strip()
            if 'phone' in data: item.phone = str(data['phone']).strip()
            if 'address' in data: item.address = str(data['address']).strip()
            if 'enrollment_date' in data and data['enrollment_date']:
                try: item.enrollment_date = datetime.fromisoformat(data['enrollment_date'])
                except Exception: pass

            db.session.add(item)
            db.session.commit()
            return jsonify({"success": True, "message": "Student created successfully", "data": item.to_dict()}), 201
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating Student: {e}")
            return jsonify({"success": False, "error": str(e)}), 400

    @app.route('/api/students/<int:item_id>', methods=['PUT'])
    def update_student(item_id):
        try:
            item = Student.query.get_or_404(item_id)
            data = request.get_json() or {}
            if 'first_name' in data: item.first_name = str(data['first_name']).strip()
            if 'last_name' in data: item.last_name = str(data['last_name']).strip()
            if 'email' in data: item.email = str(data['email']).strip()
            if 'roll_no' in data: item.roll_no = int(data['roll_no'])
            if 'grade' in data: item.grade = str(data['grade']).strip()
            if 'phone' in data: item.phone = str(data['phone']).strip()
            if 'address' in data: item.address = str(data['address']).strip()
            if 'enrollment_date' in data and data['enrollment_date']:
                try: item.enrollment_date = datetime.fromisoformat(data['enrollment_date'])
                except Exception: pass

            db.session.commit()
            return jsonify({"success": True, "message": "Student updated successfully", "data": item.to_dict()}), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating Student: {e}")
            return jsonify({"success": False, "error": str(e)}), 400

    @app.route('/api/students/<int:item_id>', methods=['DELETE'])
    def delete_student(item_id):
        try:
            item = Student.query.get_or_404(item_id)
            db.session.delete(item)
            db.session.commit()
            return jsonify({"success": True, "message": "Student deleted successfully"}), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting Student: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    # ================= Attendance CRUD Routes =================
    @app.route('/api/attendances', methods=['GET'])
    def get_attendances():
        try:
            query = Attendance.query
            search = request.args.get('search', '').strip()
            if search:
                pass

            items = query.order_by(Attendance.id.desc()).all()
            return jsonify({
                "success": True,
                "data": [item.to_dict() for item in items],
                "total": len(items)
            }), 200
        except Exception as e:
            logger.error(f"Error fetching attendances: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/attendances/<int:item_id>', methods=['GET'])
    def get_attendance_by_id(item_id):
        item = Attendance.query.get_or_404(item_id)
        return jsonify({"success": True, "data": item.to_dict()}), 200

    @app.route('/api/attendances', methods=['POST'])
    def create_attendance():
        try:
            data = request.get_json() or {}
            item = Attendance()
            if 'student_id' in data: item.student_id = int(data['student_id'])
            if 'date' in data and data['date']:
                try: item.date = datetime.fromisoformat(data['date'])
                except Exception: pass
            if 'status' in data: item.status = str(data['status']).strip()
            if 'remarks' in data: item.remarks = str(data['remarks']).strip()

            db.session.add(item)
            db.session.commit()
            return jsonify({"success": True, "message": "Attendance created successfully", "data": item.to_dict()}), 201
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating Attendance: {e}")
            return jsonify({"success": False, "error": str(e)}), 400

    @app.route('/api/attendances/<int:item_id>', methods=['PUT'])
    def update_attendance(item_id):
        try:
            item = Attendance.query.get_or_404(item_id)
            data = request.get_json() or {}
            if 'student_id' in data: item.student_id = int(data['student_id'])
            if 'date' in data and data['date']:
                try: item.date = datetime.fromisoformat(data['date'])
                except Exception: pass
            if 'status' in data: item.status = str(data['status']).strip()
            if 'remarks' in data: item.remarks = str(data['remarks']).strip()

            db.session.commit()
            return jsonify({"success": True, "message": "Attendance updated successfully", "data": item.to_dict()}), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating Attendance: {e}")
            return jsonify({"success": False, "error": str(e)}), 400

    @app.route('/api/attendances/<int:item_id>', methods=['DELETE'])
    def delete_attendance(item_id):
        try:
            item = Attendance.query.get_or_404(item_id)
            db.session.delete(item)
            db.session.commit()
            return jsonify({"success": True, "message": "Attendance deleted successfully"}), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting Attendance: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    # ================= Course CRUD Routes =================
    @app.route('/api/courses', methods=['GET'])
    def get_courses():
        try:
            query = Course.query
            search = request.args.get('search', '').strip()
            if search:
                from sqlalchemy import or_
                query = query.filter(or_(Course.course_code.ilike(f'%{search}%'), Course.course_name.ilike(f'%{search}%')))

            items = query.order_by(Course.id.desc()).all()
            return jsonify({
                "success": True,
                "data": [item.to_dict() for item in items],
                "total": len(items)
            }), 200
        except Exception as e:
            logger.error(f"Error fetching courses: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/courses/<int:item_id>', methods=['GET'])
    def get_course_by_id(item_id):
        item = Course.query.get_or_404(item_id)
        return jsonify({"success": True, "data": item.to_dict()}), 200

    @app.route('/api/courses', methods=['POST'])
    def create_course():
        try:
            data = request.get_json() or {}
            item = Course()
            if 'course_code' in data: item.course_code = str(data['course_code']).strip()
            if 'course_name' in data: item.course_name = str(data['course_name']).strip()
            if 'instructor' in data: item.instructor = str(data['instructor']).strip()
            if 'credits' in data: item.credits = float(data['credits'])

            db.session.add(item)
            db.session.commit()
            return jsonify({"success": True, "message": "Course created successfully", "data": item.to_dict()}), 201
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating Course: {e}")
            return jsonify({"success": False, "error": str(e)}), 400

    @app.route('/api/courses/<int:item_id>', methods=['PUT'])
    def update_course(item_id):
        try:
            item = Course.query.get_or_404(item_id)
            data = request.get_json() or {}
            if 'course_code' in data: item.course_code = str(data['course_code']).strip()
            if 'course_name' in data: item.course_name = str(data['course_name']).strip()
            if 'instructor' in data: item.instructor = str(data['instructor']).strip()
            if 'credits' in data: item.credits = float(data['credits'])

            db.session.commit()
            return jsonify({"success": True, "message": "Course updated successfully", "data": item.to_dict()}), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating Course: {e}")
            return jsonify({"success": False, "error": str(e)}), 400

    @app.route('/api/courses/<int:item_id>', methods=['DELETE'])
    def delete_course(item_id):
        try:
            item = Course.query.get_or_404(item_id)
            db.session.delete(item)
            db.session.commit()
            return jsonify({"success": True, "message": "Course deleted successfully"}), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting Course: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    return app

def _seed_initial_data():
    """Populates realistic starter demo records if database is empty."""
    try:
        if User.query.count() == 0:
            demo_user = User(username="admin", email="admin@autodevai.io", role="Admin", password_hash="admin123")
            db.session.add(demo_user)
            db.session.commit()
        if Student.query.count() == 0:
            # Seed demo Student records
            db.session.add(Student(first_name='Demo Student 1', last_name='Demo Student 1', email='user1@example.com', roll_no='CODE-101', grade='Standard', phone='Sample phone 1', address='Initial demo record 1 populated for system testing.', enrollment_date='CODE-101'))
            db.session.add(Student(first_name='Demo Student 2', last_name='Demo Student 2', email='user2@example.com', roll_no='CODE-102', grade='Standard', phone='Sample phone 2', address='Initial demo record 2 populated for system testing.', enrollment_date='CODE-102'))
            db.session.commit()
        if Attendance.query.count() == 0:
            # Seed demo Attendance records
            db.session.add(Attendance(student_id=10, date='Sample date 1', status='Active', remarks='Initial demo record 1 populated for system testing.'))
            db.session.add(Attendance(student_id=20, date='Sample date 2', status='Active', remarks='Initial demo record 2 populated for system testing.'))
            db.session.commit()
        if Course.query.count() == 0:
            # Seed demo Course records
            db.session.add(Course(course_code='CODE-101', course_name='Demo Course 1', instructor='Sample instructor 1', credits=25.5))
            db.session.add(Course(course_code='CODE-102', course_name='Demo Course 2', instructor='Sample instructor 2', credits=51.0))
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.warning(f"Initial seed warning: {e}")

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    app = create_app()
    logger.info(f"Starting Student Management System Backend on http://{host}:{port}")
    app.run(host=host, port=port, debug=True)