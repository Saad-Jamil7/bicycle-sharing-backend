# routes/user.py
from flask import Blueprint, jsonify,request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Ride, Notification,db

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/me', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        user_id = int(get_jwt_identity())
    except ValueError:
        return jsonify({"error": "Invalid token"}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "cnic": user.cnic,
        "balance": user.balance,
        "deposit": user.deposit,
        "is_active": user.is_active,
        "role": user.role  # Include role!
    }), 200

@user_bp.route('/active-ride', methods=['GET'])
@jwt_required()
def get_active_ride():
    try:
        user_id = int(get_jwt_identity())
    except ValueError:
        return jsonify({"error": "Invalid token"}), 401

    ride = Ride.query.filter_by(user_id=user_id, status='active').first()
    if not ride:
        return jsonify({"active_ride": None}), 200

    return jsonify({
        "active_ride": {
            "ride_id": ride.id,
            "start_time": ride.start_time.isoformat(),
            "start_location": ride.start_location
        }
    }), 200

@user_bp.route('/ride-history', methods=['GET'])
@jwt_required()
def ride_history():
    try:
        user_id = int(get_jwt_identity())
    except ValueError:
        return jsonify({"error": "Invalid token"}), 401

    rides = Ride.query.filter_by(user_id=user_id, status='completed').order_by(Ride.end_time.desc()).all()
    history = []
    for r in rides:
        history.append({
            "ride_id": r.id,
            "start_time": r.start_time.isoformat(),
            "end_time": r.end_time.isoformat(),
            "start_location": r.start_location,
            "end_location": r.end_location,
            "fare": r.fare,
            "duration_mins": int((r.end_time - r.start_time).total_seconds() / 60)
        })
    return jsonify({"ride_history": history}), 200

@user_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    try:
        user_id = int(get_jwt_identity())
    except ValueError:
        return jsonify({"error": "Invalid token"}), 401

    notifs = Notification.query.filter_by(user_id=user_id).order_by(Notification.timestamp.desc()).all()
    result = [
        {
            "id": n.id,
            "message": n.message,
            "timestamp": n.timestamp.isoformat(),
            "is_read": n.is_read
        }
        for n in notifs
    ]
    return jsonify({"notifications": result}), 200

@user_bp.route('/add-balance', methods=['POST'])
@jwt_required()
def add_balance():
    try:
        user_id = int(get_jwt_identity())
    except ValueError:
        return jsonify({"error": "Invalid token"}), 401

    data = request.get_json(silent=True)
    amount = float(data.get('amount', 0))
    if amount <= 0:
        return jsonify({"error": "Amount must be positive"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.balance += amount
    notification = Notification(
        user_id=user.id,
        message=f"Rs.{amount} added to your balance. New balance: Rs.{user.balance}"
    )
    db.session.add(notification)
    db.session.commit()

    return jsonify({
        "message": "Balance added",
        "new_balance": user.balance
    }), 200