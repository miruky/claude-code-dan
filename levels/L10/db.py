"""SQLite connection and migration runner."""
import os
import sqlite3

from config import config

_MIGRATIONS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "migrations")


def connect():
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def migrate():
    conn = connect()
    try:
        conn.execute("CREATE TABLE IF NOT EXISTS _mig(name TEXT PRIMARY KEY)")
        done = {r["name"] for r in conn.execute("SELECT name FROM _mig")}
        for name in sorted(os.listdir(_MIGRATIONS)):
            if name.endswith(".sql") and name not in done:
                with open(os.path.join(_MIGRATIONS, name), encoding="utf-8") as fh:
                    conn.executescript(fh.read())
                conn.execute("INSERT INTO _mig(name) VALUES(?)", (name,))
                conn.commit()
    finally:
        conn.close()


def seed():
    """Create the platform-operated 'admin' tenant if missing."""
    conn = connect()
    try:
        if conn.execute("SELECT COUNT(*) FROM tenants WHERE slug='admin'").fetchone()[0] == 0:
            conn.execute(
                "INSERT INTO tenants(slug, display_name, plan) VALUES('admin','Platform','business')"
            )
            tid = conn.execute("SELECT id FROM tenants WHERE slug='admin'").fetchone()["id"]
            conn.execute(
                "INSERT INTO members(tenant_id, email, role) VALUES(?, 'ops@platform', 'owner')",
                (tid,),
            )
            conn.commit()
    finally:
        conn.close()
