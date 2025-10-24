# routes/auth.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from models import db, User

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validate required fields
    required = ['name', 'email', 'password', 'cnic']
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    if len(data['cnic']) != 13 or not data['cnic'].isdigit():
        return jsonify({"error": "CNIC must be exactly 13 digits"}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already registered"}), 400

    if User.query.filter_by(cnic=data['cnic']).first():
        return jsonify({"error": "CNIC already registered"}), 400

    # Minimum deposit of 100 Rs
    deposit = float(data.get('deposit', 100.0))
    if deposit < 100.0:
        return jsonify({"error": "Deposit must be at least 100 Rs"}), 400

    user = User(
        name=data['name'],
        email=data['email'],
        cnic=data['cnic'],
        deposit=deposit,
        balance=0.0
    )
    user.set_password(data['password'])

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201



@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    if not user.is_active:
        return jsonify({"error": "Account is blocked"}), 403

    # ✅ FIX: Use string ID for identity, role in claims
    additional_claims = {"role": user.role}
    token = create_access_token(
        identity=str(user.id),           # ← Must be string
        additional_claims=additional_claims
    )

    return jsonify({
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role  # Send role to frontend
        }
    }), 200