# routes/rides.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from models import db, User, Ride
from datetime import datetime

rides_bp = Blueprint('rides_bp', __name__)

@rides_bp.route('/start', methods=['POST'])
@jwt_required()
def start_ride():
    try:
        user_id = int(get_jwt_identity())
    except ValueError:
        return jsonify({"error": "Invalid user identity"}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.deposit < 0:
        return jsonify({"error": "Insufficient deposit. Account blocked."}), 403

    active_ride = Ride.query.filter_by(user_id=user_id, status='active').first()
    if active_ride:
        return jsonify({"error": "You already have an active ride"}), 400

    data = request.get_json()
    location = data.get('location', 'Unknown')
    ride = Ride(user_id=user_id, start_location=location)
    db.session.add(ride)
    db.session.commit()

    return jsonify({
        "message": "Ride started",
        "ride_id": ride.id,
        "start_time": ride.start_time.isoformat()
    }), 201

@rides_bp.route('/end', methods=['POST'])
@jwt_required()
def end_ride():
    try:
        user_id = int(get_jwt_identity())
    except ValueError:
        return jsonify({"error": "Invalid user identity"}), 401

    ride = Ride.query.filter_by(user_id=user_id, status='active').first()
    if not ride:
        return jsonify({"error": "No active ride found"}), 404

    data = request.get_json()
    end_location = data.get('location', 'Unknown')
    ride.end_location = end_location
    ride.end_time = datetime.utcnow()

    duration = (ride.end_time - ride.start_time).total_seconds() / 60
    fare = round(duration * 0.5, 2)

    user = User.query.get(user_id)
    if user.balance >= fare:
        user.balance -= fare
    else:
        remaining = fare - user.balance
        user.balance = 0
        user.deposit -= remaining

    ride.fare = fare
    ride.status = "completed"

    if user.deposit < 0:
        user.is_active = False

    msg = f"Ride ended. Fare: Rs.{fare}. Duration: {int(duration)} mins."
    if user.deposit < 0:
        msg += " Your account is now blocked due to negative deposit."

    notification = Notification(user_id=user.id, message=msg)
    db.session.add(notification)
    db.session.commit()

    return jsonify({
        "message": "Ride ended",
        "fare": fare,
        "duration_mins": int(duration),
        "new_balance": user.balance,
        "new_deposit": user.deposit,
        "account_blocked": not user.is_active
    }), 200