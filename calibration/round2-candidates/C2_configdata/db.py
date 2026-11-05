import sqlite3

_conn = None

def conn():
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(":memory:", check_same_thread=False)
        _conn.row_factory = sqlite3.Row
        c = _conn
        c.execute("CREATE TABLE members(id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT, role TEXT, note TEXT)")
        # 既定メンバー。id=1 は管理者
        c.execute("INSERT INTO members(email, role, note) VALUES('admin@deskline.test','admin','')")
        c.execute("INSERT INTO members(email, role, note) VALUES('sup@deskline.test','support','')")
        c.commit()
    return _conn
