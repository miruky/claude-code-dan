"""Exported-report file server.

Nightly jobs drop generated PDF/CSV reports under ./reports. This service
lets analysts download a report by name and upload a new template.
"""
import os
from flask import Flask, request, send_file, jsonify, abort
from werkzeug.utils import secure_filename

app = Flask(__name__)
REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates_store")
ALLOWED_EXT = {".pdf", ".csv", ".txt"}

# ensure the data directories exist when the service is imported
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)


@app.get("/download")
def download():
    name = request.args.get("name", "")
    if not name:
        abort(400)
    path = os.path.join(REPORTS_DIR, name)
    if not os.path.isfile(path):
        abort(404)
    return send_file(path, as_attachment=True)


@app.get("/template")
def template():
    # templates are addressed by a short id; we build the filename ourselves
    tid = request.args.get("id", "")
    if not tid.isalnum():
        abort(400)
    path = os.path.join(TEMPLATES_DIR, tid + ".html")
    if not os.path.isfile(path):
        abort(404)
    return send_file(path)


@app.post("/upload")
def upload():
    f = request.files.get("file")
    if f is None:
        abort(400)
    fname = secure_filename(f.filename or "")
    ext = os.path.splitext(fname)[1].lower()
    if not fname or ext not in ALLOWED_EXT:
        return jsonify({"error": "unsupported"}), 400
    os.makedirs(TEMPLATES_DIR, exist_ok=True)
    f.save(os.path.join(TEMPLATES_DIR, fname))
    return jsonify({"saved": fname})


if __name__ == "__main__":
    os.makedirs(REPORTS_DIR, exist_ok=True)
    os.makedirs(TEMPLATES_DIR, exist_ok=True)
    sample = os.path.join(REPORTS_DIR, "welcome.txt")
    if not os.path.exists(sample):
        with open(sample, "w") as fh:
            fh.write("sample report\n")
    app.run(host="127.0.0.1", port=8103)
