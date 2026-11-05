"""payflow - internal transfer service (loopback only).

Factory wires the account, transfer, and health blueprints over a local
SQLite database.
"""
from flask import Flask

import db
from api import transfers, accounts, health, statements


def create_app():
    app = Flask(__name__)
    app.register_blueprint(health.bp)
    app.register_blueprint(accounts.bp)
    app.register_blueprint(transfers.bp)
    app.register_blueprint(statements.bp)
    return app


app = create_app()


def bootstrap():
    db.migrate()
    db.seed()


if __name__ == "__main__":
    bootstrap()
    app.run(host="127.0.0.1", port=8109)
