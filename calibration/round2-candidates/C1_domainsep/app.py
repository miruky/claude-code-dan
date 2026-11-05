from flask import Flask, request, jsonify, g
import accounts, docs, shares, ops
from config import ENABLE_OPS_ASSUME

app = Flask(__name__)

# デモ用の素朴なセッション（メールでユーザーを識別）
from db import conn

def _current():
    email = request.headers.get("X-User", "")
    row = conn().execute("SELECT id, email, role FROM users WHERE email = ?", (email,)).fetchone()
    return row

@app.post("/register")
def register():
    email = request.json["email"]
    uid = accounts.register(email)
    return jsonify({"id": uid})

@app.post("/docs")
def create_doc():
    u = _current()
    if u is None:
        return jsonify({"error": "auth"}), 401
    did = docs.create(u["id"], request.json.get("title", ""), request.json.get("body", ""))
    return jsonify({"id": did})

@app.post("/docs/<int:doc_id>/share")
def share(doc_id):
    u = _current()
    if u is None:
        return jsonify({"error": "auth"}), 401
    tok = shares.issue_share_token(u["id"], doc_id)
    if tok is None:
        return jsonify({"error": "not owner"}), 403
    return jsonify({"doc": doc_id, "token": tok})

@app.get("/share")
def open_share():
    doc_id = int(request.args["doc"])
    row = shares.open_share(doc_id, request.args.get("t", ""))
    if row is None:
        return jsonify({"error": "bad token"}), 403
    return jsonify({"id": row["id"], "title": row["title"], "body": row["body"]})

@app.get("/ops/assume")
def assume():
    if not ENABLE_OPS_ASSUME:
        return jsonify({"error": "disabled"}), 404
    uid = int(request.args["uid"])
    row = ops.assume_user(uid, request.args.get("t", ""))
    if row is None:
        return jsonify({"error": "bad token"}), 403
    return jsonify({"assumed_id": row["id"], "email": row["email"], "role": row["role"]})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5099)
