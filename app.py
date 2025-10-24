# app.py
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from models import db
from routes.auth import auth_bp
from routes.rides import rides_bp
from routes.user import user_bp
from routes.admin import admin_bp
import os

def create_app():
    app = Flask(__name__)
    
    # Configurations
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'jwt-secret-string-bike-app'

    # Initialize extensions
    db.init_app(app)
    JWTManager(app)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.rides import rides_bp
    from routes.user import user_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(rides_bp, url_prefix='/api/rides')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    # Create tables
    with app.app_context():
        db.create_all()
        # Create default admin if not exists
        from models import User
        if not User.query.filter_by(email="admin@bike.com").first():
            admin = User(
                name="Admin",
                email="admin@bike.com",
                cnic="0000000000000",
                role="admin"
            )
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()

    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({"status": "OK", "message": "Bike Sharing API is running!"})

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
