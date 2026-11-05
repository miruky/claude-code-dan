"""Membership portal.

Combines the public account module and the back-office reporting module
behind one process. Loopback only.
"""
from flask import Flask
import db
import accounts
import reports

app = Flask(__name__)
app.register_blueprint(accounts.bp)
app.register_blueprint(reports.bp)


@app.get("/healthz")
def healthz():
    return {"ok": True}


if __name__ == "__main__":
    db.init()
    app.run(host="127.0.0.1", port=8104)
