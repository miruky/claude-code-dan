from db import conn

def get(mid: int):
    return conn().execute("SELECT id, email, role, note FROM members WHERE id = ?", (mid,)).fetchone()

def set_note(mid: int, note: str):
    c = conn(); c.execute("UPDATE members SET note = ? WHERE id = ?", (note, mid)); c.commit()

def set_role(mid: int, role: str):
    c = conn(); c.execute("UPDATE members SET role = ? WHERE id = ?", (role, mid)); c.commit()

def all_members():
    return conn().execute("SELECT id, email, role FROM members").fetchall()
