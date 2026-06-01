# How to run MoodFlix (simple)

This file explains how to run the whole project (backend + frontend) in plain, simple steps.

Prerequisites
- Install Node (v18+), npm or yarn.
- Install Python 3.10+ and `pip`.
- Optional: `virtualenv` for Python virtual environments.

Quick steps — run backend then frontend

1) Backend (API)

- Open a terminal and go to the `server` folder:

```
cd server
```

- Create and activate a Python virtual environment:

```
python3 -m venv venv
source venv/bin/activate
```

- Install Python dependencies:

```
pip install -r requirements.txt
```

- Make sure the Firebase credentials file is available. The server looks for `firebase_credentials.json` by default in the `server` folder or a path set in the `FIREBASE_CREDENTIALS_PATH` env var. If you have a copy in the project root, copy it to `server/`:

```
cp ../firebase_credentials.json ./firebase_credentials.json
```

- Set the TMDB API key (replace YOUR_KEY):

```
export TMDB_API_KEY=YOUR_KEY
```

- Start the backend API (development):

```
python3 app.py
```

The API will be available at `http://localhost:5001` (health: `/api/health`).

> Note: macOS uses port 5000 for AirPlay Receiver, so the backend defaults to **5001**. Override with `PORT` if needed.

2) Frontend (client)

- In a new terminal, go to the `client` folder:

```
cd client
```

- Install node dependencies and start dev server:

```
npm install
npm run dev
```

The frontend dev server runs at `http://localhost:5173` by default.

3) Open the app in your browser
- Visit the frontend URL (usually `http://localhost:5173`) and the frontend will call the backend API at `http://localhost:5001`.

Extra notes / tips
- To change the backend port, set `PORT` before starting: `export PORT=8000`.
- For production with Gunicorn (example):

```
gunicorn 'app:create_app()' -w 4 -b 0.0.0.0:5001
```

- The project includes machine-learning requirements (PyTorch, transformers). Installing these may take extra time and may require a compatible GPU or specific wheels. If you only want the web app UI and basic API, you can still run the server but some ML endpoints may be slow or unavailable until the model dependencies are installed and the model files are in `server/ml/models`.

Where files live (helps):
- Backend entry: [server/app.py](server/app.py)
- Backend config: [server/config.py](server/config.py)
- Backend requirements: [server/requirements.txt](server/requirements.txt)
- Frontend package file: [client/package.json](client/package.json)

Troubleshooting
- If Firebase fails to initialize, check that `server/firebase_credentials.json` exists or set `FIREBASE_CREDENTIALS_PATH` env var to a full absolute path.
- If the frontend doesn't load, ensure `npm install` finished and open the console for errors.

I added a `Makefile` to simplify setup and running. Use these `make` commands on macOS:

Using Make (quick)

- Setup backend (creates venv and installs Python deps):

```
make setup-backend
```

- Setup frontend (installs Node deps):

```
make setup-frontend
```

- Start backend (runs `server/app.py` using `python3`):

```
make backend
```

- Start frontend (dev server):

```
make frontend
```

- Start both (backend runs in background, frontend in foreground):

```
make dev
```

Notes:
- If `make dev` doesn't stop cleanly, stop the backend with `pkill -f "python3 app.py"` or kill the PID found with `lsof`.
- The `Makefile` assumes `python3` is available on your PATH (macOS default).
