"""
MoodFlix — DistilBERT fine-tuning for 16-class mood classification.

Fine-tunes `distilbert-base-uncased` on the balanced 96k-row corpus produced
by `ml/data/build_dataset.py`. Trains on Apple Silicon MPS when available,
falls back to CPU otherwise.

Saved artifacts (under `ml/models/transformer/`):
  - pytorch_model.bin / model.safetensors
  - config.json
  - tokenizer files (vocab.txt, tokenizer_config.json, special_tokens_map.json)
  - label_encoder.json      ← class index → mood string
  - eval_report.json        ← accuracy / macro-F1 / per-class report

Run:
    cd server && source venv/bin/activate
    python -m ml.train_transformer            # default: 2 epochs, batch 32
    python -m ml.train_transformer --epochs 3 --batch 64

The trained checkpoint is consumed by `ml.mood_classifier.MoodClassifier`
when present; if it isn't, the classifier falls back to the TF-IDF model.
"""
from __future__ import annotations

import argparse
import json
import os
import random
from dataclasses import dataclass
from contextlib import nullcontext

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(HERE, "data", "mood_training_data_clean.csv")
OUT_DIR = os.path.join(HERE, "models", "transformer")

MOOD_CATEGORIES = [
    "happy", "sad", "lonely", "romantic", "excited",
    "relaxed", "stressed", "dark", "emotional", "mind-bending",
    "curious", "nostalgic", "motivated", "adventurous",
    "wholesome", "scared",
]


@dataclass
class Args:
    epochs: int = 2
    batch: int = 32
    lr: float = 5e-5
    max_len: int = 96
    model_name: str = "distilbert-base-uncased"
    sample_per_class: int | None = None  # cap for quick runs (None = all)
    seed: int = 42


def _parse() -> Args:
    p = argparse.ArgumentParser()
    p.add_argument("--epochs", type=int, default=2)
    p.add_argument("--batch", type=int, default=32)
    p.add_argument("--lr", type=float, default=5e-5)
    p.add_argument("--max_len", type=int, default=96)
    p.add_argument("--model_name", default="distilbert-base-uncased")
    p.add_argument("--sample_per_class", type=int, default=None)
    p.add_argument("--seed", type=int, default=42)
    ns = p.parse_args()
    return Args(**vars(ns))


def _set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    import torch
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def _pick_device():
    import torch
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def _load_data(args: Args) -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df = df.dropna(subset=["text", "mood"])
    df["text"] = df["text"].astype(str).str.strip()
    df = df[df["text"].str.len() > 2]
    df = df[df["mood"].isin(MOOD_CATEGORIES)].reset_index(drop=True)

    if args.sample_per_class:
        parts = []
        for mood, grp in df.groupby("mood"):
            parts.append(grp.sample(n=min(args.sample_per_class, len(grp)),
                                    random_state=args.seed))
        df = pd.concat(parts, ignore_index=True)

    df = df.sample(frac=1.0, random_state=args.seed).reset_index(drop=True)
    return df


def _encode(texts, tokenizer, max_len: int):
    return tokenizer(
        list(texts),
        truncation=True,
        padding="max_length",
        max_length=max_len,
        return_tensors="pt",
    )


def train(args: Args) -> dict:
    import torch
    from torch.utils.data import DataLoader, TensorDataset
    from transformers import (
        AutoTokenizer,
        AutoModelForSequenceClassification,
        get_linear_schedule_with_warmup,
    )
    from sklearn.metrics import accuracy_score, f1_score, classification_report
    from sklearn.model_selection import train_test_split

    _set_seed(args.seed)
    device = _pick_device()
    use_amp = device.type == "cuda"
    print(f"[train] device: {device}")
    print(f"[train] amp: {'on' if use_amp else 'off'}")

    df = _load_data(args)
    print(f"[train] dataset: {len(df)} rows / {df['mood'].nunique()} classes")
    print(df["mood"].value_counts())

    # label encoding
    label_to_id = {m: i for i, m in enumerate(MOOD_CATEGORIES)}
    id_to_label = {i: m for m, i in label_to_id.items()}
    df["label"] = df["mood"].map(label_to_id)

    X_train, X_test, y_train, y_test = train_test_split(
        df["text"].tolist(),
        df["label"].tolist(),
        test_size=0.10,
        stratify=df["label"],
        random_state=args.seed,
    )
    print(f"[train] split: {len(X_train)} train / {len(X_test)} test")

    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        args.model_name,
        num_labels=len(MOOD_CATEGORIES),
        id2label=id_to_label,
        label2id=label_to_id,
    )
    model.to(device)
    scaler = torch.cuda.amp.GradScaler(enabled=use_amp)
    amp_context = torch.autocast(device_type="cuda", dtype=torch.float16) if use_amp else nullcontext()

    enc_train = _encode(X_train, tokenizer, args.max_len)
    enc_test = _encode(X_test, tokenizer, args.max_len)

    train_ds = TensorDataset(
        enc_train["input_ids"], enc_train["attention_mask"], torch.tensor(y_train),
    )
    test_ds = TensorDataset(
        enc_test["input_ids"], enc_test["attention_mask"], torch.tensor(y_test),
    )

    train_loader = DataLoader(train_ds, batch_size=args.batch, shuffle=True)
    test_loader = DataLoader(test_ds, batch_size=args.batch * 2)

    total_steps = len(train_loader) * args.epochs
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)
    scheduler = get_linear_schedule_with_warmup(
        optimizer, num_warmup_steps=int(0.06 * total_steps), num_training_steps=total_steps,
    )

    print(f"[train] {args.epochs} epoch(s), {len(train_loader)} steps/epoch")
    for epoch in range(args.epochs):
        model.train()
        running = 0.0
        for step, (ids, mask, labels) in enumerate(train_loader):
            ids, mask, labels = ids.to(device), mask.to(device), labels.to(device)
            optimizer.zero_grad()
            with amp_context:
                out = model(input_ids=ids, attention_mask=mask, labels=labels)
                loss = out.loss
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            scaler.step(optimizer)
            scaler.update()
            scheduler.step()
            running += loss.item()
            if step and step % 50 == 0:
                print(f"  epoch {epoch+1} step {step}/{len(train_loader)}  loss {running/50:.4f}")
                running = 0.0

        # quick eval after each epoch
        model.eval()
        preds, golds = [], []
        with torch.no_grad():
            for ids, mask, labels in test_loader:
                ids, mask = ids.to(device), mask.to(device)
                with amp_context:
                    logits = model(input_ids=ids, attention_mask=mask).logits
                preds.extend(torch.argmax(logits, dim=-1).cpu().tolist())
                golds.extend(labels.tolist())
        acc = accuracy_score(golds, preds)
        f1m = f1_score(golds, preds, average="macro")
        print(f"[eval] epoch {epoch+1}  acc={acc:.4f}  macro-f1={f1m:.4f}")

    # Final eval + report
    model.eval()
    preds, golds = [], []
    with torch.no_grad():
        for ids, mask, labels in test_loader:
            ids, mask = ids.to(device), mask.to(device)
            with amp_context:
                logits = model(input_ids=ids, attention_mask=mask).logits
            preds.extend(torch.argmax(logits, dim=-1).cpu().tolist())
            golds.extend(labels.tolist())

    acc = accuracy_score(golds, preds)
    f1m = f1_score(golds, preds, average="macro")
    target_names = [id_to_label[i] for i in range(len(MOOD_CATEGORIES))]
    report = classification_report(
        golds, preds, target_names=target_names, digits=3, output_dict=True,
    )
    print("\n[final]")
    print(f"  accuracy: {acc:.4f}")
    print(f"  macro-F1: {f1m:.4f}")
    print(classification_report(golds, preds, target_names=target_names, digits=3))

    os.makedirs(OUT_DIR, exist_ok=True)
    model.save_pretrained(OUT_DIR)
    tokenizer.save_pretrained(OUT_DIR)
    with open(os.path.join(OUT_DIR, "label_encoder.json"), "w") as f:
        json.dump({"id_to_label": id_to_label, "label_to_id": label_to_id}, f, indent=2)
    with open(os.path.join(OUT_DIR, "eval_report.json"), "w") as f:
        json.dump({"accuracy": acc, "macro_f1": f1m, "report": report}, f, indent=2)
    print(f"\n[saved] {OUT_DIR}")

    return {"accuracy": acc, "macro_f1": f1m}


if __name__ == "__main__":
    train(_parse())
