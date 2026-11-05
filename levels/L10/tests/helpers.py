import os
import tempfile


def fresh_db():
    os.environ["GATEKEEPER_DB"] = tempfile.mktemp(suffix=".db")


def client():
    fresh_db()
    import importlib
    import config as c; importlib.reload(c)
    import db, app as a
    importlib.reload(db); importlib.reload(a)
    a.bootstrap()
    return a.app.test_client()
