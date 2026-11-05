"""Tenant membership management with seat caps."""
import db
from config import config
from utils.errors import NotFound, Conflict, ApiError
from utils.validation import validate_email


def _tenant(conn, slug):
    row = conn.execute("SELECT id, plan FROM tenants WHERE slug = ?", (slug,)).fetchone()
    if row is None:
        raise NotFound("tenant not found")
    return row


def list_members(slug):
    conn = db.connect()
    try:
        t = _tenant(conn, slug)
        return [dict(r) for r in conn.execute(
            "SELECT email, role FROM members WHERE tenant_id = ? ORDER BY id", (t["id"],))]
    finally:
        conn.close()


def invite(slug, email, role="member"):
    validate_email(email)
    if role not in ("member", "owner", "billing"):
        raise ApiError("invalid role")
    conn = db.connect()
    try:
        # serialize concurrent invites so the seat-cap check and insert are atomic
        conn.isolation_level = None
        conn.execute("BEGIN IMMEDIATE")
        t = _tenant(conn, slug)
        count = conn.execute(
            "SELECT COUNT(*) AS c FROM members WHERE tenant_id = ?", (t["id"],)
        ).fetchone()["c"]
        cap = config.PLAN_SEATS.get(t["plan"], 3)
        if count >= cap:
            raise Conflict("seat limit reached for plan")
        dup = conn.execute(
            "SELECT 1 FROM members WHERE tenant_id = ? AND email = ?", (t["id"], email)
        ).fetchone()
        if dup:
            raise Conflict("member already exists")
        conn.execute(
            "INSERT INTO members(tenant_id, email, role) VALUES(?,?,?)",
            (t["id"], email, role),
        )
        conn.commit()
        return {"slug": slug, "email": email, "role": role}
    finally:
        conn.close()
