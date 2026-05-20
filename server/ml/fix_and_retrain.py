"""
MoodFlix — Fix training data labels and retrain the model.
Run: python fix_and_retrain.py  (from the server/ml directory)
"""

import os
import pandas as pd

# ── Label remap: every non-standard label → one of the 16 supported moods ──
LABEL_REMAP = {
    "joyful":        "happy",
    "content":       "relaxed",
    "melancholic":   "nostalgic",
    "grief-stricken":"sad",
    "isolated":      "lonely",
    "yearning":      "emotional",
    "furious":       "dark",
    "anxious":       "stressed",
    "fearful":       "scared",
    "hopeful":       "motivated",
    "apathetic":     "sad",
    "guilty":        "emotional",
    "jealous":       "dark",
    "disgusted":     "dark",
    "playful":       "wholesome",
    "focused":       "motivated",
    "amused":        "happy",
    "inspired":      "motivated",
    "grateful":      "wholesome",
    "bitter":        "dark",
    "satisfied":     "relaxed",
    "vulnerable":    "emotional",
    "accomplished":  "motivated",
    "proud":         "motivated",
    "relieved":      "relaxed",
    "surprised":     "excited",
    "neutral":       "curious",
    "smart":         "curious",
    "helpful":       "wholesome",
    "warm":          "wholesome",
    "capable":       "motivated",
    "kind":          "wholesome",
    "lucky":         "happy",
    "pleasant":      "relaxed",
    "flattered":     "happy",
    "empowered":     "motivated",
    "strong":        "motivated",
    "brave":         "adventurous",
    "humble":        "wholesome",
    "courageous":    "adventurous",
    "defeated":      "sad",
    "regretful":     "emotional",
    "embarrassed":   "emotional",
    "frustrated":    "stressed",
    "disappointed":  "sad",
    "angry":         "dark",
    "gutted":        "sad",
    "ashamed":       "emotional",
    "touched":       "emotional",
    "loved":         "romantic",
    "romantic":      "romantic",   # already valid, keep
}

VALID_MOODS = {
    "happy", "sad", "lonely", "romantic", "excited",
    "relaxed", "stressed", "dark", "emotional", "mind-bending",
    "curious", "nostalgic", "motivated", "adventurous",
    "wholesome", "scared",
}

DATA_DIR  = os.path.join(os.path.dirname(__file__), "data")
CSV_PATH  = os.path.join(DATA_DIR, "mood_training_data.csv")
FIXED_CSV = os.path.join(DATA_DIR, "mood_training_data.csv")   # overwrite in-place


def remap_and_fix():
    print("[Fix] Loading training data …")
    df = pd.read_csv(CSV_PATH)
    print(f"[Fix] {len(df)} rows, {df['mood'].nunique()} unique labels before fix")
    print(f"[Fix] Labels: {sorted(df['mood'].unique())}\n")

    # Apply remapping
    df["mood"] = df["mood"].apply(lambda m: LABEL_REMAP.get(m, m))

    # Drop any remaining unknown labels
    unknown = set(df["mood"].unique()) - VALID_MOODS
    if unknown:
        print(f"[Fix] Dropping rows with unknown labels: {unknown}")
        df = df[df["mood"].isin(VALID_MOODS)]

    print(f"[Fix] {len(df)} rows, {df['mood'].nunique()} unique labels after fix")
    print(f"[Fix] Class distribution:\n{df['mood'].value_counts()}\n")

    df.to_csv(FIXED_CSV, index=False)
    print(f"[Fix] Fixed CSV saved → {FIXED_CSV}")
    return FIXED_CSV


if __name__ == "__main__":
    fixed_path = remap_and_fix()

    # Import and run the trainer
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from ml.mood_classifier import train_model

    print("\n[Train] Starting model training …")
    result = train_model(fixed_path)
    if result:
        print(f"\n✅ Training complete — Accuracy: {result['accuracy']:.4f}  |  Samples: {result['samples']}")
    else:
        print("❌ Training failed.")
