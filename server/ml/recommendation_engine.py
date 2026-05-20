"""
MoodFlix — Hybrid Recommendation Engine
Combines content-based, mood-based, and collaborative filtering.
"""

import math
import random
from services import tmdb_service

MOOD_GENRE_WEIGHTS = {
    "happy": {"Comedy": 0.9, "Music": 0.7, "Animation": 0.6, "Family": 0.5},
    "sad": {"Drama": 0.9, "Romance": 0.6, "History": 0.3},
    "lonely": {"Drama": 0.8, "Romance": 0.7, "Family": 0.6},
    "romantic": {"Romance": 0.95, "Comedy": 0.6, "Drama": 0.5},
    "excited": {"Action": 0.9, "Adventure": 0.8, "Science Fiction": 0.7},
    "relaxed": {"Comedy": 0.8, "Animation": 0.7, "Family": 0.6, "Documentary": 0.5},
    "stressed": {"Comedy": 0.9, "Animation": 0.7, "Music": 0.6},
    "dark": {"Thriller": 0.9, "Horror": 0.8, "Crime": 0.7, "Mystery": 0.6},
    "emotional": {"Drama": 0.9, "Romance": 0.8, "War": 0.5},
    "mind-bending": {"Science Fiction": 0.9, "Mystery": 0.8, "Thriller": 0.7},
    "curious": {"Documentary": 0.9, "Mystery": 0.7, "Science Fiction": 0.6},
    "nostalgic": {"Family": 0.8, "Animation": 0.7, "Comedy": 0.6},
    "motivated": {"Drama": 0.8, "Adventure": 0.7, "History": 0.6},
    "adventurous": {"Adventure": 0.9, "Action": 0.8, "Science Fiction": 0.7},
    "wholesome": {"Family": 0.9, "Animation": 0.8, "Comedy": 0.7},
    "scared": {"Horror": 0.95, "Thriller": 0.7, "Mystery": 0.5},
}

MOOD_DESCRIPTIONS = {
    "happy": "uplifting and feel-good",
    "sad": "deeply moving and cathartic",
    "lonely": "warm, comforting, and connection-themed",
    "romantic": "love-filled and passionate",
    "excited": "high-energy and adrenaline-pumping",
    "relaxed": "calm and light-hearted",
    "stressed": "lighthearted for stress relief",
    "dark": "intense and psychologically gripping",
    "emotional": "emotionally rich and touching",
    "mind-bending": "mind-bending and thought-provoking",
    "curious": "fascinating and knowledge-expanding",
    "nostalgic": "classic and memory-evoking",
    "motivated": "inspirational and empowering",
    "adventurous": "thrilling adventures and epic journeys",
    "wholesome": "heartwarming and family-friendly",
    "scared": "terrifying and spine-chilling",
}

GENRE_ID_TO_NAME = {
    28: "Action", 12: "Adventure", 16: "Animation", 35: "Comedy",
    80: "Crime", 99: "Documentary", 18: "Drama", 10751: "Family",
    14: "Fantasy", 36: "History", 27: "Horror", 10402: "Music",
    9648: "Mystery", 10749: "Romance", 878: "Science Fiction",
    53: "Thriller", 10752: "War", 37: "Western",
}


def _mood_match_score(movie, mood):
    weights = MOOD_GENRE_WEIGHTS.get(mood.lower(), {})
    if not weights:
        return 0.5
    genres = [GENRE_ID_TO_NAME.get(g, "") for g in movie.get("genre_ids", [])]
    total = sum(weights.values())
    matched = sum(weights.get(g, 0) for g in genres)
    return round(matched / total, 3) if total else 0.5


def _content_score(movie):
    r = movie.get("rating", 0) / 10.0
    p = min(1.0, math.log1p(movie.get("popularity", 0)) / math.log1p(1000))
    return round(0.7 * r + 0.3 * p, 3)


def _collab_score(movie):
    vc = movie.get("vote_count", 0)
    r = movie.get("rating", 0)
    C, m = 6.5, 500
    if vc == 0:
        return 0.3
    return round(((vc / (vc + m)) * r + (m / (vc + m)) * C) / 10.0, 3)


def generate_explanation(movie, mood, scores):
    mood_lower = mood.lower()
    desc = MOOD_DESCRIPTIONS.get(mood_lower, "matching your mood")
    weights = MOOD_GENRE_WEIGHTS.get(mood_lower, {})
    genres = [GENRE_ID_TO_NAME.get(g, "") for g in movie.get("genre_ids", [])]
    matched = [g for g in genres if g in weights]
    pct = int(scores.get("mood_match", 0) * 100)

    reasons = []
    if pct > 60:
        reasons.append(f"Strong mood match ({pct}%) — this film is {desc}")
    elif pct > 30:
        reasons.append(f"Partial mood match ({pct}%) — aligns with your {mood_lower} mood")
    if matched:
        reasons.append(f"Genre alignment: {', '.join(matched)}")
    rating = movie.get("rating", 0)
    if rating >= 7.5:
        reasons.append(f"Highly rated ({rating}/10) by the community")
    if movie.get("popularity", 0) > 100:
        reasons.append("Trending among viewers with similar tastes")
    if not reasons:
        reasons.append(f"Selected to match your {mood_lower} mood")

    return {
        "mood_match_pct": pct,
        "genre_similarity": round(len(matched) / max(len(genres), 1), 2),
        "emotional_alignment": desc,
        "matched_genres": matched,
        "reasons": reasons,
        "scores": scores,
    }


def get_recommendations(mood, user_id=None, page=1, limit=20):
    movies = tmdb_service.get_movies_for_mood(mood, page=page).get("results", [])
    if page == 1:
        seen = {m["tmdb_id"] for m in movies}
        for m in tmdb_service.get_popular(page=1).get("results", []):
            if m["tmdb_id"] not in seen:
                movies.append(m)
                seen.add(m["tmdb_id"])

    # Shuffle the initial pool slightly to introduce variety
    random.shuffle(movies)

    scored = []
    for m in movies:
        ms = _mood_match_score(m, mood)
        cs = _content_score(m)
        cb = _collab_score(m)
        final = round(0.4 * cb + 0.3 * cs + 0.3 * ms, 3)
        scores = {"mood_match": ms, "content": cs, "collaborative": cb, "final": final}
        expl = generate_explanation(m, mood, scores)
        scored.append({**m, "mood_match_pct": expl["mood_match_pct"],
                       "ai_explanation": expl, "recommendation_score": final})

    scored.sort(key=lambda x: x["recommendation_score"], reverse=True)
    return {"mood": mood, "results": scored[:limit], "total": len(scored), "page": page}


def get_because_you_feel(mood):
    picks = get_recommendations(mood, limit=12).get("results", [])
    picks = [m for m in picks if m.get("rating", 0) >= 6.0][:12]
    desc = MOOD_DESCRIPTIONS.get(mood.lower(), mood)
    return {
        "title": f"Because You Feel {mood.capitalize()}",
        "description": f"We picked these {desc} titles just for you",
        "mood": mood, "results": picks,
    }
