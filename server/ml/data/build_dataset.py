"""
MoodFlix — Training Dataset Builder

Merges four sources into a single clean, balanced CSV mapped to the 16
canonical MoodFlix moods:

  1. The hand-written mood_training_data.csv (~764 rows, 67 messy labels)
  2. augmentation.csv (~160 hand-written samples for weak classes)
  3. synthetic_mood_data.csv (~96k generated samples — 6k per class)
  4. dair-ai/emotion (HuggingFace, ~20k rows, 6 labels)
  5. go_emotions (HuggingFace, ~58k Reddit comments, 27 labels + neutral)

All non-canonical labels are normalized via MOOD_MAP below. After merging,
the result is class-balanced (up-sample weak classes from the synthetic pool
when needed, down-sample over-represented real-world classes) and written to
`mood_training_data_clean.csv`.

Run:
    cd server && source venv/bin/activate && python -m ml.data.synth_generator
    python -m ml.data.build_dataset
"""
from __future__ import annotations

import os
import sys
import random
from collections import Counter

import pandas as pd

# Canonical MoodFlix moods (must match MOOD_CATEGORIES in mood_classifier.py)
CANONICAL_MOODS = {
    "happy", "sad", "lonely", "romantic", "excited",
    "relaxed", "stressed", "dark", "emotional", "mind-bending",
    "curious", "nostalgic", "motivated", "adventurous",
    "wholesome", "scared",
}

# Master mapping: any source label -> one of the 16 canonical moods (or None to drop)
MOOD_MAP: dict[str, str | None] = {
    # ---- already canonical (identity) ----
    **{m: m for m in CANONICAL_MOODS},

    # ---- our own CSV's extra labels (67 -> 16) ----
    "joyful": "happy",
    "amused": "happy",
    "playful": "happy",
    "pleasant": "happy",
    "satisfied": "happy",
    "content": "relaxed",
    "peaceful": "relaxed",
    "relieved": "relaxed",
    "calm": "relaxed",
    "grateful": "wholesome",
    "loved": "wholesome",
    "warm": "wholesome",
    "kind": "wholesome",
    "helpful": "wholesome",
    "touched": "emotional",
    "flattered": "emotional",
    "vulnerable": "emotional",
    "melancholic": "sad",
    "grief-stricken": "sad",
    "disappointed": "sad",
    "gutted": "sad",
    "regretful": "sad",
    "ashamed": "sad",
    "guilty": "sad",
    "defeated": "sad",
    "isolated": "lonely",
    "yearning": "lonely",
    "anxious": "stressed",
    "fearful": "scared",
    "frustrated": "stressed",
    "furious": "dark",
    "angry": "dark",
    "bitter": "dark",
    "jealous": "dark",
    "disgusted": "dark",
    "embarrassed": "emotional",
    "apathetic": "sad",
    "neutral": None,  # too generic
    "surprised": "curious",
    "inspired": "motivated",
    "hopeful": "motivated",
    "empowered": "motivated",
    "courageous": "motivated",
    "brave": "motivated",
    "strong": "motivated",
    "capable": "motivated",
    "accomplished": "motivated",
    "proud": "motivated",
    "focused": "motivated",
    "humble": "wholesome",
    "lucky": "happy",
    "smart": "curious",

    # ---- dair-ai/emotion (6 labels) ----
    "sadness": "sad",
    "joy": "happy",
    "love": "romantic",
    "anger": "dark",
    "fear": "scared",
    "surprise": "curious",

    # ---- go_emotions (27 + neutral) ----
    "admiration": "wholesome",
    "amusement": "happy",
    "annoyance": "stressed",
    "approval": "wholesome",
    "caring": "wholesome",
    "confusion": "mind-bending",
    "curiosity": "curious",
    "desire": "romantic",
    "disappointment": "sad",
    "disapproval": "stressed",
    "disgust": "dark",
    "embarrassment": "emotional",
    "excitement": "excited",
    "gratitude": "wholesome",
    "grief": "sad",
    "nervousness": "stressed",
    "optimism": "motivated",
    "pride": "motivated",
    "realization": "curious",
    "relief": "relaxed",
    "remorse": "emotional",
}


def _normalize(label: str) -> str | None:
    label = label.strip().lower()
    return MOOD_MAP.get(label)


def _load_local_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]
    df = df[["text", "mood"]].dropna()
    df["mood"] = df["mood"].astype(str).map(_normalize)
    df = df.dropna(subset=["mood"])
    print(f"[local csv] kept {len(df)} rows after mapping")
    return df


def _load_dair_ai() -> pd.DataFrame:
    from datasets import load_dataset
    print("[dair-ai/emotion] downloading…")
    ds = load_dataset("dair-ai/emotion", split="train")
    label_names = ds.features["label"].names  # ['sadness', 'joy', 'love', 'anger', 'fear', 'surprise']
    rows = []
    for ex in ds:
        canonical = _normalize(label_names[ex["label"]])
        if canonical:
            rows.append((ex["text"], canonical))
    df = pd.DataFrame(rows, columns=["text", "mood"])
    print(f"[dair-ai/emotion] kept {len(df)} rows")
    return df


def _load_go_emotions() -> pd.DataFrame:
    from datasets import load_dataset
    print("[go_emotions] downloading…")
    ds = load_dataset("go_emotions", "simplified", split="train")
    label_names = ds.features["labels"].feature.names
    rows = []
    for ex in ds:
        if not ex["labels"]:
            continue
        # take the FIRST label (most prominent) to keep single-label classification
        canonical = _normalize(label_names[ex["labels"][0]])
        if canonical:
            rows.append((ex["text"], canonical))
    df = pd.DataFrame(rows, columns=["text", "mood"])
    print(f"[go_emotions] kept {len(df)} rows")
    return df


def _balance(df: pd.DataFrame, target_per_class: int = 6000) -> pd.DataFrame:
    """Equalize per-class counts to `target_per_class` by down-sampling.

    Up-sampling is handled upstream by mixing in a large synthetic corpus,
    so by the time we get here every class has well over `target` rows.
    If a class is still short (because synthetic was disabled), we leave it
    alone rather than duplicating — `class_weight='balanced'` in training
    handles the residual gap.
    """
    parts = []
    counts = df["mood"].value_counts()
    print(f"[balance] raw counts:\n{counts}")
    for mood, group in df.groupby("mood"):
        n = len(group)
        if n > target_per_class:
            sampled = group.sample(n=target_per_class, random_state=42)
        else:
            sampled = group
        parts.append(sampled)
    out = pd.concat(parts, ignore_index=True)
    out = out.sample(frac=1.0, random_state=42).reset_index(drop=True)
    return out


def main() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    local_csv = os.path.join(here, "mood_training_data.csv")
    synth_csv = os.path.join(here, "synthetic_mood_data.csv")
    out_csv = os.path.join(here, "mood_training_data_clean.csv")

    dfs: list[pd.DataFrame] = []
    if os.path.exists(local_csv):
        dfs.append(_load_local_csv(local_csv))

    # Hand-written augmentation specifically for weak classes (adventurous,
    # lonely, nostalgic, relaxed, excited, emotional, mind-bending, motivated)
    aug_csv = os.path.join(here, "augmentation.csv")
    if os.path.exists(aug_csv):
        dfs.append(_load_local_csv(aug_csv))

    # Synthetic corpus — 6k samples per class with rich style variation.
    # This is the dominant signal source for weak classes.
    if os.path.exists(synth_csv):
        synth = pd.read_csv(synth_csv)
        synth.columns = [c.strip().lower() for c in synth.columns]
        synth = synth[["text", "mood"]].dropna()
        synth = synth[synth["mood"].isin(CANONICAL_MOODS)]
        print(f"[synthetic] kept {len(synth)} rows")
        dfs.append(synth)
    else:
        print("[synthetic] missing — run `python -m ml.data.synth_generator` first.", file=sys.stderr)

    try:
        dfs.append(_load_dair_ai())
    except Exception as e:
        print(f"[dair-ai/emotion] FAILED ({e}). Continuing without it.", file=sys.stderr)

    try:
        dfs.append(_load_go_emotions())
    except Exception as e:
        print(f"[go_emotions] FAILED ({e}). Continuing without it.", file=sys.stderr)

    if not dfs:
        print("No data sources loaded. Aborting.", file=sys.stderr)
        sys.exit(1)

    df = pd.concat(dfs, ignore_index=True)
    # basic text hygiene
    df["text"] = df["text"].astype(str).str.strip()
    df = df[df["text"].str.len() > 3]
    df = df.drop_duplicates(subset=["text"]).reset_index(drop=True)

    # confirm only canonical labels survive
    assert set(df["mood"].unique()) <= CANONICAL_MOODS, \
        f"Non-canonical labels leaked: {set(df['mood'].unique()) - CANONICAL_MOODS}"

    df = _balance(df, target_per_class=6000)
    print(f"\n[final] total rows: {len(df)}")
    print(f"[final] class counts:\n{df['mood'].value_counts()}")

    df.to_csv(out_csv, index=False)
    print(f"\n[final] wrote {out_csv}")


if __name__ == "__main__":
    main()
