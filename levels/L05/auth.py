"""Token authentication helpers.

Tokens are opaque strings issued at login and mapped to a user id.
Every protected route must resolve the caller with require_user().
"""
from functools import wraps
from flask import request, jsonify, g

# demo token table; real deployment loads these from the session store
TOKENS = {
    "tok-alice": 1,
    "tok-bob": 2,
}


def require_user(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization", "")
        if token.startswith("Bearer "):
            token = token[len("Bearer "):]
        uid = TOKENS.get(token)
        if uid is None:
            return jsonify({"error": "unauthorized"}), 401
        g.user_id = uid
        return fn(*args, **kwargs)

    return wrapper
