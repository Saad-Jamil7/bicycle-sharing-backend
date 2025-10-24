# routes/admin.py
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import User, Ride, Notification
from models import db

admin_bp = Blueprint('admin_bp', __name__)

@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
def admin_stats():
    claims = get_jwt()
    role = claims.get("role")
    if role != 'admin':
        return jsonify({"error": "Admin access required"}), 403

    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    total_rides = Ride.query.count()
    active_rides = Ride.query.filter_by(status='active').count()
    revenue = db.session.query(db.func.sum(Ride.fare)).scalar() or 0.0
    low_deposit_users = User.query.filter(User.deposit < 50, User.is_active == True).limit(5).all()
    warnings = [f"{u.name}: Deposit Rs.{u.deposit}" for u in low_deposit_users]

    return jsonify({
        "total_users": total_users,
        "active_users": active_users,
        "total_rides": total_rides,
        "active_rides": active_rides,
        "total_revenue": round(revenue, 2),
        "warnings": warnings
    }), 200

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def list_users():
    claims = get_jwt()
    role = claims.get("role")
    if role != 'admin':
        return jsonify({"error": "Admin access required"}), 403

    users = User.query.all()
    result = []
    for u in users:
        result.append({
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "cnic": u.cnic,
            "balance": u.balance,
            "deposit": u.deposit,
            "is_active": u.is_active,
            "role": u.role
        })
    return jsonify({"users": result}), 200