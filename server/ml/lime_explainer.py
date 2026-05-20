"""
MoodFlix — LIME explanations for the mood classifier.

LIME perturbs the input text by deleting words and asks the classifier how
the predicted-class probability changes. The result is a list of (word, weight)
pairs — positive weight = word pushed the prediction TOWARD the top class,
negative = pushed it AWAY.

We expose this for the `/api/analyze-mood` endpoint so the frontend can
highlight the user's own words by their influence on the prediction.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Iterable

import numpy as np

from .mood_classifier import get_classifier


@lru_cache(maxsize=1)
def _explainer():
    # Imported lazily so the Flask process doesn't pay LIME's import cost
    # unless someone actually requests an explanation.
    from lime.lime_text import LimeTextExplainer
    classifier = get_classifier()
    if classifier.pipeline is None:
        return None
    class_names = list(classifier.pipeline.classes_)
    return LimeTextExplainer(class_names=class_names, bow=False, random_state=42)


def _predict_proba(texts: Iterable[str]) -> np.ndarray:
    classifier = get_classifier()
    return classifier.pipeline.predict_proba(list(texts))


def explain(text: str, num_features: int = 8, num_samples: int = 500) -> dict | None:
    """Return {top_mood, words: [{word, weight}], num_samples}.

    Returns None when no trained model is available, when input is too short
    to meaningfully perturb, or if LIME raises.
    """
    if not text or len(text.split()) < 3:
        return None

    explainer = _explainer()
    if explainer is None:
        return None

    classifier = get_classifier()
    if classifier.pipeline is None:
        return None

    try:
        # Pick the index of the predicted class to explain
        probs = classifier.pipeline.predict_proba([text])[0]
        top_idx = int(np.argmax(probs))
        top_mood = classifier.pipeline.classes_[top_idx]

        exp = explainer.explain_instance(
            text,
            _predict_proba,
            num_features=num_features,
            num_samples=num_samples,
            labels=(top_idx,),
        )
        pairs = exp.as_list(label=top_idx)
        # Normalize weights to [-1, 1] for easier UI rendering
        max_abs = max((abs(w) for _, w in pairs), default=1.0) or 1.0
        words = [
            {"word": w, "weight": round(weight / max_abs, 3)}
            for w, weight in pairs
        ]
        return {
            "top_mood": str(top_mood),
            "words": words,
            "num_samples": num_samples,
        }
    except Exception as e:
        print(f"[LIME] explain failed: {e}")
        return None
