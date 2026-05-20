"""
MoodFlix — User Routes
GET /api/user/profile, POST /api/user/save, POST /api/user/rate, GET /api/user/history
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.firebase_service import (
    create_document, get_document, update_document,
    query_collection, delete_document, get_document_by_field,
)
from services.auth_service import get_user_profile, update_user_profile
from datetime import datetime

user_bp = Blueprint("user", __name__, url_prefix="/api/user")


@user_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = get_user_profile(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": user}), 200


@user_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    allowed = ["username", "bio", "avatar", "favorite_genres"]
    filtered = {k: v for k, v in data.items() if k in allowed}
    if not filtered:
        return jsonify({"error": "No valid fields to update"}), 400

    success = update_user_profile(user_id, filtered)
    if not success:
        return jsonify({"error": "Failed to update profile"}), 500

    user = get_user_profile(user_id)
    return jsonify({"user": user}), 200


@user_bp.route("/save", methods=["POST"])
@jwt_required()
def save_movie():
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data or not data.get("tmdb_id"):
        return jsonify({"error": "tmdb_id is required"}), 400

    doc_id = create_document("saved_movies", {
        "user_id": user_id,
        "tmdb_id": data["tmdb_id"],
        "title": data.get("title", ""),
        "poster": data.get("poster", ""),
        "rating": data.get("rating", 0),
        "media_type": data.get("media_type", "movie"),
        "created_at": datetime.utcnow().isoformat(),
    })
    return jsonify({"message": "Saved", "id": doc_id}), 201


@user_bp.route("/save/<int:tmdb_id>", methods=["DELETE"])
@jwt_required()
def unsave_movie(tmdb_id):
    user_id = get_jwt_identity()
    items = query_collection("saved_movies", [
        ("user_id", "==", user_id),
        ("tmdb_id", "==", tmdb_id),
    ])
    for item in items:
        delete_document("saved_movies", item["id"])
    return jsonify({"message": "Removed from saved"}), 200


@user_bp.route("/saved", methods=["GET"])
@jwt_required()
def get_saved():
    user_id = get_jwt_identity()
    items = query_collection("saved_movies", [("user_id", "==", user_id)],
                             order_by="created_at", order_dir="DESCENDING")
    return jsonify({"results": items}), 200


@user_bp.route("/rate", methods=["POST"])
@jwt_required()
def rate_movie():
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data or not data.get("tmdb_id") or data.get("rating") is None:
        return jsonify({"error": "tmdb_id and rating are required"}), 400

    rating_val = data["rating"]
    if not (1 <= rating_val <= 10):
        return jsonify({"error": "Rating must be between 1 and 10"}), 400

    doc_id = create_document("ratings", {
        "user_id": user_id,
        "tmdb_id": data["tmdb_id"],
        "rating": rating_val,
        "created_at": datetime.utcnow().isoformat(),
    })
    return jsonify({"message": "Rated", "id": doc_id}), 201


@user_bp.route("/history", methods=["GET"])
@jwt_required()
def watch_history():
    user_id = get_jwt_identity()
    items = query_collection("watch_history", [("user_id", "==", user_id)],
                             order_by="watched_at", order_dir="DESCENDING", limit=50)
    return jsonify({"results": items}), 200


@user_bp.route("/history", methods=["POST"])
@jwt_required()
def add_to_history():
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data or not data.get("tmdb_id"):
        return jsonify({"error": "tmdb_id is required"}), 400

    doc_id = create_document("watch_history", {
        "user_id": user_id,
        "tmdb_id": data["tmdb_id"],
        "title": data.get("title", ""),
        "poster": data.get("poster", ""),
        "media_type": data.get("media_type", "movie"),
        "watched_at": datetime.utcnow().isoformat(),
    })
    return jsonify({"message": "Added to history", "id": doc_id}), 201


@user_bp.route("/mood-history", methods=["GET"])
@jwt_required()
def mood_history():
    user_id = get_jwt_identity()
    logs = query_collection("mood_logs", [("user_id", "==", user_id)],
                            order_by="created_at", order_dir="DESCENDING", limit=30)
    return jsonify({"results": logs}), 200
