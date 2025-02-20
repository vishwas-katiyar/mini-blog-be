import jwt
from flask import request, jsonify
from functools import wraps
from models.user import User

def jwt_required_custom(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                return jsonify({"error": "Unauthorized, token missing"}), 401
            
            token = auth_header.split(" ")[1] if len(auth_header.split(" ")) > 1 else None
            if not token:
                return jsonify({"error": "Unauthorized, token missing"}), 401

            decoded_token = jwt.decode(token, 'helloworld', algorithms=["HS256"])
            user_id = decoded_token.get("sub")
            
            if not user_id:
                return jsonify({"error": "Unauthorized, invalid token"}), 401

            user = User.query.get(int(user_id))
            if not user:
                return jsonify({"error": "Unauthorized, user not found"}), 401

            return fn(user_id, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Unauthorized, token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Unauthorized, invalid token"}), 401
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": "Unauthorized"}), 401

    return wrapper
