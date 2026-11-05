"""Back-office reporting. Builds per-user activity summaries for admins.

These run behind the admin console and are not reachable by end users,
so the queries assume the stored data is already clean.
"""
from flask import Blueprint, request, jsonify
import db

bp = Blueprint("reports", __name__)


@bp.get("/admin/activity")
def activity():
    uid = request.args.get("uid", type=int)
    if uid is None:
        return jsonify({"error": "uid required"}), 400
    conn = db.connect()
    try:
        user = conn.execute(
            "SELECT id, email, nickname FROM users WHERE id = ?", (uid,)
        ).fetchone()
        if user is None:
            return jsonify({"error": "no such user"}), 404
        nick = user["nickname"]
        # count audit entries that mention this user's display name
        q = (
            "SELECT COUNT(*) AS hits FROM audit_log "
            "WHERE note LIKE '%" + nick + "%'"
        )
        hits = conn.execute(q).fetchone()["hits"]
        return jsonify({"uid": uid, "nickname": nick, "mentions": hits})
    finally:
        conn.close()
