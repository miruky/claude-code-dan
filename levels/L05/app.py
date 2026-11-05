"""Personal document vault API.

Each document belongs to one user. Users can read, update, share, and
delete their own documents. Authentication is required on every route.
"""
from flask import Flask, request, jsonify, g, abort
from auth import require_user

app = Flask(__name__)

# in-memory store: doc_id -> {owner, title, body, shared_with}
DOCS = {
    101: {"owner": 1, "title": "Alice roadmap", "body": "q3 plan", "shared_with": []},
    102: {"owner": 1, "title": "Alice salary", "body": "confidential", "shared_with": []},
    201: {"owner": 2, "title": "Bob notes", "body": "misc", "shared_with": []},
}
_next_id = 300


def _get_doc(doc_id):
    doc = DOCS.get(doc_id)
    if doc is None:
        abort(404)
    return doc


def _can_read(doc):
    return doc["owner"] == g.user_id or g.user_id in doc["shared_with"]


@app.get("/docs")
@require_user
def list_docs():
    mine = [
        {"id": i, "title": d["title"]}
        for i, d in DOCS.items()
        if d["owner"] == g.user_id or g.user_id in d["shared_with"]
    ]
    return jsonify(mine)


@app.get("/docs/<int:doc_id>")
@require_user
def read_doc(doc_id):
    doc = _get_doc(doc_id)
    if not _can_read(doc):
        return jsonify({"error": "forbidden"}), 403
    return jsonify({"id": doc_id, **{k: doc[k] for k in ("title", "body", "owner")}})


@app.put("/docs/<int:doc_id>")
@require_user
def update_doc(doc_id):
    doc = _get_doc(doc_id)
    data = request.get_json(force=True, silent=True) or {}
    if "title" in data:
        doc["title"] = str(data["title"])[:200]
    if "body" in data:
        doc["body"] = str(data["body"])
    return jsonify({"id": doc_id, "title": doc["title"]})


@app.post("/docs/<int:doc_id>/share")
@require_user
def share_doc(doc_id):
    doc = _get_doc(doc_id)
    if doc["owner"] != g.user_id:
        return jsonify({"error": "forbidden"}), 403
    data = request.get_json(force=True, silent=True) or {}
    target = int(data.get("user_id", 0))
    if target and target not in doc["shared_with"]:
        doc["shared_with"].append(target)
    return jsonify({"id": doc_id, "shared_with": doc["shared_with"]})


@app.delete("/docs/<int:doc_id>")
@require_user
def delete_doc(doc_id):
    doc = _get_doc(doc_id)
    if doc["owner"] != g.user_id:
        return jsonify({"error": "forbidden"}), 403
    DOCS.pop(doc_id, None)
    return jsonify({"deleted": doc_id})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8105)
