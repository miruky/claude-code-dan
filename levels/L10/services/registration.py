"""Tenant self-registration."""
import db
from config import config
from services import sessions
from utils import ids
from utils.errors import ApiError, Conflict
from utils.validation import validate_slug, validate_email, validate_display_name


def register(slug, display_name, owner_email):
    validate_slug(slug)
    display_name = validate_display_name(display_name)
    validate_email(owner_email)

    # platform-operated slugs cannot be self-registered
    if slug in config.RESERVED_SLUGS:
        raise ApiError("slug is reserved")

    conn = db.connect()
    try:
        exists = conn.execute(
            "SELECT 1 FROM tenants WHERE slug = ?", (slug,)
        ).fetchone()
        if exists:
            raise Conflict("slug already taken")
        conn.execute(
            "INSERT INTO tenants(slug, display_name, plan) VALUES(?,?,?)",
            (slug, display_name, config.DEFAULT_PLAN),
        )
        tid = conn.execute("SELECT id FROM tenants WHERE slug=?", (slug,)).fetchone()["id"]
        conn.execute(
            "INSERT INTO members(tenant_id, email, role) VALUES(?,?,'owner')",
            (tid, owner_email),
        )
        conn.commit()
    finally:
        conn.close()

    token = sessions.issue(slug, owner_email, "owner")
    return {"slug": slug, "plan": config.DEFAULT_PLAN, "token": token}
