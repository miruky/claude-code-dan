"""SQLite connection handling and the migration runner."""
import os
import sqlite3

from config import config

_MIGRATIONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "migrations")


def connect():
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _applied(conn):
    conn.execute(
        "CREATE TABLE IF NOT EXISTS _migrations(name TEXT PRIMARY KEY, at TEXT DEFAULT (datetime('now')))"
    )
    return {r["name"] for r in conn.execute("SELECT name FROM _migrations")}


def migrate():
    conn = connect()
    try:
        done = _applied(conn)
        for name in sorted(os.listdir(_MIGRATIONS_DIR)):
            if not name.endswith(".sql") or name in done:
                continue
            with open(os.path.join(_MIGRATIONS_DIR, name), encoding="utf-8") as fh:
                conn.executescript(fh.read())
            conn.execute("INSERT INTO _migrations(name) VALUES(?)", (name,))
            conn.commit()
    finally:
        conn.close()


def seed():
    """Insert a couple of demo accounts if the table is empty."""
    conn = connect()
    try:
        if conn.execute("SELECT COUNT(*) FROM accounts").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO accounts(number, owner, currency, balance_minor) VALUES(?,?,?,?)",
                [
                    ("JP-0001", "ops", "JPY", 1_000_000_000),
                    ("JP-0002", "treasury", "JPY", 5_000_000_000),
                ],
            )
            conn.commit()
    finally:
        conn.close()
