from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from models.db import db
from routes.auth import auth_bp
from routes.blog import blog_bp
from config import Config

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS", "DELETE","PUT"]}}, supports_credentials=True)

app.config.from_object(Config)

JWTManager(app)
db.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(blog_bp)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

