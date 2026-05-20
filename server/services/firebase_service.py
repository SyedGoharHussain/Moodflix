"""
MoodFlix — Firebase Service
Handles all Firestore database operations.
"""

import firebase_admin
from firebase_admin import credentials, firestore
from config import get_config

_db = None


def init_firebase():
    """Initialize Firebase Admin SDK."""
    global _db
    if _db is not None:
        return _db

    config = get_config()
    cred_path = config.FIREBASE_CREDENTIALS_PATH

    try:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        _db = firestore.client()
        print("[Firebase] Connected successfully.")
    except FileNotFoundError:
        print(f"[Firebase] Credentials file not found at: {cred_path}")
        print("[Firebase] Running in offline/mock mode.")
        _db = None
    except Exception as e:
        print(f"[Firebase] Initialization error: {e}")
        _db = None

    return _db


def get_db():
    """Get the Firestore client instance."""
    global _db
    if _db is None:
        init_firebase()
    return _db


# ---------------------------------------------------------------------------
# Generic CRUD helpers
# ---------------------------------------------------------------------------

def create_document(collection: str, data: dict, doc_id: str = None) -> str:
    """Create a document in the given collection. Returns the document ID."""
    db = get_db()
    if db is None:
        return None
    if doc_id:
        db.collection(collection).document(doc_id).set(data)
        return doc_id
    else:
        _, doc_ref = db.collection(collection).add(data)
        return doc_ref.id


def get_document(collection: str, doc_id: str) -> dict | None:
    """Get a single document by ID."""
    db = get_db()
    if db is None:
        return None
    doc = db.collection(collection).document(doc_id).get()
    if doc.exists:
        result = doc.to_dict()
        result["id"] = doc.id
        return result
    return None


def update_document(collection: str, doc_id: str, data: dict) -> bool:
    """Update fields on an existing document."""
    db = get_db()
    if db is None:
        return False
    db.collection(collection).document(doc_id).update(data)
    return True


def delete_document(collection: str, doc_id: str) -> bool:
    """Delete a document by ID."""
    db = get_db()
    if db is None:
        return False
    db.collection(collection).document(doc_id).delete()
    return True


def query_collection(
    collection: str,
    filters: list[tuple] = None,
    order_by: str = None,
    order_dir: str = "ASCENDING",
    limit: int = None,
) -> list[dict]:
    """
    Query a collection with optional filters.
    filters: list of (field, operator, value) tuples
    """
    db = get_db()
    if db is None:
        return []

    ref = db.collection(collection)

    if filters:
        for field, op, value in filters:
            ref = ref.where(field, op, value)

    if order_by:
        direction = (
            firestore.Query.DESCENDING
            if order_dir.upper() == "DESCENDING"
            else firestore.Query.ASCENDING
        )
        ref = ref.order_by(order_by, direction=direction)

    if limit:
        ref = ref.limit(limit)

    docs = ref.stream()
    results = []
    for doc in docs:
        item = doc.to_dict()
        item["id"] = doc.id
        results.append(item)
    return results


def get_document_by_field(collection: str, field: str, value) -> dict | None:
    """Find the first document matching field == value."""
    db = get_db()
    if db is None:
        return None
    docs = db.collection(collection).where(field, "==", value).limit(1).stream()
    for doc in docs:
        result = doc.to_dict()
        result["id"] = doc.id
        return result
    return None
