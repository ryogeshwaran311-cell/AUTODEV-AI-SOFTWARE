import json
from datetime import datetime
from database import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(200))
    password_hash = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'password_hash': self.password_hash,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(200))
    last_name = db.Column(db.String(200))
    email = db.Column(db.String(200), nullable=False)
    roll_no = db.Column(db.Integer, default=1)
    grade = db.Column(db.String(200))
    phone = db.Column(db.String(200))
    address = db.Column(db.Text)
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'roll_no': self.roll_no,
            'grade': self.grade,
            'phone': self.phone,
            'address': self.address,
            'enrollment_date': self.enrollment_date.isoformat() if self.enrollment_date else None,
        }


class Attendance(db.Model):
    __tablename__ = 'attendances'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, default=1)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(200))
    remarks = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'date': self.date.isoformat() if self.date else None,
            'status': self.status,
            'remarks': self.remarks,
        }


class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(200))
    course_name = db.Column(db.String(200))
    instructor = db.Column(db.String(200))
    credits = db.Column(db.Float, default=0.0)

    def to_dict(self):
        return {
            'id': self.id,
            'course_code': self.course_code,
            'course_name': self.course_name,
            'instructor': self.instructor,
            'credits': self.credits,
        }