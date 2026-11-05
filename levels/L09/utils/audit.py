"""Append-only audit log helper."""
import json

import db


def record(actor, action, detail):
    conn = db.connect()
    try:
        conn.execute(
            "INSERT INTO audit_log(actor, action, detail) VALUES(?,?,?)",
            (actor, action, json.dumps(detail, ensure_ascii=False)),
        )
        conn.commit()
    finally:
        conn.close()


def tail(limit=50):
    conn = db.connect()
    try:
        rows = conn.execute(
            "SELECT actor, action, detail, at FROM audit_log ORDER BY id DESC LIMIT ?",
            (int(limit),),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
