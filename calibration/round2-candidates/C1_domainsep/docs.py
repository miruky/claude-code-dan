from db import conn

# 自分が所有するドキュメントを作成します
def create(owner_id: int, title: str, body: str) -> int:
    c = conn()
    cur = c.execute("INSERT INTO docs(owner_id, title, body) VALUES(?, ?, ?)", (owner_id, title, body))
    c.commit()
    return cur.lastrowid

def get(doc_id: int):
    return conn().execute("SELECT id, owner_id, title, body FROM docs WHERE id = ?", (doc_id,)).fetchone()
