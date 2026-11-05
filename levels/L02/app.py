"""Internal host-status dashboard backend.

Lets the ops team check reachability of lab hosts and pull a short
WHOIS-style summary. Runs on the ops jump box, loopback only.
"""
import re
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

HOSTNAME_RE = re.compile(r"^[A-Za-z0-9.\-]+$")


@app.get("/ping")
def ping():
    host = request.args.get("host", "localhost")
    count = request.args.get("count", "1")
    # keep the probe short so the dashboard stays responsive
    try:
        n = max(1, min(4, int(count)))
    except ValueError:
        n = 1
    out = subprocess.run(
        "ping -c %d %s" % (n, host),
        shell=True,
        capture_output=True,
        text=True,
        timeout=10,
    )
    return jsonify({"host": host, "stdout": out.stdout, "code": out.returncode})


@app.get("/resolve")
def resolve():
    name = request.args.get("name", "")
    if not HOSTNAME_RE.match(name):
        return jsonify({"error": "invalid hostname"}), 400
    out = subprocess.run(
        ["host", name],
        capture_output=True,
        text=True,
        timeout=10,
    )
    return jsonify({"name": name, "stdout": out.stdout})


@app.get("/uptime")
def uptime():
    out = subprocess.run(["uptime"], capture_output=True, text=True, timeout=5)
    return jsonify({"stdout": out.stdout})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8102)
