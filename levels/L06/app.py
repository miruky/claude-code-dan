"""Dashboard service that restores per-client UI preferences.

The client sends its preferences blob back on each request; the server
decodes it and returns the resolved view settings. Loopback only.
"""
from flask import Flask, request, jsonify

import prefs

app = Flask(__name__)

DEFAULTS = {"theme": "light", "sort": "recent", "density": "comfortable"}


@app.get("/view")
def view():
    raw = request.cookies.get("prefs") or request.args.get("prefs", "")
    try:
        user_prefs = prefs.decode_prefs(raw)
    except Exception:
        user_prefs = {}
    resolved = dict(DEFAULTS)
    if isinstance(user_prefs, dict):
        for k in ("theme", "sort", "density"):
            if k in user_prefs:
                resolved[k] = user_prefs[k]
    return jsonify(resolved)


@app.post("/save")
def save():
    data = request.get_json(force=True, silent=True) or {}
    blob = prefs.encode_prefs({k: data.get(k) for k in DEFAULTS if k in data})
    resp = jsonify({"ok": True})
    resp.set_cookie("prefs", blob)
    return resp


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8106)
