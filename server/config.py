"""
MoodFlix — Application Configuration
Centralizes all environment-based settings.
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""

    # Flask
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "moodflix-dev-secret-key")
    DEBUG = os.getenv("FLASK_DEBUG", "1") == "1"

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "moodflix-jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"

    # Firebase
    FIREBASE_CREDENTIALS_PATH = os.getenv(
        "FIREBASE_CREDENTIALS_PATH", "./firebase-credentials.json"
    )

    # TMDB
    TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
    TMDB_BASE_URL = os.getenv("TMDB_BASE_URL", "https://api.themoviedb.org/3")
    TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p"

    # Rate Limiting
    RATE_LIMIT_DEFAULT = 100  # requests per minute
    RATE_LIMIT_AUTH = 20  # auth requests per minute

    # ML Model Paths
    ML_MODEL_DIR = os.path.join(os.path.dirname(__file__), "ml", "models")
    ML_DATA_DIR = os.path.join(os.path.dirname(__file__), "ml", "data")


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}


def get_config():
    env = os.getenv("FLASK_ENV", "development")
    return config_map.get(env, DevelopmentConfig)
