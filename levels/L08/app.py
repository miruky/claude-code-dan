"""API gateway with JWT-based access control.

Clients log in to receive a token, then present it as a Bearer token.
The /admin route additionally requires the admin role. Loopback only.
"""
from flask import Flask, request, jsonify

import tokens

app = Flask(__name__)

USERS = {"alice": ("pw-alice", "user"), "root": ("pw-root", "admin")}


@app.post("/login")
def login():
    data = request.get_json(force=True, silent=True) or {}
    u = data.get("username", "")
    p = data.get("password", "")
    rec = USERS.get(u)
    if rec is None or rec[0] != p:
        return jsonify({"error": "invalid credentials"}), 401
    return jsonify({"token": tokens.issue({"sub": u, "role": rec[1]})})


def _bearer():
    auth = request.headers.get("Authorization", "")
    return auth[7:] if auth.startswith("Bearer ") else ""


@app.get("/me")
def me():
    payload = tokens.verify(_bearer())
    if payload is None:
        return jsonify({"error": "unauthorized"}), 401
    return jsonify({"sub": payload.get("sub"), "role": payload.get("role")})


@app.get("/admin")
def admin():
    payload = tokens.verify(_bearer())
    if payload is None:
        return jsonify({"error": "unauthorized"}), 401
    if payload.get("role") != "admin":
        return jsonify({"error": "forbidden"}), 403
    return jsonify({"secret": "flag-admin-panel-open"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8108)
