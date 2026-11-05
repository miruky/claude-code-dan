"""User-facing account module. Handles sign-up and profile edits."""
from flask import Blueprint, request, jsonify
import db

bp = Blueprint("accounts", __name__)


def _valid_email(s):
    return "@" in s and len(s) <= 120


@bp.post("/signup")
def signup():
    data = request.get_json(force=True, silent=True) or {}
    email = (data.get("email") or "").strip()
    nickname = (data.get("nickname") or "").strip()
    if not _valid_email(email) or not nickname:
        return jsonify({"error": "email and nickname required"}), 400
    if len(nickname) > 60:
        return jsonify({"error": "nickname too long"}), 400
    conn = db.connect()
    try:
        cur = conn.execute(
            "INSERT INTO users(email, nickname) VALUES(?, ?)",
            (email, nickname),
        )
        conn.commit()
        return jsonify({"id": cur.lastrowid, "nickname": nickname})
    except Exception:
        return jsonify({"error": "email already registered"}), 409
    finally:
        conn.close()


@bp.put("/profile/<int:uid>")
def update_profile(uid):
    data = request.get_json(force=True, silent=True) or {}
    nickname = (data.get("nickname") or "").strip()
    if not nickname or len(nickname) > 60:
        return jsonify({"error": "invalid nickname"}), 400
    conn = db.connect()
    try:
        conn.execute("UPDATE users SET nickname = ? WHERE id = ?", (nickname, uid))
        conn.commit()
        return jsonify({"id": uid, "nickname": nickname})
    finally:
        conn.close()
