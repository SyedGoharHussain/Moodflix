# MoodFlix — PC Migration Handoff

> You are reading this on your new PC. The project was being developed on a MacBook M2 (Air-class thermals), and a long training run got killed mid-flight because the M2 was throttling and overheating. This document captures **what the project is**, **what was already done**, **what was left undone**, and **exact step-by-step setup instructions** so you can boot it up on the new rig and resume.
>
> New machine: **Ryzen 7 7700X / RTX 4060 Ti 8 gb/ 32 GB DDR5**. State on first read: only **VS Code** is installed. Nothing else. Treat this doc as the single source of truth for getting from zero → fully working dev environment → resuming the interrupted ML training.

REMEMBER TO USE NVIDIA GPU NOT MY AMD, MY AMD IS ONLY CPU OK RYZEN 7YTHINGSO CHECK THAT FIRST BEFORE DOING ANYTHING

---

## 1. What MoodFlix is

MoodFlix is an **AI-powered movie/TV recommendation engine driven by your mood**. The user types how they feel (or just emojis), an NLP model classifies that text into one of **16 mood categories**, and the backend fetches mood-matched titles from TMDB and explains *why* each was recommended.

- **Frontend:** React 18 + Vite + Tailwind + Framer Motion + Zustand. Firebase Auth (email + Google).
- **Backend:** Python 3 + Flask. Firebase Admin (Firestore for mood logs / user data). TMDB REST API for movies.
- **ML stack:** A **two-headed mood classifier** living at [server/ml/mood_classifier.py](server/ml/mood_classifier.py):
  1. **TF-IDF + Logistic Regression** ensemble (word + char n-grams, hard-negative mining, sigmoid calibration). Fast, ~15 MB pickle.
  2. **DistilBERT fine-tune** (16-class head). Higher accuracy on slang/typos/short inputs. **This is the one that didn't finish training on the M2.**
- **Explainability:** LIME explanations exposed via the `/api/analyze-mood` endpoint so the UI can highlight which of the user's words pushed the prediction. Implementation in [server/ml/lime_explainer.py](server/ml/lime_explainer.py).

The 16 canonical moods are: `happy, sad, lonely, romantic, excited, relaxed, stressed, dark, emotional, mind-bending, curious, nostalgic, motivated, adventurous, wholesome, scared`.

---

## 2. Current repo state (as of the last commit on M2)

Branch: `main`. Last commit: `413f411 model`. Several files are dirty (uncommitted) — these are the in-progress upgrades to the ML pipeline and the frontend redesign. **Do not stash or discard these — they are the work in progress.**

### What's already done & working
- Frontend redesign (Dashboard, Landing, Login, Register, Profile, Search, MovieDetail, Navbar, MoodInput, MovieCard, MovieCarousel, SkeletonCard, index.css, tailwind config). All uncommitted.
- Google auth + email signups (committed).
- Backend mood classifier rewritten from a tiny 243 KB TF-IDF model into a **15 MB ensemble pipeline** (char + word n-grams, hard-negative mining, calibration). Pickle is at [server/ml/models/mood_classifier.pkl](server/ml/models/mood_classifier.pkl) and is loadable today.
- Training corpus pipeline:
  - [server/ml/data/synth_generator.py](server/ml/data/synth_generator.py) — generates ~96k synthetic samples (6k/class) with formal/slang/typo/emoji style variation.
  - [server/ml/data/build_dataset.py](server/ml/data/build_dataset.py) — merges synthetic + dair-ai/emotion + go_emotions + hand-labeled CSVs + augmentation, normalizes to the 16 canonical labels, class-balances, writes [`mood_training_data_clean.csv`](server/ml/data/mood_training_data_clean.csv) (~96k rows).
  - [server/ml/data/augmentation.csv](server/ml/data/augmentation.csv) — hand-written extras for weak classes (adventurous, lonely, nostalgic, etc).
- TF-IDF training entrypoint: [server/ml/train_mood_classifier.py](server/ml/train_mood_classifier.py).
- LIME explainability hooked into [server/routes/recommendations.py](server/routes/recommendations.py) at the `/api/analyze-mood` route.
- Smoke test: [server/ml/smoke_test.py](server/ml/smoke_test.py) (33 fixed inputs covering formal/slang/Gen Z/emoji/typo cases, prints a hit-rate summary).

### What was interrupted — the DistilBERT fine-tune
- Script: [server/ml/train_transformer.py](server/ml/train_transformer.py).
- It was running on the M2 via MPS, **the laptop got too hot and was throttling**, the run was killed before saving artifacts.
- **There is no `server/ml/models/transformer/` directory yet.** That's the missing output — until it exists, the ensemble silently falls back to TF-IDF only (see `MoodClassifier._TransformerHead.available` in [mood_classifier.py:171](server/ml/mood_classifier.py#L171)).
- Once trained, the inference layer will automatically pick it up: it expects `pytorch_model.bin` / `model.safetensors`, `config.json`, tokenizer files, `label_encoder.json`, and `eval_report.json` inside `server/ml/models/transformer/`.

> **This is the #1 reason for the PC migration.** A 4060 Ti will eat this training job for breakfast — the M2 couldn't.

---

## 3. Files you need to bring over from the Mac

The repo is on git, so `git clone` covers most of it. But **secrets and a couple of artifacts are gitignored** and must be transferred manually (USB stick, AirDrop, scp, whatever):

| File | Why it's not in git | Where it goes on PC |
| --- | --- | --- |
| `server/.env` | gitignored, contains Flask/JWT secrets, TMDB API key | `server\.env` |
| `server/firebase_credentials.json` | gitignored (sensitive) | `server\firebase_credentials.json` |
| `firebase_credentials.json` (root) | gitignored duplicate — same content | `firebase_credentials.json` |
| `server/ml/data/mood_training_data_clean.csv` | ~96k rows, ~9 MB, not committed | `server\ml\data\mood_training_data_clean.csv` |
| `server/ml/data/synthetic_mood_data.csv` | ~96k rows, not committed | `server\ml\data\synthetic_mood_data.csv` |
| `server/ml/models/mood_classifier.pkl` | 15 MB, technically committed but worth verifying after clone | `server\ml\models\mood_classifier.pkl` |

> If you forget the synthetic / clean CSVs, you can regenerate them from scratch on the PC (it's slow but reproducible — see §6 below). The secrets you cannot regenerate without re-issuing them in Firebase / TMDB.

For reference, the current contents of `server/.env`:
```
FLASK_SECRET_KEY=MoodFlixProject
JWT_SECRET_KEY=MoodFlixProject
FIREBASE_CREDENTIALS_PATH=./firebase_credentials.json
TMDB_API_KEY=ce89a62614355ee2550d54b24aad090f
TMDB_BASE_URL=https://api.themoviedb.org/3
FLASK_ENV=development
FLASK_DEBUG=1
PORT=5001
```

(The TMDB key is already in the local `.env`. Firebase web config is hard-coded in [client/src/services/firebase.js](client/src/services/firebase.js) so the frontend doesn't need a separate env.)

---

## 4. PC setup from a fresh box (only VS Code installed)

Walk through this top-to-bottom. Most of it is a one-time install. Estimated wall-clock: **45–90 minutes**, dominated by CUDA + PyTorch downloads.

### 4.1 Install the base toolchain
1. **Git** — https://git-scm.com/download/win → install with default options. Make sure `git --version` works in PowerShell after.
2. **Python 3.11** (recommended; 3.10–3.12 also fine — avoid 3.13 because of some ML wheels) — https://www.python.org/downloads/windows/ → **tick "Add python.exe to PATH"** during install. Verify with `python --version`.
3. **Node.js LTS** (20.x or 22.x) — https://nodejs.org/ → installer adds it to PATH. Verify `node -v` and `npm -v`.
4. **NVIDIA GPU driver** — install the latest **Studio** or **Game Ready** driver for the RTX 4060 Ti from https://www.nvidia.com/Download/index.aspx. Reboot.

### 4.2 Install CUDA so PyTorch can see the GPU
You do **not** need to install the full CUDA Toolkit — PyTorch ships with its own CUDA runtime. You only need a recent driver (step 4.1 #4 above). Confirm the GPU is visible from PowerShell:
```powershell
nvidia-smi
```
You should see the 4060 Ti listed with its 16 GB VRAM. If you see nothing, fix the driver before continuing.

### 4.3 Clone the repo
```powershell
cd $HOME\Desktop
git clone <your-github-remote-or-bundle> moodflix
cd moodflix
```
(If you transferred the repo as a folder instead, just `cd` into it. Make sure `.git/` came along.)

Now drop in the secret files from §3 (`.env`, `firebase_credentials.json` in both server/ and root, and the two CSVs if you brought them).

### 4.4 Backend Python env
```powershell
cd server
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

That installs Flask, scikit-learn, pandas, NLTK, joblib, transformers, accelerate, lime, etc. **The `torch` line in `requirements.txt` will install the CPU-only build by default** — you do **not** want that. Override it with the CUDA build:

```powershell
pip uninstall -y torch
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

Verify CUDA is wired up:
```powershell
python -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'no gpu')"
```
Expected output something like: `2.4.1+cu121 True NVIDIA GeForce RTX 4060 Ti`.

### 4.5 Frontend npm deps
Open a second PowerShell tab:
```powershell
cd $HOME\Desktop\moodflix\client
npm install
```

### 4.6 Smoke-test the backend
With the Python venv activated:
```powershell
cd $HOME\Desktop\moodflix\server
python app.py
```
You should see Flask boot on `http://0.0.0.0:5001` and `[MoodClassifier] TF-IDF model loaded successfully.` If the transformer dir doesn't exist yet, it will log "transformer disabled" — that's fine, that's exactly the gap we're filling next.

Hit `http://localhost:5001/api/health` — should return `{"status":"ok"}`.

### 4.7 Smoke-test the frontend
```powershell
cd $HOME\Desktop\moodflix\client
npm run dev
```
Visit `http://localhost:5173`. Try logging in and typing a mood. The Vite proxy in [client/vite.config.js](client/vite.config.js) sends `/api/*` to `localhost:5001` so the backend must be running too.

---

## 5. The main job: finish the DistilBERT training on the 4060 Ti

This is what the M2 couldn't do. On the 4060 Ti with 16 GB VRAM, the same dataset (~96k rows, 16 classes, max_len=96, batch=32, 2 epochs) should finish in roughly **8–15 minutes** instead of hours of thermal-throttled MPS purgatory.

From `server/` with the venv active:
```powershell
python -m ml.train_transformer
```

Defaults (see `Args` in [train_transformer.py:46](server/ml/train_transformer.py#L46)):
- 2 epochs
- batch size 32
- lr 5e-5
- max_len 96
- model: `distilbert-base-uncased`

`_pick_device()` will return `cuda` automatically once the CUDA build of torch is installed.

**Recommended PC settings** (the M2 couldn't push these — your GPU can):
```powershell
python -m ml.train_transformer --epochs 3 --batch 64
```
Higher batch size + an extra epoch + GPU = better macro-F1 in less wall time. VRAM headroom on a 16 GB 4060 Ti is plenty for DistilBERT at batch 64 / max_len 96.

When the run finishes, it writes everything to `server\ml\models\transformer\`:
- `model.safetensors`, `config.json`
- Tokenizer files (`vocab.txt`, `tokenizer_config.json`, `special_tokens_map.json`)
- `label_encoder.json` — id ↔ mood mapping
- `eval_report.json` — accuracy / macro-F1 / per-class precision-recall

The next time you boot the Flask server, `MoodClassifier.__init__()` will see the directory, load the transformer head, and start blending it 65/35 with the TF-IDF voter automatically. No code changes needed.

### Verify the trained head
```powershell
python -m ml.smoke_test
```
Source column in the output should now read `ensemble` (transformer + TF-IDF) for most rows instead of `ml_model`. Hit-rate should jump materially compared to TF-IDF-only.

---

## 6. If you have to regenerate the training corpus from scratch

You only need this if you didn't carry over the two big CSVs from the Mac.

```powershell
cd $HOME\Desktop\moodflix\server
venv\Scripts\activate
python -m ml.data.synth_generator   # ~96k synthetic samples → synthetic_mood_data.csv
python -m ml.data.build_dataset     # merge with HF datasets → mood_training_data_clean.csv
python -m ml.train_mood_classifier  # retrain TF-IDF head (fast, ~1 min)
python -m ml.train_transformer      # then the DistilBERT fine-tune
```

`build_dataset.py` will download `dair-ai/emotion` and `go_emotions` from HuggingFace the first time — they're cached after that. No HF token needed for those.

---

## 7. Day-to-day dev commands (PC, copy-paste ready)

Two terminals — one for each side.

**Backend (PowerShell #1):**
```powershell
cd $HOME\Desktop\moodflix\server
venv\Scripts\activate
python app.py
```

**Frontend (PowerShell #2):**
```powershell
cd $HOME\Desktop\moodflix\client
npm run dev
```

**Open the app:** http://localhost:5173

**Retrain ML when you tweak data/code:**
```powershell
# from server/ with venv active
python -m ml.train_mood_classifier   # TF-IDF head (quick)
python -m ml.train_transformer       # DistilBERT head (uses GPU)
python -m ml.smoke_test              # sanity check predictions
```

---

## 8. Architectural map (so you don't have to dig)

```
moodflix/
├── client/                        # React + Vite frontend
│   ├── src/
│   │   ├── pages/                 # Landing, Login, Register, Dashboard, Profile, MovieDetail, Search
│   │   ├── components/            # MoodInput, MovieCard, MovieCarousel, Navbar, SkeletonCard
│   │   ├── services/firebase.js   # Firebase web config (hard-coded; not secret on client)
│   │   └── services/api.js        # axios client for backend
│   └── vite.config.js             # proxies /api → :5001
│
└── server/                        # Flask backend
    ├── app.py                     # entrypoint, blueprints, CORS, JWT, Firebase init
    ├── config.py                  # reads .env
    ├── .env                       # TMDB key, Flask/JWT secrets, port (PORT=5001)
    ├── firebase_credentials.json  # Firebase Admin SDK service account
    ├── routes/
    │   ├── auth.py                # signup/login
    │   ├── users.py               # profile + saved/liked
    │   └── recommendations.py     # POST /api/analyze-mood, GET /api/recommendations, /trending, /search, ...
    ├── services/
    │   ├── auth_service.py
    │   ├── firebase_service.py
    │   └── tmdb_service.py
    └── ml/
        ├── mood_classifier.py     # ensemble: transformer + TF-IDF + emoji + keyword fallback
        ├── recommendation_engine.py
        ├── lime_explainer.py      # LIME word-importance for /api/analyze-mood
        ├── explainability.py
        ├── train_mood_classifier.py    # TF-IDF training entrypoint
        ├── train_transformer.py        # DistilBERT fine-tune (the interrupted one)
        ├── smoke_test.py               # 33-case predict + hit-rate
        ├── models/
        │   ├── mood_classifier.pkl     # 15 MB TF-IDF ensemble
        │   └── transformer/            # ← will appear after the GPU training run
        └── data/
            ├── synth_generator.py            # generates synthetic_mood_data.csv
            ├── build_dataset.py              # merges everything → clean csv
            ├── mood_training_data.csv        # original ~764 hand-labeled rows
            ├── augmentation.csv              # weak-class hand extras
            ├── synthetic_mood_data.csv       # generator output, ~96k rows
            └── mood_training_data_clean.csv  # final training corpus, ~96k rows
```

---

## 9. Known gotchas worth keeping in mind

1. **`requirements.txt` ships `torch>=2.2,<2.5`** — that installs the CPU-only wheel by default on Windows. You MUST follow step 4.4 to reinstall it from the CUDA index URL, otherwise the GPU is wasted and training will be slower than the M2 was.
2. **Backend port is `5001`, not 5000.** Flask's default is 5000; the `.env` overrides it. The Vite proxy already points at 5001 — don't change one without changing the other.
3. **Two `firebase_credentials.json`** — one at repo root, one inside `server/`. Both are gitignored. Bring both. The backend reads the one inside `server/` (relative path in `.env`).
4. **TF-IDF model is committed** but it's 15 MB binary blob; if you ever delete it, regenerate via `python -m ml.train_mood_classifier`.
5. **Transformer head is optional at runtime.** The classifier checks `available` (label_encoder.json must exist). If you delete or move the dir, it silently falls back to TF-IDF.
6. **LIME only fires** when the prediction `source == "ml_model"` and the input is ≥4 words ([recommendations.py:33](server/routes/recommendations.py#L33)). When the transformer head is loaded, source becomes `"ensemble"` or `"transformer"`, so LIME will need a small update to also explain those — that's a follow-up task once training is done.
7. **CORS allows `http://localhost:5173` and `http://localhost:3000`** ([app.py:23](server/app.py#L23)). If you change the Vite port, also update this.
8. **Firestore writes** happen on every `/api/analyze-mood` call when a user is logged in — make sure the Firebase service account in the credentials file still has Firestore access (it should; this hasn't been changed in months).

---

## 10. TL;DR for the impatient

```powershell
# 1. install git, Python 3.11, Node LTS,

cd $HOME\Desktop\moodflix\server
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip uninstall -y torch
pip install torch --index-url https://download.pytorch.org/whl/cu121
python -c "import torch; print(torch.cuda.is_available())"   # must print True

cd ..\client
npm install

# 3. finish what the M2 couldn't:
cd ..\server
python -m ml.train_transformer --epochs 3 --batch 64
python -m ml.smoke_test

# 4. run the app
python app.py                # in one terminal
cd ..\client && npm run dev  # in another
# → open http://localhost:5173
```

Welcome to the new rig. The M2 is now relieved of its duties.
