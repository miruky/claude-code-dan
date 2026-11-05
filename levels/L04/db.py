import sqlite3

DB_PATH = "app.db"


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init():
    conn = connect()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            email TEXT UNIQUE,
            nickname TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS audit_log(
            id INTEGER PRIMARY KEY,
            actor TEXT,
            note TEXT
        );
        """
    )
    if conn.execute("SELECT COUNT(*) FROM audit_log").fetchone()[0] == 0:
        conn.execute(
            "INSERT INTO audit_log(actor, note) VALUES(?, ?)",
            ("system", "secret-internal-token=KQ19Z"),
        )
    conn.commit()
    conn.close()
