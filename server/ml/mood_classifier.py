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
                       "delighted", "ecstatic", "thrilled", "content", "pleased",
                       "smile", "laugh", "glad", "excited about life", "on top of the world",
                       "feeling great", "best day", "love life"],
            "sad": ["sad", "depressed", "down", "unhappy", "miserable", "heartbroken",
                     "grief", "sorrow", "crying", "tears", "gloomy", "melancholy",
                     "blue", "upset", "devastated", "hopeless", "lost", "fail", "failed",
                     "lose", "rejected", "rejection", "heartbreak", "broke up", "breakup",
                     "dumped", "left me", "she left", "he left", "they left", "split up",
                     "relationship ended", "painful", "hurt", "broken", "not okay",
                     "falling apart", "crushed", "shattered", "gutted", "grieving",
                     "mourning", "loss", "missed", "disappoint", "regret"],
            "lonely": ["lonely", "alone", "isolated", "abandoned", "solitary",
                        "lonesome", "by myself", "no one", "miss someone",
                        "empty", "disconnected", "friendless", "solo",
                        "single", "no friends", "nobody cares", "all alone",
                        "missing her", "missing him", "miss my", "without her",
                        "without him", "wish i had", "no company", "invisible"],
            "romantic": ["romantic", "love", "crush", "date", "valentine",
                          "passionate", "affection", "intimate", "sweetheart",
                          "soulmate", "butterflies", "kiss", "couple",
                          "girlfriend", "boyfriend", "partner", "dating",
                          "in love", "fell in love", "romance", "lover",
                          "anniversary", "proposal", "marriage", "wedding"],
            "excited": ["excited", "pumped", "can't wait",
                         "hyped", "energetic", "exhilarated", "fired up",
                         "stoked", "eager", "electrified", "win", "won",
                         "victory", "champion", "adrenaline", "epic", "action",
                         "explosive", "intense action", "fast paced", "thrill"],
            "relaxed": ["relaxed", "calm", "peaceful", "chill", "serene",
                         "tranquil", "zen", "lazy", "cozy", "comfortable",
                         "mellow", "unwind", "laid back", "rest", "sleepy",
                         "tired", "easygoing", "light movie", "nothing heavy",
                         "kick back", "slow down", "decompress"],
            "stressed": ["stressed", "anxious", "overwhelmed", "pressure",
                          "worried", "tense", "nervous", "burnout",
                          "exhausted", "overworked", "frazzled", "panic",
                          "deadline", "work", "school", "too much", "can't cope",
                          "on edge", "brain fried", "need escape", "distract"],
            "dark": ["dark", "twisted", "sinister", "disturbing",
                      "macabre", "eerie", "grim", "morbid",
                      "intense", "brutal", "raw", "evil", "villain",
                      "crime", "thriller", "psychological", "noir",
                      "revenge", "corrupt", "bleak", "violent", "gritty"],
            "emotional": ["emotional", "feeling deeply", "deep", "touching",
                           "moving", "cry", "sob", "weep", "sentimental", "poignant",
                           "heartfelt", "tear jerker", "vulnerable", "beautiful story",
                           "feel something", "process emotions", "heavy heart",
                           "need a cry", "something real", "deeply human"],
            "mind-bending": ["mind-bending", "mind-blowing", "trippy",
                              "inception", "matrix", "philosophical",
                              "paradox", "surreal", "abstract",
                              "thought-provoking", "complex", "twist",
                              "confused", "weird", "reality", "time travel",
                              "dimension", "simulation", "question everything"],
            "curious": ["curious", "interested", "learn", "discover",
                         "explore", "mystery", "investigat", "wonder",
                         "fascinated", "intrigued", "questioning",
                         "documentary", "true story", "how does", "why does",
                         "science", "history", "facts", "knowledge", "educate"],
            "nostalgic": ["nostalgic", "remember", "childhood", "memories",
                           "old times", "retro", "vintage", "throwback",
                           "classic", "good old days", "reminisce", "past",
                           "simpler times", "back then", "used to", "miss the old",
                           "90s", "80s", "70s", "grew up", "tradition"],
            "motivated": ["motivated", "motivation", "inspired", "inspiration",
                           "determined", "driven", "ambitious", "goals", "achieve",
                           "success", "persever", "hustle", "grind", "empower",
                           "workout", "gym", "study", "overcome", "underdog",
                           "never give up", "keep going", "keep pushing",
                           "dont give up", "don't give up", "push myself",
                           "conquer", "champion", "rise up", "bounce back",
                           "need to be inspired", "need inspiration"],
            "adventurous": ["adventurous", "adventure", "explore", "travel",
                             "journey", "quest", "wild",
                             "daring", "bold", "expedition", "hike", "nature",
                             "discover new worlds", "epic quest", "treasure",
                             "explore the unknown", "grand journey", "new places"],
            "wholesome": ["wholesome", "heartwarming", "sweet", "cute",
                           "family", "comfort", "gentle",
                           "uplifting", "feel-good", "warm", "dog", "cat", "pet",
                           "kindness", "innocent", "pure", "fuzzy", "good vibes",
                           "faith in humanity", "cozy movie", "feel good"],
            "scared": ["scared", "terrified", "horror", "fright",
                        "spooky", "creepy", "jump scare", "nightmare",
                        "haunted", "petrified", "fearful", "afraid",
                        "ghost", "monster", "demon", "scary", "terror",
                        "chilling", "spine", "dark night", "supernatural"],
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
        # 0. Direct mood bypass — when the user explicitly picks a mood from the UI
        #    the input will be exactly one of the 16 category names.
        direct = text.lower().strip()
        if direct in MOOD_CATEGORIES:
            return {
                "detected_mood": direct,
                "confidence": 0.92,
                "emotion_breakdown": {direct: 0.92},
                "source": "direct",
            }

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

        # 3. Try ML model — only trust it when confidence is high enough
        if self.pipeline is not None:
            try:
                prediction = self.pipeline.predict([cleaned])[0]
                probabilities = self.pipeline.predict_proba([cleaned])[0]
                classes = self.pipeline.classes_

                confidence = round(float(max(probabilities)), 2)

                # If the ML model is uncertain, fall through to keyword fallback.
                # This prevents bad guesses like "excited" for sad inputs.
                if confidence >= 0.52:
                    prob_pairs = sorted(
                        zip(classes, probabilities),
                        key=lambda x: x[1],
                        reverse=True,
                    )
                    breakdown = {m: round(float(p), 3) for m, p in prob_pairs[:5]}

                    # Boost confidence when emoji agrees with ML
                    if emoji_result and emoji_result["detected_mood"] == prediction:
                        confidence = min(0.99, confidence + 0.1)

                    return {
                        "detected_mood": prediction,
                        "confidence": confidence,
                        "emotion_breakdown": breakdown,
                        "source": "ml_model",
                    }
                # else: confidence too low — fall through to keyword fallback
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

    # Filter out classes with only 1 sample to avoid stratify errors
    class_counts = df['mood'].value_counts()
    valid_classes = class_counts[class_counts > 1].index
    df = df[df['mood'].isin(valid_classes)]

    X_train, X_test, y_train, y_test = train_test_split(
        df["text"], df["mood"], test_size=0.2, random_state=42, stratify=df["mood"]
    )

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            max_features=15000,
            ngram_range=(1, 3),
            min_df=1,
            max_df=0.95,
            sublinear_tf=True,
            analyzer="word",
        )),
        ("clf", LogisticRegression(
            max_iter=2000,
            C=5.0,
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

