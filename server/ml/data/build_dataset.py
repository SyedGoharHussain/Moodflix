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


# Repo root → the user's downloaded raw datasets live under models/.
# build_dataset.py is at server/ml/data/, so root is three levels up.
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
MODELS_DIR = os.path.join(_REPO_ROOT, "models")

# Label index order for the downloaded dair-ai/emotion CSVs (text,label with 0-5).
DAIR_AI_LABELS = ["sadness", "joy", "love", "anger", "fear", "surprise"]

# Label index order for the downloaded GoEmotions TSVs (matches data/emotions.txt).
GO_EMOTIONS_LABELS = [
    "admiration", "amusement", "anger", "annoyance", "approval", "caring",
    "confusion", "curiosity", "desire", "disappointment", "disapproval",
    "disgust", "embarrassment", "excitement", "fear", "gratitude", "grief",
    "joy", "love", "nervousness", "optimism", "pride", "realization",
    "relief", "remorse", "sadness", "surprise", "neutral",
]


def _normalize(label: str) -> str | None:
    label = label.strip().lower()
    return MOOD_MAP.get(label)


def _first_existing(*paths: str) -> str | None:
    for p in paths:
        if p and os.path.exists(p):
            return p
    return None


def _load_dair_ai_local() -> pd.DataFrame | None:
    """Load dair-ai/emotion from the locally downloaded CSVs (models/archive (1)/).

    Columns are `text,label` where label is an int 0-5. Merges the train /
    validation / test splits for maximum real-world signal. Returns None when
    the local copy is not present (caller falls back to the HF download).
    """
    base = _first_existing(
        os.path.join(MODELS_DIR, "archive (1)"),
        os.path.join(MODELS_DIR, "archive"),
    )
    if not base:
        return None
    frames = []
    for name in ("training.csv", "validation.csv", "test.csv", "train.csv"):
        path = os.path.join(base, name)
        if not os.path.exists(path):
            continue
        part = pd.read_csv(path)
        part.columns = [c.strip().lower() for c in part.columns]
        if not {"text", "label"} <= set(part.columns):
            continue
        frames.append(part[["text", "label"]])
    if not frames:
        return None
    raw = pd.concat(frames, ignore_index=True).dropna()
    rows = []
    for _, r in raw.iterrows():
        try:
            name = DAIR_AI_LABELS[int(r["label"])]
        except (ValueError, IndexError, TypeError):
            continue
        canonical = _normalize(name)
        if canonical:
            rows.append((str(r["text"]), canonical))
    df = pd.DataFrame(rows, columns=["text", "mood"])
    print(f"[dair-ai/emotion · local] kept {len(df)} rows")
    return df


def _load_go_emotions_local() -> pd.DataFrame | None:
    """Load GoEmotions from the locally downloaded TSVs (models/archive/data/).

    Each row is `text \\t comma-separated-label-ids \\t comment_id`. We take the
    first (most prominent) label to keep this single-label, matching the HF
    `simplified` behaviour. Returns None when the local copy is absent.
    """
    base = _first_existing(
        os.path.join(MODELS_DIR, "archive", "data"),
        os.path.join(MODELS_DIR, "archive (1)", "data"),
    )
    if not base:
        return None
    rows = []
    for name in ("train.tsv", "dev.tsv", "test.tsv"):
        path = os.path.join(base, name)
        if not os.path.exists(path):
            continue
        tsv = pd.read_csv(path, sep="\t", header=None,
                          names=["text", "labels", "id"], dtype=str).dropna(subset=["text", "labels"])
        for _, r in tsv.iterrows():
            first = str(r["labels"]).split(",")[0].strip()
            if not first.isdigit():
                continue
            idx = int(first)
            if idx >= len(GO_EMOTIONS_LABELS):
                continue
            canonical = _normalize(GO_EMOTIONS_LABELS[idx])
            if canonical:
                rows.append((str(r["text"]), canonical))
    if not rows:
        return None
    df = pd.DataFrame(rows, columns=["text", "mood"])
    print(f"[go_emotions · local] kept {len(df)} rows")
    return df


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


def _balance_real_first(real: pd.DataFrame, synth: pd.DataFrame,
                        target_per_class: int = 6000,
                        real_cap: int = 3000) -> pd.DataFrame:
    """Build a class-balanced corpus that BLENDS real-world and synthetic text.

    For every canonical mood we take up to `real_cap` genuine samples first,
    then top the class up to `target_per_class` from the synthetic pool. The
    cap matters: GoEmotions (Reddit, first-label) is noisy and ambiguous for
    overlapping moods (stressed/wholesome/curious), so letting it fully
    dominate a class hurts accuracy. Capping real at ~half the class keeps the
    clean synthetic backbone (which also covers rare moods like adventurous /
    nostalgic that have almost no real data) while still teaching the model on
    real human phrasing. Set real_cap >= target_per_class for a real-first mix.
    """
    cap = min(real_cap, target_per_class)
    parts = []
    for mood in sorted(CANONICAL_MOODS):
        r = real[real["mood"] == mood]
        s = synth[synth["mood"] == mood]
        if len(r) >= cap:
            picked_r = r.sample(n=cap, random_state=42)
            need = target_per_class - cap
            picked_s = s.sample(n=min(need, len(s)), random_state=42) if (need > 0 and len(s)) else s.iloc[0:0]
        else:
            picked_r = r
            need = target_per_class - len(r)
            picked_s = s.sample(n=min(need, len(s)), random_state=42) if len(s) else s
        picked_r = picked_r.assign(_src="real")
        picked_s = picked_s.assign(_src="synth")
        merged = pd.concat([picked_r, picked_s], ignore_index=True)
        print(f"[balance] {mood:<13} → {len(merged):>5} "
              f"({len(picked_r)} real + {len(picked_s)} synth)")
        parts.append(merged)
    out = pd.concat(parts, ignore_index=True)
    out = out.sample(frac=1.0, random_state=42).reset_index(drop=True)
    return out


def main() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    local_csv = os.path.join(here, "mood_training_data.csv")
    synth_csv = os.path.join(here, "synthetic_mood_data.csv")
    out_csv = os.path.join(here, "mood_training_data_clean.csv")

    # ── Real-world sources (prioritized in the final balance) ───────────────
    real_dfs: list[pd.DataFrame] = []
    if os.path.exists(local_csv):
        real_dfs.append(_load_local_csv(local_csv))

    # Hand-written augmentation specifically for weak classes (adventurous,
    # lonely, nostalgic, relaxed, excited, emotional, mind-bending, motivated)
    aug_csv = os.path.join(here, "augmentation.csv")
    if os.path.exists(aug_csv):
        real_dfs.append(_load_local_csv(aug_csv))

    # dair-ai/emotion — prefer the locally downloaded CSVs, fall back to HF.
    dair = _load_dair_ai_local()
    if dair is None:
        try:
            dair = _load_dair_ai()
        except Exception as e:
            print(f"[dair-ai/emotion] FAILED ({e}). Continuing without it.", file=sys.stderr)
    if dair is not None:
        real_dfs.append(dair)

    # GoEmotions — prefer the locally downloaded TSVs (full ~58k), fall back to HF.
    go = _load_go_emotions_local()
    if go is None:
        try:
            go = _load_go_emotions()
        except Exception as e:
            print(f"[go_emotions] FAILED ({e}). Continuing without it.", file=sys.stderr)
    if go is not None:
        real_dfs.append(go)

    # ── Synthetic corpus — only used to TOP UP classes that real data leaves thin ──
    if os.path.exists(synth_csv):
        synth = pd.read_csv(synth_csv)
        synth.columns = [c.strip().lower() for c in synth.columns]
        synth = synth[["text", "mood"]].dropna()
        synth = synth[synth["mood"].isin(CANONICAL_MOODS)]
        print(f"[synthetic] available {len(synth)} rows (used only to fill gaps)")
    else:
        synth = pd.DataFrame(columns=["text", "mood"])
        print("[synthetic] missing — run `python -m ml.data.synth_generator` first.", file=sys.stderr)

    if not real_dfs and synth.empty:
        print("No data sources loaded. Aborting.", file=sys.stderr)
        sys.exit(1)

    real = pd.concat(real_dfs, ignore_index=True) if real_dfs else pd.DataFrame(columns=["text", "mood"])
    for frame in (real, synth):
        if not frame.empty:
            frame["text"] = frame["text"].astype(str).str.strip()
    real = real[real["text"].str.len() > 3].drop_duplicates(subset=["text"]).reset_index(drop=True)
    synth = synth[synth["text"].str.len() > 3].drop_duplicates(subset=["text"]).reset_index(drop=True)

    # confirm only canonical labels survive
    leaked = (set(real["mood"].unique()) | set(synth["mood"].unique())) - CANONICAL_MOODS
    assert not leaked, f"Non-canonical labels leaked: {leaked}"

    df = _balance_real_first(real, synth, target_per_class=6000)
    print(f"\n[final] total rows: {len(df)}")
    print(f"[final] real vs synthetic: {int((df['_src'] == 'real').sum())} real / "
          f"{int((df['_src'] == 'synth').sum())} synthetic")
    df = df.drop(columns=["_src"])
    print(f"[final] class counts:\n{df['mood'].value_counts()}")

    df.to_csv(out_csv, index=False)
    print(f"\n[final] wrote {out_csv}")


if __name__ == "__main__":
    main()
