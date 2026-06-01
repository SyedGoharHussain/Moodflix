"""
MoodFlix — Main Flask Application
Entry point for the backend server.
"""

import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import get_config
from services.firebase_service import init_firebase


def create_app():
    app = Flask(__name__)

    # Load config
    config = get_config()
    app.config.from_object(config)

    # CORS
    CORS(app, resources={r"/api/*": {
        "origins": ["http://localhost:5173", "http://localhost:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
    }})

    # JWT
    JWTManager(app)

    # Initialize Firebase
    init_firebase()

    # Register blueprints
    from routes.auth import auth_bp
    from routes.recommendations import recs_bp
    from routes.users import user_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(recs_bp)
    app.register_blueprint(user_bp)

    # Health check
    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok", "service": "MoodFlix API"}), 200

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Endpoint not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error"}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)
