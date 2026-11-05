from db import conn

# 新規ユーザーを登録します（既定ロールは member）
def register(email: str) -> int:
    c = conn()
    cur = c.execute("INSERT INTO users(email, role) VALUES(?, 'member')", (email,))
    c.commit()
    return cur.lastrowid

def get_user(uid: int):
    return conn().execute("SELECT id, email, role FROM users WHERE id = ?", (uid,)).fetchone()
