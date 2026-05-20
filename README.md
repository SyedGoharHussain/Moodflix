# MoodFlix 🎬✨

MoodFlix is an AI-powered movie and TV show recommendation engine that curates content based on how you feel. Instead of mindlessly scrolling through genres, simply tell MoodFlix what your current mood is, and our custom NLP classifier will find the perfect movies to match your emotional state!

## 🌟 Features

- **AI Mood Detection**: Type how you feel (or drop some emojis!), and our built-in Machine Learning engine (TF-IDF + Logistic Regression) will categorize your mood across 16 different emotional spectrums.
- **Smart Recommendations**: Connects with TMDB to provide highly accurate, mood-aligned movie and TV show suggestions.
- **Explainable AI**: Gives you a detailed breakdown of *why* a movie was recommended to you based on your mood profile and genre preferences.
- **Seamless Authentication**: Sign in using your Email or safely via Google, powered by Firebase Authentication.
- **Beautiful UI**: A highly interactive, emotionally resonant interface built with React, Tailwind CSS, and Framer Motion.

## 🛠️ Tech Stack

### Frontend
- **Framework**: React 18 (Vite)
- **Styling**: Tailwind CSS & Framer Motion for animations
- **State Management**: Zustand
- **Routing**: React Router DOM
- **Authentication**: Firebase Client SDK

### Backend
- **Framework**: Python 3 & Flask
- **Machine Learning**: scikit-learn, joblib, pandas
- **Authentication & Database**: Firebase Admin SDK & Firestore
- **External APIs**: TMDB (The Movie Database) API

## 🚀 How to Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/moodflix.git
cd moodflix
```

### 2. Setup the Backend
```bash
cd server
python -m venv .venv
source .venv/Scripts/activate  # On Windows
pip install -r requirements.txt
```
*Note: Make sure to place your `firebase_credentials.json` in the `server` directory and set up your `.env` file with your TMDB API Key.*

### 3. Setup the Frontend
```bash
cd ../client
npm install
```
*Note: Ensure your Firebase config is set up in `client/src/services/firebase.js`.*

### 4. Run the App
**Start the backend server:**
```bash
cd server
python app.py
```

**Start the frontend development server:**
```bash
cd client
npm run dev
```

Visit `http://localhost:5173` in your browser and start exploring!

---
*Built with ❤️ for movie lovers everywhere.*