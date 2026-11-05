from flask import Flask, request, jsonify
import authz, members, loader
from db import conn

app = Flask(__name__)
_ENDPOINTS = loader.load_endpoints()

# デモ用セッション: X-Member にメンバーIDを入れると、そのロールで動作します
def _role_of(mid):
    row = members.get(mid)
    return row["role"] if row else None

def _require(method_path):
    mid = int(request.headers.get("X-Member", "0"))
    role = _role_of(mid)
    required = _ENDPOINTS[method_path]
    if role is None or not authz.has_perm(role, required):
        return None, (jsonify({"error": "forbidden", "need": required}), 403)
    return mid, None

@app.get("/members")
def list_members():
    mid, err = _require("GET  /members")
    if err: return err
    return jsonify([dict(r) for r in members.all_members()])

@app.post("/members/<int:mid>/note")
def add_note(mid):
    caller, err = _require("POST /members/<id>/note")
    if err: return err
    members.set_note(mid, request.json.get("note", ""))
    return jsonify({"ok": True})

@app.post("/members/<int:mid>/role")
def change_role(mid):
    caller, err = _require("POST /members/<id>/role")
    if err: return err
    members.set_role(mid, request.json["role"])
    return jsonify({"ok": True, "member": mid, "role": request.json["role"]})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5098)
