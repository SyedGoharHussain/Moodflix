"""
MoodFlix — Explainability Engine
Generates human-readable AI explanations for recommendations.
"""


def explain_recommendation(movie, mood, user_history=None):
    """Generate a detailed explanation panel for a recommendation."""
    mood_lower = mood.lower()
    genres = movie.get("genres", [])
    rating = movie.get("rating", 0)
    ai_expl = movie.get("ai_explanation", {})

    panel = {
        "mood_match": ai_expl.get("mood_match_pct", 0),
        "genre_similarity": ai_expl.get("genre_similarity", 0),
        "user_preference_match": 0,
        "similar_user_trends": 0,
        "emotional_alignment": ai_expl.get("emotional_alignment", ""),
        "reasons": ai_expl.get("reasons", []),
        "insights": [],
    }

    # Generate SHAP-style feature importance
    features = {}
    features["mood_signal"] = round(panel["mood_match"] / 100, 2)
    features["genre_fit"] = panel["genre_similarity"]
    features["community_rating"] = round(rating / 10, 2)
    features["popularity_factor"] = round(
        min(1.0, movie.get("popularity", 0) / 500), 2
    )

    if user_history:
        watched_genres = []
        for h in user_history:
            watched_genres.extend(h.get("genres", []))
        from collections import Counter
        genre_counts = Counter(watched_genres)
        overlap = sum(1 for g in genres if g in genre_counts)
        features["history_alignment"] = round(overlap / max(len(genres), 1), 2)
        panel["user_preference_match"] = int(features["history_alignment"] * 100)

    # Sort features by importance
    sorted_features = sorted(features.items(), key=lambda x: x[1], reverse=True)
    panel["feature_importance"] = [
        {"feature": f, "importance": v} for f, v in sorted_features
    ]

    # Generate natural-language insights
    if panel["mood_match"] > 70:
        panel["insights"].append(
            f"This title strongly resonates with your {mood_lower} mood profile"
        )
    if rating >= 8.0:
        panel["insights"].append("Critically acclaimed with outstanding reviews")
    if features.get("history_alignment", 0) > 0.5:
        panel["insights"].append("Closely matches your viewing history patterns")

    return panel
