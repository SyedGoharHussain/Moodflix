"""
MoodFlix — Recommendation Routes
POST /api/analyze-mood, GET /api/recommendations, GET /api/trending, etc.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from ml.mood_classifier import get_classifier
from ml.recommendation_engine import (
    get_recommendations, get_because_you_feel,
)
from services import tmdb_service
from services.firebase_service import create_document
from datetime import datetime

recs_bp = Blueprint("recommendations", __name__, url_prefix="/api")


@recs_bp.route("/analyze-mood", methods=["POST"])
def analyze_mood():
    data = request.get_json()
    if not data or not data.get("text"):
        return jsonify({"error": "Text input is required"}), 400

    text = data["text"].strip()
    if len(text) > 1000:
        return jsonify({"error": "Input too long (max 1000 chars)"}), 400

    classifier = get_classifier()
    result = classifier.predict(text)

    # LIME explanation — only attempt for model-backed predictions on non-trivial text.
    if result.get("source") in {"ml_model", "ensemble", "transformer"} and len(text.split()) >= 4:
        try:
            from ml.lime_explainer import explain as lime_explain
            lime = lime_explain(text)
            if lime:
                result["lime_explanation"] = lime
        except Exception as e:
            print(f"[analyze_mood] LIME skipped: {e}")

    # Log mood if user is authenticated
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
        if user_id:
            create_document("mood_logs", {
                "user_id": user_id,
                "text": text,
                "detected_mood": result["detected_mood"],
                "confidence": result["confidence"],
                "created_at": datetime.utcnow().isoformat(),
            })
    except Exception:
        pass

    return jsonify(result), 200


@recs_bp.route("/recommendations", methods=["GET"])
def recommendations():
    mood = request.args.get("mood", "curious")
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 20, type=int)

    user_id = None
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
    except Exception:
        pass

    result = get_recommendations(mood, user_id=user_id, page=page, limit=limit)
    return jsonify(result), 200


@recs_bp.route("/because-you-feel", methods=["GET"])
def because_you_feel():
    mood = request.args.get("mood", "happy")
    result = get_because_you_feel(mood)
    return jsonify(result), 200


@recs_bp.route("/trending", methods=["GET"])
def trending():
    media_type = request.args.get("type", "all")
    time_window = request.args.get("window", "week")
    page = request.args.get("page", 1, type=int)
    result = tmdb_service.get_trending(media_type, time_window, page)
    return jsonify(result), 200


@recs_bp.route("/top-rated", methods=["GET"])
def top_rated():
    media_type = request.args.get("type", "movie")
    page = request.args.get("page", 1, type=int)
    result = tmdb_service.get_top_rated(media_type, page)
    return jsonify(result), 200


@recs_bp.route("/popular", methods=["GET"])
def popular():
    media_type = request.args.get("type", "movie")
    page = request.args.get("page", 1, type=int)
    result = tmdb_service.get_popular(media_type, page)
    return jsonify(result), 200


@recs_bp.route("/movie/<int:movie_id>", methods=["GET"])
def movie_detail(movie_id):
    media_type = request.args.get("type", "movie")
    result = tmdb_service.get_movie_details(movie_id, media_type)
    if not result:
        return jsonify({"error": "Movie not found"}), 404
    return jsonify(result), 200


@recs_bp.route("/search", methods=["GET"])
def search():
    query = request.args.get("q", "")
    page = request.args.get("page", 1, type=int)
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400
    result = tmdb_service.search_movies(query, page)
    return jsonify(result), 200


@recs_bp.route("/genres", methods=["GET"])
def genres():
    media_type = request.args.get("type", "movie")
    result = tmdb_service.get_genres(media_type)
    return jsonify({"genres": result}), 200
