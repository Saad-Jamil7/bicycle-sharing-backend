# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    cnic = db.Column(db.String(13), unique=True, nullable=False)  # 13-digit CNIC
    balance = db.Column(db.Float, default=0.0)
    deposit = db.Column(db.Float, default=100.0)  # Min 100 Rs required
    is_active = db.Column(db.Boolean, default=True)
    role = db.Column(db.String(10), default="user")  # "user" or "admin"

    def set_password(self, pwd):
        self.password = generate_password_hash(pwd)

    def check_password(self, pwd):
        return check_password_hash(self.password, pwd)


class Ride(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    start_location = db.Column(db.String(100))
    end_location = db.Column(db.String(100))
    fare = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(10), default="active")  # active, completed

    user = db.relationship('User', backref='rides')


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

    user = db.relationship('User', backref='notifications')