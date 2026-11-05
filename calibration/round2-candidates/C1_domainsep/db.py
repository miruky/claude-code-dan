import sqlite3

_conn = None

def conn():
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(":memory:", check_same_thread=False)
        _conn.row_factory = sqlite3.Row
        _init(_conn)
    return _conn

def _init(c):
    c.executescript(
        """
        CREATE TABLE users(id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, role TEXT);
        CREATE TABLE docs(id INTEGER PRIMARY KEY AUTOINCREMENT, owner_id INTEGER, title TEXT, body TEXT);
        """
    )
    # プラットフォーム管理者を user id=1 として投入します
    c.execute("INSERT INTO users(email, role) VALUES(?, ?)", ("root@ledgerline.test", "admin"))
    c.commit()
