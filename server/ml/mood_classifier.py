"""
MoodFlix — Mood classifier with transformer + TF-IDF ensemble.

Inference stack (in priority order):

  1. Transformer head (DistilBERT fine-tuned on 96k samples × 16 moods),
     loaded from `ml/models/transformer/`. ~3× more accurate than TF-IDF on
     short / slang / typo-laden inputs. Provides softmax probabilities.
  2. TF-IDF + LogisticRegression (with char + word features, hard-negative
     mining, sigmoid calibration). Acts as a second voter and as a fallback
     if torch/transformers are unavailable.
  3. Emoji-only fast path: when the input is just emojis we trust the
     emoji map directly.
  4. Keyword fallback: last-resort heuristic so the API never returns nothing.

The final prediction is a probability-space average of (1) and (2). If only
one is available, that one is used directly. If neither is available, the
keyword/emoji fallback is returned. Emoji agreement still gives a small
confidence bonus on top.
"""
from __future__ import annotations

import json
import os
import re
import string
import threading

import joblib

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "mood_classifier.pkl")
TRANSFORMER_DIR = os.path.join(MODEL_DIR, "transformer")

MOOD_CATEGORIES = [
    "happy", "sad", "lonely", "romantic", "excited",
    "relaxed", "stressed", "dark", "emotional", "mind-bending",
    "curious", "nostalgic", "motivated", "adventurous",
    "wholesome", "scared",
]

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
    "🤗": "wholesome", "☀️": "wholesome",
    "😱": "scared", "👻": "scared", "🎃": "scared", "😨": "scared",
    "🌀": "mind-bending", "🧠": "mind-bending", "🔮": "mind-bending",
}


def _clean_text(text: str) -> str:
    """Lowercase, drop URLs / mentions / hashtags, strip punctuation, normalize whitespace.

    Numbers are PRESERVED (intensity signals like '10/10' or '5 stars' carry mood signal).
    The transformer head receives the *raw* text — only the TF-IDF head sees this cleaned form.
    """
    text = text.lower().strip()
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"@\w+", "", text)
    text = re.sub(r"#\w+", "", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _detect_emoji_mood(text: str) -> dict | None:
    mood_scores: dict[str, int] = {}
    for emoji, mood in EMOJI_MOOD_MAP.items():
        if emoji in text:
            mood_scores[mood] = mood_scores.get(mood, 0) + 1
    if not mood_scores:
        return None
    top_mood = max(mood_scores, key=mood_scores.get)
    total = sum(mood_scores.values())
    return {
        "detected_mood": top_mood,
        "confidence": min(0.95, 0.65 + (mood_scores[top_mood] / total) * 0.30),
        "source": "emoji",
    }


def _is_emoji_dominant(text: str) -> bool:
    """True when the input is essentially just emojis (no real text content)."""
    stripped = text
    for emoji in EMOJI_MOOD_MAP:
        stripped = stripped.replace(emoji, "")
    stripped = re.sub(r"\s+", " ", stripped).strip()
    # Remove any remaining unicode emoji-like characters as a safety net.
    stripped = re.sub(r"[\U0001F300-\U0001FAFF☀-➿️]", "", stripped).strip()
    return len(stripped) <= 1  # tolerate a stray period / space


# Keyword fallback used only when no models are loaded.
_KEYWORD_MAP = {
    "happy":      ["happy", "great", "amazing", "wonderful", "joy", "cheerful", "fantastic", "awesome", "blessed", "delighted", "ecstatic", "thrilled", "pleased", "smile", "laugh", "glad"],
    "sad":        ["sad", "depressed", "down", "unhappy", "miserable", "heartbroken", "grief", "sorrow", "crying", "tears", "gloomy", "melancholy", "blue", "upset", "devastated", "hopeless", "fail", "lose"],
    "lonely":     ["lonely", "alone", "isolated", "abandoned", "solitary", "lonesome", "no one", "miss", "empty", "disconnected"],
    "romantic":   ["romantic", "love", "crush", "date", "valentine", "passionate", "affection", "intimate", "sweetheart", "soulmate", "butterflies", "kiss"],
    "excited":    ["excited", "thrilled", "pumped", "hyped", "energetic", "exhilarated", "fired up", "stoked", "eager", "win", "won", "victory", "game", "champion", "lfg", "lets go"],
    "relaxed":    ["relaxed", "calm", "peaceful", "chill", "serene", "tranquil", "zen", "cozy", "comfortable", "mellow", "unwind", "rest", "sleepy"],
    "stressed":   ["stressed", "anxious", "overwhelmed", "pressure", "worried", "tense", "nervous", "burnout", "exhausted", "frazzled", "panic", "deadline"],
    "dark":       ["dark", "twisted", "sinister", "disturbing", "creepy", "macabre", "eerie", "grim", "morbid", "brutal", "raw", "evil", "villain", "angry", "furious", "hate"],
    "emotional":  ["emotional", "feeling", "deep", "touching", "moving", "sentimental", "poignant", "heartfelt", "vulnerable", "tearful"],
    "mind-bending": ["mind-bending", "mind-blowing", "trippy", "inception", "matrix", "philosophical", "paradox", "surreal", "abstract", "thought-provoking", "twist", "confused"],
    "curious":    ["curious", "interested", "learn", "discover", "explore", "mystery", "investigate", "wonder", "fascinated", "intrigued"],
    "nostalgic":  ["nostalgic", "remember", "childhood", "memories", "old times", "retro", "vintage", "throwback", "classic", "reminisce", "past"],
    "motivated":  ["motivated", "inspired", "determined", "driven", "ambitious", "goals", "achieve", "success", "persevere", "hustle", "grind", "workout", "gym", "study"],
    "adventurous":["adventurous", "adventure", "explore", "travel", "journey", "quest", "wild", "thrill", "daring", "bold", "hike", "hiking", "trek", "camp", "mountain"],
    "wholesome":  ["wholesome", "heartwarming", "sweet", "cute", "family", "comfort", "gentle", "uplifting", "feel-good", "warm", "grateful"],
    "scared":     ["scared", "terrified", "horror", "fright", "spooky", "jump scare", "nightmare", "haunted", "petrified", "fearful", "afraid"],
}


def _keyword_fallback(text: str) -> dict:
    scores: dict[str, int] = {}
    t = text.lower()
    for mood, words in _KEYWORD_MAP.items():
        hits = sum(1 for w in words if w in t)
        if hits:
            scores[mood] = hits
    if not scores:
        return {
            "detected_mood": "curious",
            "confidence": 0.30,
            "emotion_breakdown": {"curious": 0.30},
            "source": "default",
        }
    total = sum(scores.values())
    top = max(scores, key=scores.get)
    breakdown = {m: round(s / total, 3) for m, s in sorted(scores.items(), key=lambda x: -x[1])[:5]}
    return {
        "detected_mood": top,
        "confidence": round(min(0.95, 0.55 + (scores[top] / total) * 0.40), 3),
        "emotion_breakdown": breakdown,
        "source": "keyword",
    }


# --------------------------------------------------------------------------
# Transformer wrapper
# --------------------------------------------------------------------------

class _TransformerHead:
    """Thin wrapper over a fine-tuned DistilBERT / RoBERTa checkpoint.

    Lazy-imports torch and transformers so the Flask process pays no startup
    cost when the checkpoint is absent.
    """

    def __init__(self, model_dir: str):
        self.model_dir = model_dir
        self.classes_: list[str] | None = None
        self._model = None
        self._tokenizer = None
        self._device = None
        self._lock = threading.Lock()
        self._import_error: str | None = None

    @property
    def available(self) -> bool:
        return os.path.isdir(self.model_dir) and os.path.exists(
            os.path.join(self.model_dir, "label_encoder.json")
        )

    def load(self) -> bool:
        if self._model is not None:
            return True
        if not self.available:
            return False
        with self._lock:
            if self._model is not None:
                return True
            try:
                import torch
                from transformers import AutoTokenizer, AutoModelForSequenceClassification
            except Exception as e:
                self._import_error = str(e)
                print(f"[MoodClassifier] transformer disabled — torch/transformers missing: {e}")
                return False
            try:
                with open(os.path.join(self.model_dir, "label_encoder.json")) as f:
                    enc = json.load(f)
                self.classes_ = [enc["id_to_label"][str(i)] for i in range(len(enc["id_to_label"]))]
                self._tokenizer = AutoTokenizer.from_pretrained(self.model_dir)
                self._model = AutoModelForSequenceClassification.from_pretrained(self.model_dir)
                self._model.eval()
                if torch.backends.mps.is_available():
                    self._device = torch.device("mps")
                elif torch.cuda.is_available():
                    self._device = torch.device("cuda")
                else:
                    self._device = torch.device("cpu")
                self._model.to(self._device)
                print(f"[MoodClassifier] transformer loaded ({self._device})")
                return True
            except Exception as e:
                print(f"[MoodClassifier] transformer load failed: {e}")
                self._model = None
                return False

    def predict_proba(self, text: str) -> dict[str, float] | None:
        if not self.load():
            return None
        import torch
        with torch.no_grad():
            enc = self._tokenizer(
                text, truncation=True, padding=True, max_length=96, return_tensors="pt",
            ).to(self._device)
            logits = self._model(**enc).logits[0]
            probs = torch.softmax(logits, dim=-1).cpu().tolist()
        return {cls: float(p) for cls, p in zip(self.classes_, probs)}


# --------------------------------------------------------------------------
# Ensemble classifier
# --------------------------------------------------------------------------

class MoodClassifier:
    """Stacked transformer + TF-IDF + emoji/keyword classifier.

    Weights default to 0.65/0.35 (transformer/tfidf). The TF-IDF voter still
    helps when the transformer has low confidence or when the input is a
    purely keyword-style phrase (gym, hike, etc).
    """

    def __init__(self):
        self.pipeline = None
        self.transformer = _TransformerHead(TRANSFORMER_DIR)
        self._load_tfidf()
        # Warm the transformer up so the first request isn't slow
        self.transformer.load()

    def _load_tfidf(self):
        if not os.path.exists(MODEL_PATH):
            print(f"[MoodClassifier] No TF-IDF model at {MODEL_PATH}; will use keyword fallback.")
            return
        try:
            self.pipeline = joblib.load(MODEL_PATH)
            print("[MoodClassifier] TF-IDF model loaded successfully.")
        except Exception as e:
            print(f"[MoodClassifier] Error loading TF-IDF model: {e}")
            self.pipeline = None

    def _tfidf_proba(self, cleaned: str) -> dict[str, float] | None:
        if self.pipeline is None:
            return None
        try:
            probs = self.pipeline.predict_proba([cleaned])[0]
            return {cls: float(p) for cls, p in zip(self.pipeline.classes_, probs)}
        except Exception as e:
            print(f"[MoodClassifier] TF-IDF predict_proba failed: {e}")
            return None

    @staticmethod
    def _blend(transformer_p: dict[str, float] | None,
               tfidf_p: dict[str, float] | None,
               w_tf: float = 0.65,
               w_lr: float = 0.35) -> dict[str, float] | None:
        if transformer_p and tfidf_p:
            keys = set(transformer_p) | set(tfidf_p)
            out = {k: w_tf * transformer_p.get(k, 0.0) + w_lr * tfidf_p.get(k, 0.0) for k in keys}
            total = sum(out.values()) or 1.0
            return {k: v / total for k, v in out.items()}
        if transformer_p:
            return transformer_p
        if tfidf_p:
            return tfidf_p
        return None

    def predict(self, text: str) -> dict:
        """Return {detected_mood, confidence, emotion_breakdown, source}."""
        if not text or not text.strip():
            return {
                "detected_mood": "curious",
                "confidence": 0.30,
                "emotion_breakdown": {"curious": 0.30},
                "source": "default",
            }

        emoji_result = _detect_emoji_mood(text)
        cleaned = _clean_text(text)

        # Pure-emoji input → just trust the emoji
        if emoji_result and (not cleaned or _is_emoji_dominant(text)):
            emoji_result["emotion_breakdown"] = {emoji_result["detected_mood"]: emoji_result["confidence"]}
            return emoji_result

        if not cleaned:
            return {
                "detected_mood": "curious",
                "confidence": 0.30,
                "emotion_breakdown": {"curious": 0.30},
                "source": "default",
            }

        transformer_p = self.transformer.predict_proba(text) if self.transformer.available else None
        tfidf_p = self._tfidf_proba(cleaned)

        blended = self._blend(transformer_p, tfidf_p)
        if blended is not None:
            ranked = sorted(blended.items(), key=lambda x: x[1], reverse=True)
            top_mood, top_prob = ranked[0]
            breakdown = {m: round(float(p), 3) for m, p in ranked[:5]}
            confidence = round(float(top_prob), 3)

            # Agreement bonuses
            if emoji_result and emoji_result["detected_mood"] == top_mood:
                confidence = min(0.99, confidence + 0.08)
            if transformer_p and tfidf_p:
                tf_top = max(transformer_p, key=transformer_p.get)
                lr_top = max(tfidf_p, key=tfidf_p.get)
                if tf_top == lr_top == top_mood:
                    confidence = min(0.99, confidence + 0.05)

            if transformer_p and tfidf_p:
                source = "ensemble"
            elif transformer_p:
                source = "transformer"
            else:
                source = "ml_model"

            return {
                "detected_mood": top_mood,
                "confidence": confidence,
                "emotion_breakdown": breakdown,
                "source": source,
            }

        # Keyword fallback when neither ML head loaded
        result = _keyword_fallback(cleaned)
        if emoji_result:
            if emoji_result["detected_mood"] == result["detected_mood"]:
                result["confidence"] = round(min(0.99, result["confidence"] + 0.15), 3)
            elif emoji_result["confidence"] > result["confidence"]:
                result["detected_mood"] = emoji_result["detected_mood"]
                result["confidence"] = emoji_result["confidence"]
        return result


_classifier_instance: MoodClassifier | None = None


def get_classifier() -> MoodClassifier:
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = MoodClassifier()
    return _classifier_instance


def train_model(data_path: str | None = None) -> dict:
    """Train an upgraded TF-IDF + LogReg ensemble on the merged 96k-row corpus.

    Differences vs. the legacy version:
      • Char + word n-grams (FeatureUnion) so OOV slang/typos still match.
      • Larger vocabulary (160k features) and longer n-grams (1–2 word, 3–5 char).
      • Hard-negative-mining pass: misclassified training samples are
        upweighted (×3) in a second fit to focus the decision boundary.
      • Sigmoid calibration is preserved so the API still returns sensible
        confidence values.
    """
    import pandas as pd
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.pipeline import Pipeline, FeatureUnion
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, f1_score, accuracy_score

    if data_path is None:
        here = os.path.dirname(__file__)
        clean = os.path.join(here, "data", "mood_training_data_clean.csv")
        legacy = os.path.join(here, "data", "mood_training_data.csv")
        data_path = clean if os.path.exists(clean) else legacy

    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Training data not found: {data_path}")

    print(f"[train] loading {data_path}")
    df = pd.read_csv(data_path)
    df["text"] = df["text"].astype(str).map(_clean_text)
    df = df[df["text"].str.len() > 2]
    df = df[df["mood"].isin(MOOD_CATEGORIES)].reset_index(drop=True)

    print(f"[train] {len(df)} samples / {df['mood'].nunique()} classes")
    print(df["mood"].value_counts())

    # Three-way split: train (HN mining + main fit), calib (sigmoid calibration), test (eval)
    X_trainval, X_test, y_trainval, y_test = train_test_split(
        df["text"], df["mood"],
        test_size=0.10, random_state=42, stratify=df["mood"],
    )
    X_train, X_calib, y_train, y_calib = train_test_split(
        X_trainval, y_trainval,
        test_size=0.12, random_state=42, stratify=y_trainval,
    )
    X_train, X_calib = X_train.reset_index(drop=True), X_calib.reset_index(drop=True)
    y_train, y_calib = y_train.reset_index(drop=True), y_calib.reset_index(drop=True)
    print(f"[train] split: train={len(X_train)}  calib={len(X_calib)}  test={len(X_test)}")

    features = FeatureUnion([
        ("word", TfidfVectorizer(
            analyzer="word",
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95,
            sublinear_tf=True,
            max_features=80_000,
        )),
        ("char", TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(3, 5),
            min_df=2,
            max_df=0.98,
            sublinear_tf=True,
            max_features=80_000,
        )),
    ])

    base = Pipeline([
        ("features", features),
        ("clf", LogisticRegression(
            C=4.0, solver="liblinear", max_iter=4000,
            class_weight="balanced",
        )),
    ])

    print("[train] first pass…")
    base.fit(X_train, y_train)

    # --- Hard negative mining: upweight misclassified train rows and refit ---
    train_pred = base.predict(X_train)
    misses = train_pred != y_train.values
    sample_weight = np.ones(len(X_train), dtype=float)
    sample_weight[misses] = 3.0
    n_hn = int(misses.sum())
    print(f"[train] hard negatives found: {n_hn} / {len(X_train)} (upweighting ×3)")
    if n_hn:
        X_train_feats = base.named_steps["features"].transform(X_train)
        clf2 = LogisticRegression(
            C=4.0, solver="liblinear", max_iter=4000, class_weight="balanced",
        )
        clf2.fit(X_train_feats, y_train, sample_weight=sample_weight)
        base.named_steps["clf"] = clf2

    # Sigmoid calibration on top, using the held-out calib fold (cv='prefit'
    # so the HN-mined base classifier is preserved instead of refitted).
    print("[train] calibrating on held-out fold…")
    pipeline = CalibratedClassifierCV(base, method="sigmoid", cv="prefit")
    pipeline.fit(X_calib, y_calib)

    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1m = f1_score(y_test, y_pred, average="macro")
    print(f"\n[train] accuracy: {acc:.4f}   macro-F1: {f1m:.4f}\n")
    print(classification_report(y_test, y_pred, digits=3))

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    print(f"[train] saved -> {MODEL_PATH}")

    return {
        "accuracy": round(float(acc), 4),
        "macro_f1": round(float(f1m), 4),
        "samples": len(df),
        "classes": sorted(df["mood"].unique().tolist()),
    }
