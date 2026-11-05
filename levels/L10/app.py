"""gatekeeper - multi-tenant control plane (loopback only)."""
from flask import Flask

import db
from api import tenants, admin, members, health


def create_app():
    app = Flask(__name__)
    app.register_blueprint(health.bp)
    app.register_blueprint(tenants.bp)
    app.register_blueprint(members.bp)
    app.register_blueprint(admin.bp)
    return app


app = create_app()


def bootstrap():
    db.migrate()
    db.seed()


if __name__ == "__main__":
    bootstrap()
    app.run(host="127.0.0.1", port=8110)
