"""
MoodFlix — Rate Limiter Middleware
Simple in-memory rate limiting per IP address.
"""

import time
from functools import wraps
from flask import request, jsonify

_requests = {}


def rate_limit(max_requests=100, window_seconds=60):
    """Decorator to rate-limit a route."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            ip = request.remote_addr or "unknown"
            key = f"{ip}:{f.__name__}"
            now = time.time()

            if key not in _requests:
                _requests[key] = []

            # Clean old entries
            _requests[key] = [t for t in _requests[key] if now - t < window_seconds]

            if len(_requests[key]) >= max_requests:
                return jsonify({
                    "error": "Too many requests. Please try again later."
                }), 429

            _requests[key].append(now)
            return f(*args, **kwargs)
        return wrapped
    return decorator
