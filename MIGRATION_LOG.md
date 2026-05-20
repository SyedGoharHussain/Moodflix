# MoodFlix — PC Migration Log

A simple step-by-step log of what happened, from the dead MacBook to the trained model on the 4060 Ti.

---

## Where we started (the Mac problem)

The project was being built on a **MacBook Air M2**. Everything was going fine until the big ML job. The plan was to fine-tune **DistilBERT** on ~96,000 mood-labeled samples (16 classes) so the app could understand mood from short / slang / typo / emoji text.

On the M2 this job:
- ran on **MPS** (Apple's GPU layer)
- pushed the laptop into thermal throttling
- got **killed mid-run before saving anything**
- left `server/ml/models/transformer/` empty, so the app silently fell back to the weaker TF-IDF model only

That whole story is captured in [HANDOFF.md](HANDOFF.md) — it's the doc that came over with the project. The whole point of the handoff was: *"new PC, finish this DistilBERT run."*

The new machine: **Ryzen 7 7700X + RTX 4060 Ti (NVIDIA) + 32 GB DDR5**. (The Ryzen is AMD CPU only — the actual GPU is NVIDIA. This matters because PyTorch needs CUDA, which is NVIDIA-only.)

---

## What we did, in order

### 1. PyTorch + CUDA setup
The default `torch` from `requirements.txt` is the CPU-only Windows build. That would have wasted the GPU. So we:
- uninstalled the CPU torch
- reinstalled from `https://download.pytorch.org/whl/cu121`
- ended up on `torch 2.5.1+cu121`

Verified with a quick check:
```
torch: 2.5.1+cu121
CUDA available: True
GPU: NVIDIA GeForce RTX 4060 Ti
VRAM: 8 GB
```

> Side note: the handoff doc said "16 GB VRAM" — that's wrong. This is the 8 GB variant of the 4060 Ti. Still plenty for DistilBERT in FP16, just had to keep batch size at 32 instead of 64.

### 2. Node.js + frontend deps
The new PC didn't have Node installed at all. We:
- ran `winget install OpenJS.NodeJS.LTS --force` — got Node v24.15.0 / npm 11.12.1
- ran `npm install` inside `client/`
- 0 vulnerabilities, 249 packages audited

Frontend is now ready to `npm run dev`.

### 3. TF-IDF head (fast model)
Ran `python -m ml.train_mood_classifier` on the 96k-row cleaned dataset.

Steps inside the script:
- 76,031 train / 10,368 calib / 9,600 test split (stratified)
- word n-grams (1–2) + char n-grams (3–5), 80k features each
- LogisticRegression first pass
- **hard-negative mining**: 919 misclassified train rows upweighted ×3, refit
- sigmoid calibration on the held-out calib fold

Result:
```
accuracy : 0.8831
macro-F1 : 0.8840
```
Saved to [server/ml/models/mood_classifier.pkl](server/ml/models/mood_classifier.pkl) (16 MB).

> A small bug: the very last `print` in the training script uses a unicode arrow `→` which Windows' default cp1252 stdout can't encode, so the script crashed with a UnicodeEncodeError **after** the model was already saved to disk. Cosmetic only. Workaround for next time: `$env:PYTHONIOENCODING="utf-8"`.

### 4. DistilBERT head (the big one — what the Mac couldn't do)
Ran `python -m ml.train_transformer --epochs 3 --batch 32 --lr 5e-5 --max_len 96`.

Setup:
- device: **cuda** (the script's `_pick_device()` correctly chose the 4060 Ti)
- **AMP fp16** mixed precision: on
- 86,400 train / 9,600 test
- 2,700 steps per epoch × 3 epochs = 8,100 total steps

Loss curve (smoothed):

| step | loss |
|---|---|
| start | 2.83 |
| epoch 1 mid | 0.47 |
| epoch 1 end | 0.31 |
| epoch 2 end | 0.22 |
| epoch 3 end | 0.12 |

Eval accuracy after each epoch:

| epoch | accuracy | macro-F1 |
|---|---|---|
| 1 | 0.9155 | 0.9160 |
| 2 | 0.9207 | 0.9210 |
| **3 (final)** | **0.9221** | **0.9224** |

Saved to `server/ml/models/transformer/`:
- `model.safetensors` (256 MB)
- `config.json`, tokenizer files, `vocab.txt`
- `label_encoder.json` — 16-class id ↔ mood mapping
- `eval_report.json` — full per-class precision/recall

The whole run on the 4060 Ti took roughly **10 minutes**. On the M2 the same job had been running for hours and then died.

### 5. Smoke test (the ensemble in action)
Ran `python -m ml.smoke_test` — 35 fixed inputs covering formal, slang, Gen Z, emoji, typos, edge cases.

Every prediction now reports `source: ensemble` (transformer 65% + TF-IDF 35% blend) instead of `ml_model` (TF-IDF only). The transformer is actually loaded.

Result: **32 / 35 = 91.4%** hit rate.

The 3 misses are genuinely ambiguous:
- `"idk what to feel anymore"` → predicted **mind-bending**, expected sad (existential confusion is a fair read)
- `"how does the brain actually store memories"` → predicted **mind-bending**, expected curious (both are valid)
- `"watched my niece blow out her birthday candles, my heart"` → predicted **romantic** (low conf 0.26), expected wholesome (genuine miss, low confidence)

---

## Where we were vs. where we are

| Thing | On the Mac | On the PC |
|---|---|---|
| TF-IDF head | trained, 88% | trained, **88.31%** |
| DistilBERT head | **never finished, no artifacts** | **trained, 92.21% accuracy** |
| `server/ml/models/transformer/` | empty / missing | **populated, 256 MB checkpoint** |
| Inference source | falls back to `ml_model` (TF-IDF only) | **`ensemble`** (transformer + TF-IDF blend) |
| Smoke test hit rate | ~77% (TF-IDF only) | **91.4%** (32/35) |
| Frontend deps | installed on the Mac | installed fresh, 0 vulnerabilities |
| GPU utilization | thermal-throttled MPS, killed mid-run | **CUDA on RTX 4060 Ti**, AMP fp16, finished in ~10 min |

The 4060 Ti finished, in ten minutes, the exact training job the M2 couldn't complete in hours.

---

## How to run the app now

Two terminals.

**Backend:**
```powershell
cd C:\Users\xslay\Downloads\moodflix\moodflix\server
.\venv\Scripts\activate
python app.py
```
On startup you should now see:
```
[MoodClassifier] TF-IDF model loaded successfully.
[MoodClassifier] transformer loaded (cuda)
```
That second line is the new one — it didn't appear on the Mac because the file didn't exist.

**Frontend:**
```powershell
cd C:\Users\xslay\Downloads\moodflix\moodflix\client
npm run dev
```
Open http://localhost:5173.

---

## Small things to clean up later (not blocking)

1. The unicode `→` print in [server/ml/mood_classifier.py:471](server/ml/mood_classifier.py#L471) crashes Windows stdout. Either swap for `->` or set `PYTHONIOENCODING=utf-8` before training the TF-IDF head.
2. The `torch.cuda.amp.GradScaler(...)` call in [server/ml/train_transformer.py:160](server/ml/train_transformer.py#L160) is deprecated in torch 2.5 — works fine but warns. New form is `torch.amp.GradScaler('cuda', ...)`.
3. LIME explainability ([server/routes/recommendations.py:33](server/routes/recommendations.py#L33)) only fires when `source == "ml_model"`. Now that source is `ensemble`/`transformer`, LIME never runs. Small follow-up: widen that condition so the UI keeps getting word-importance highlights.

---

## TL;DR
- Old setup (Mac M2): DistilBERT couldn't finish, app ran on TF-IDF only.
- New setup (RTX 4060 Ti): DistilBERT trained in ~10 minutes, **92.21% accuracy**, ensemble smoke test **91.4%**.
- Frontend deps installed. Everything that was supposed to be done in [HANDOFF.md](HANDOFF.md) is done.
