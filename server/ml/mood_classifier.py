"""
MoodFlix — NLP Mood Classifier
TF-IDF + Logistic Regression pipeline for detecting user emotional state.
Supports 16 mood categories with confidence scores and emotion breakdown.
"""

import os
import re
import string
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "mood_classifier.pkl")

MOOD_CATEGORIES = [
    "happy", "sad", "lonely", "romantic", "excited",
    "relaxed", "stressed", "dark", "emotional", "mind-bending",
    "curious", "nostalgic", "motivated", "adventurous",
    "wholesome", "scared",
]

# Emoji → mood mapping for emoji-based detection
EMOJI_MOOD_MAP = {
    "😊": "happy", "😄": "happy", "😁": "happy", "🥳": "happy", "😎": "happy",
    "🎉": "excited", "🤩": "excited", "⚡": "excited", "🔥": "excited",
    "😢": "sad", "😭": "sad", "💔": "sad", "😞": "sad",
    "😔": "lonely", "🥺": "lonely", "😿": "lonely",
    "❤️": "romantic", "💕": "romantic", "😍": "romantic", "🥰": "romantic",
    "😌": "relaxed", "🧘": "relaxed", "☮️": "relaxed", "🌿": "relaxed",
    "😰": "stressed", "😤": "stressed", "🤯": "stressed", "😩": "stressed",
    "🖤": "dark", "💀": "dark", "🌑": "dark", "😈": "dark",
    "🥲": "emotional", "😥": "emotional", "🥹": "emotional",
    "🤔": "curious", "🧐": "curious", "❓": "curious",
    "📸": "nostalgic", "🕰️": "nostalgic", "🌅": "nostalgic",
    "💪": "motivated", "🏆": "motivated", "🚀": "motivated",
    "🏔️": "adventurous", "✈️": "adventurous", "🗺️": "adventurous",
    "🤗": "wholesome", "🥰": "wholesome", "☀️": "wholesome",
    "😱": "scared", "👻": "scared", "🎃": "scared", "😨": "scared",
    "🌀": "mind-bending", "🧠": "mind-bending", "🔮": "mind-bending",
}


def _clean_text(text: str) -> str:
    """Clean and normalize input text."""
    text = text.lower().strip()
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"@\w+", "", text)
    text = re.sub(r"#\w+", "", text)
    # Keep emojis for now — they'll be stripped after emoji detection
    text = re.sub(r"\d+", "", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _detect_emoji_mood(text: str) -> dict | None:
    """Try to detect mood from emojis in the text."""
    mood_scores = {}
    for emoji, mood in EMOJI_MOOD_MAP.items():
        if emoji in text:
            mood_scores[mood] = mood_scores.get(mood, 0) + 1

    if mood_scores:
        top_mood = max(mood_scores, key=mood_scores.get)
        total = sum(mood_scores.values())
        return {
            "detected_mood": top_mood,
            "confidence": min(0.95, 0.6 + (mood_scores[top_mood] / total) * 0.35),
            "source": "emoji",
        }
    return None


class MoodClassifier:
    """NLP-based mood classification engine."""

    def __init__(self):
        self.pipeline = None
        self._load_model()

    def _load_model(self):
        """Load trained model from disk if available."""
        if os.path.exists(MODEL_PATH):
            try:
                self.pipeline = joblib.load(MODEL_PATH)
                print("[MoodClassifier] Model loaded successfully.")
            except Exception as e:
                print(f"[MoodClassifier] Error loading model: {e}")
                self.pipeline = None
        else:
            print("[MoodClassifier] No trained model found. Using keyword fallback.")

    def _keyword_fallback(self, text: str) -> dict:
        """Keyword-based mood detection when no ML model is available."""
        keyword_map = {
            "happy": ["happy", "great", "amazing", "wonderful", "joy", "cheerful",
                       "fantastic", "awesome", "good mood", "feeling good", "blessed",
                       "delighted", "ecstatic", "thrilled", "content", "pleased"],
            "sad": ["sad", "depressed", "down", "unhappy", "miserable", "heartbroken",
                     "grief", "sorrow", "crying", "tears", "gloomy", "melancholy",
                     "blue", "upset", "devastated", "hopeless"],
            "lonely": ["lonely", "alone", "isolated", "abandoned", "solitary",
                        "lonesome", "by myself", "no one", "miss someone",
                        "empty", "disconnected", "friendless"],
            "romantic": ["romantic", "love", "crush", "date", "valentine",
                          "passionate", "affection", "intimate", "sweetheart",
                          "soulmate", "butterflies", "heart"],
            "excited": ["excited", "thrilled", "pumped", "can't wait",
                         "hyped", "energetic", "exhilarated", "fired up",
                         "stoked", "eager", "electrified"],
            "relaxed": ["relaxed", "calm", "peaceful", "chill", "serene",
                         "tranquil", "zen", "lazy", "cozy", "comfortable",
                         "mellow", "unwind", "laid back"],
            "stressed": ["stressed", "anxious", "overwhelmed", "pressure",
                          "worried", "tense", "nervous", "burnout",
                          "exhausted", "overworked", "frazzled", "tired"],
            "dark": ["dark", "twisted", "sinister", "disturbing", "creepy",
                      "macabre", "eerie", "shadowy", "grim", "morbid",
                      "intense", "brutal", "raw"],
            "emotional": ["emotional", "feeling", "deep", "touching",
                           "moving", "crying", "sentimental", "poignant",
                           "heartfelt", "tear-jerker", "vulnerable"],
            "mind-bending": ["mind-bending", "mind-blowing", "trippy",
                              "inception", "matrix", "philosophical",
                              "paradox", "surreal", "abstract",
                              "thought-provoking", "complex", "twist"],
            "curious": ["curious", "interested", "learn", "discover",
                         "explore", "mystery", "investigat", "wonder",
                         "fascinated", "intrigued", "questioning"],
            "nostalgic": ["nostalgic", "remember", "childhood", "memories",
                           "old times", "retro", "vintage", "throwback",
                           "classic", "good old days", "reminisce"],
            "motivated": ["motivated", "inspired", "determined", "driven",
                           "ambitious", "goals", "achieve", "success",
                           "persever", "hustle", "grind", "empower"],
            "adventurous": ["adventurous", "adventure", "explore", "travel",
                             "journey", "quest", "wild", "thrill",
                             "daring", "bold", "expedition"],
            "wholesome": ["wholesome", "heartwarming", "sweet", "cute",
                           "family", "comfort", "cozy", "gentle",
                           "uplifting", "feel-good", "warm"],
            "scared": ["scared", "terrified", "horror", "fright",
                        "spooky", "creepy", "jump scare", "nightmare",
                        "haunted", "petrified", "fearful"],
        }

        scores = {}
        text_lower = text.lower()
        for mood, keywords in keyword_map.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[mood] = score

        if not scores:
            return {
                "detected_mood": "curious",
                "confidence": 0.30,
                "emotion_breakdown": {"curious": 0.30},
                "source": "default",
            }

        total = sum(scores.values())
        top_mood = max(scores, key=scores.get)

        # Build breakdown from top 3 moods
        sorted_moods = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
        breakdown = {m: round(s / total, 2) for m, s in sorted_moods}

        return {
            "detected_mood": top_mood,
            "confidence": round(min(0.95, 0.5 + (scores[top_mood] / total) * 0.45), 2),
            "emotion_breakdown": breakdown,
            "source": "keyword",
        }

    def predict(self, text: str) -> dict:
        """
        Analyze text and return mood prediction.
        Returns: {detected_mood, confidence, emotion_breakdown, source}
        """
        # 1. Try emoji detection first
        emoji_result = _detect_emoji_mood(text)

        # 2. Clean text for NLP
        cleaned = _clean_text(text)

        if not cleaned and emoji_result:
            emoji_result["emotion_breakdown"] = {emoji_result["detected_mood"]: emoji_result["confidence"]}
            return emoji_result

        if not cleaned:
            return {
                "detected_mood": "curious",
                "confidence": 0.30,
                "emotion_breakdown": {"curious": 0.30},
                "source": "default",
            }

        # 3. Try ML model
        if self.pipeline is not None:
            try:
                prediction = self.pipeline.predict([cleaned])[0]
                probabilities = self.pipeline.predict_proba([cleaned])[0]
                classes = self.pipeline.classes_

                # Build emotion breakdown (top 5)
                prob_pairs = sorted(
                    zip(classes, probabilities),
                    key=lambda x: x[1],
                    reverse=True,
                )
                breakdown = {m: round(float(p), 3) for m, p in prob_pairs[:5]}
                confidence = round(float(max(probabilities)), 2)

                # If emoji was also detected, boost confidence if they agree
                if emoji_result and emoji_result["detected_mood"] == prediction:
                    confidence = min(0.99, confidence + 0.1)

                return {
                    "detected_mood": prediction,
                    "confidence": confidence,
                    "emotion_breakdown": breakdown,
                    "source": "ml_model",
                }
            except Exception as e:
                print(f"[MoodClassifier] Prediction error: {e}")

        # 4. Fallback to keyword matching
        result = self._keyword_fallback(cleaned)

        # Merge with emoji result if available
        if emoji_result:
            if emoji_result["detected_mood"] == result["detected_mood"]:
                result["confidence"] = min(0.99, result["confidence"] + 0.15)
            elif emoji_result["confidence"] > result["confidence"]:
                result["detected_mood"] = emoji_result["detected_mood"]
                result["confidence"] = emoji_result["confidence"]

        return result


def train_model(data_path: str = None):
    """
    Train the mood classifier from CSV data.
    CSV must have columns: text, mood
    """
    import pandas as pd

    if data_path is None:
        data_path = os.path.join(os.path.dirname(__file__), "data", "mood_training_data.csv")

    if not os.path.exists(data_path):
        print(f"[Training] Data file not found: {data_path}")
        return None

    print("[Training] Loading data...")
    df = pd.read_csv(data_path)
    df["text"] = df["text"].apply(_clean_text)
    df = df[df["text"].str.len() > 0]

    print(f"[Training] {len(df)} samples, {df['mood'].nunique()} classes")
    print(f"[Training] Class distribution:\n{df['mood'].value_counts()}")

    X_train, X_test, y_train, y_test = train_test_split(
        df["text"], df["mood"], test_size=0.2, random_state=42, stratify=df["mood"]
    )

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95,
            sublinear_tf=True,
        )),
        ("clf", LogisticRegression(
            max_iter=1000,
            C=1.0,
            class_weight="balanced",
            solver="lbfgs",
            multi_class="multinomial",
        )),
    ])

    print("[Training] Fitting model...")
    pipeline.fit(X_train, y_train)

    # Evaluate
    y_pred = pipeline.predict(X_test)
    accuracy = (y_pred == y_test).mean()
    print(f"\n[Training] Accuracy: {accuracy:.4f}")
    print("\n[Training] Classification Report:")
    print(classification_report(y_test, y_pred))

    # Save model
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    print(f"[Training] Model saved to {MODEL_PATH}")

    return {
        "accuracy": round(accuracy, 4),
        "samples": len(df),
        "classes": list(df["mood"].unique()),
    }


# Singleton instance
_classifier_instance = None


def get_classifier() -> MoodClassifier:
    """Get or create the singleton MoodClassifier instance."""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = MoodClassifier()
    return _classifier_instance

