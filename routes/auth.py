from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from models.user import User, db
import jwt , datetime
from middleware.auth_middleware import jwt_required_custom

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not all([data.get("name"), data.get("email"), data.get("password")]):
        return jsonify({"error": "Missing required fields"}), 400
    
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already exists"}), 400
    
    user = User(name=data["name"], email=data["email"])
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get("email")).first()
    if not user or not user.check_password(data.get("password")):
        return jsonify({"error": "Invalid credentials"}), 401

    payload = {
        "sub": str(user.id),  # Ensure user ID is a string
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
        "iat": datetime.datetime.utcnow()
    }
    access_token = jwt.encode(payload, 'helloworld', algorithm="HS256")

    return jsonify({"access_token": access_token}), 200

@auth_bp.route("/profile", methods=["PUT"])
@jwt_required_custom
def update_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    data = request.get_json()
    if "name" in data:
        user.name = data["name"]
    if "password" in data:
        user.set_password(data["password"])
    
    db.session.commit()
    return jsonify({"message": "Profile updated successfully"}), 200

@auth_bp.route("/profile", methods=["GET"])
@jwt_required_custom
def get_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "created_at": user.created_at
    }), 200
