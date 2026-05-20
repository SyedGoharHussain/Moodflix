"""
MoodFlix — Training entrypoint.

Trains the upgraded TF-IDF + LogReg ensemble (char + word n-grams, hard
negative mining, sigmoid calibration). Run *after* the cleaned corpus has
been built. For the transformer head, see `ml/train_transformer.py`.

Full pipeline from a fresh checkout:

    cd server && source venv/bin/activate
    python -m ml.data.synth_generator      # ~96k synthetic samples
    python -m ml.data.build_dataset        # merge synth + real → clean CSV
    python -m ml.train_mood_classifier     # train TF-IDF head (fast)
    python -m ml.train_transformer         # fine-tune DistilBERT (slow)
"""
from __future__ import annotations

from ml.mood_classifier import train_model


if __name__ == "__main__":
    summary = train_model()
    print("\n========================================")
    print(f"  accuracy : {summary['accuracy']}")
    print(f"  macro-F1 : {summary['macro_f1']}")
    print(f"  samples  : {summary['samples']}")
    print(f"  classes  : {len(summary['classes'])}")
    print("========================================\n")
