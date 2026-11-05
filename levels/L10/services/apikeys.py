"""API key issuance (prefix stored; secret shown once)."""
import db
from services import tenants
from utils import ids


def create(slug, label):
    t = tenants.get(slug)
    prefix = ids.key_prefix()
    secret = ids.token(18)
    conn = db.connect()
    try:
        conn.execute(
            "INSERT INTO api_keys(tenant_id, label, prefix) VALUES(?,?,?)",
            (t["id"], label, prefix),
        )
        conn.commit()
    finally:
        conn.close()
    return {"slug": slug, "label": label, "prefix": prefix, "secret": f"{prefix}.{secret}"}


def list_keys(slug):
    t = tenants.get(slug)
    conn = db.connect()
    try:
        return [dict(r) for r in conn.execute(
            "SELECT label, prefix, created_at FROM api_keys WHERE tenant_id = ? ORDER BY id",
            (t["id"],))]
    finally:
        conn.close()
