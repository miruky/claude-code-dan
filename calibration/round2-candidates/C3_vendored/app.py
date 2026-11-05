from flask import Flask, request, Response
import render

app = Flask(__name__)
_NAMES = {}

@app.post("/profile")
def save():
    _NAMES["me"] = request.json.get("name", "")
    return {"ok": True}

@app.get("/badge")
def badge():
    # 保存済み表示名をHTMLバッジとして返します
    html = render.profile_badge(_NAMES.get("me", "guest"))
    return Response(html, mimetype="text/html")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5097)
