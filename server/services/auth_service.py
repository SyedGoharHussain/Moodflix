"""
MoodFlix — Authentication Service
Handles user registration, login, and password management.
"""

from datetime import datetime
import bcrypt
from services.firebase_service import (
    create_document,
    get_document,
    get_document_by_field,
    update_document,
)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def register_user(username: str, email: str, password: str) -> dict:
    """Register a new user. Returns user dict or error."""
    # Check if email already exists
    existing = get_document_by_field("users", "email", email)
    if existing:
        return {"error": "Email already registered.", "status": 409}

    # Check if username is taken
    existing_name = get_document_by_field("users", "username", username)
    if existing_name:
        return {"error": "Username already taken.", "status": 409}

    hashed = hash_password(password)
    now = datetime.utcnow().isoformat()

    user_data = {
        "username": username,
        "email": email,
        "password": hashed,
        "avatar": "",
        "bio": "",
        "favorite_genres": [],
        "mood_history": [],
        "created_at": now,
        "updated_at": now,
    }

    user_id = create_document("users", user_data)
    if not user_id:
        return {"error": "Failed to create user.", "status": 500}

    # Return user without password
    user_data.pop("password", None)
    user_data["id"] = user_id
    return {"user": user_data, "status": 201}


def login_user(email: str, password: str) -> dict:
    """Authenticate a user. Returns user dict or error."""
    user = get_document_by_field("users", "email", email)
    if not user:
        return {"error": "Invalid email or password.", "status": 401}

    if not verify_password(password, user.get("password", "")):
        return {"error": "Invalid email or password.", "status": 401}

    # Return user without password
    user.pop("password", None)
    return {"user": user, "status": 200}


def get_user_profile(user_id: str) -> dict | None:
    """Get user profile without password."""
    user = get_document("users", user_id)
    if user:
        user.pop("password", None)
    return user


def update_user_profile(user_id: str, data: dict) -> bool:
    """Update user profile fields."""
    # Never allow password update through this method
    data.pop("password", None)
    data["updated_at"] = datetime.utcnow().isoformat()
    return update_document("users", user_id, data)
