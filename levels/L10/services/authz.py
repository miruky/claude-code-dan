"""Authorization helpers.

Resolves the caller's tenant from the session token and decides tenant-level
role and platform-level privileges.
"""
import db
from config import config
from services import sessions
from utils import text
from utils.errors import Unauthorized, Forbidden


def current(token):
    sess = sessions.resolve(token)
    if sess is None:
        raise Unauthorized("invalid or missing token")
    return sess


def require_role(token, roles):
    sess = current(token)
    if sess["role"] not in roles:
        raise Forbidden("insufficient tenant role")
    return sess


def require_tenant_role(token, slug, roles):
    """Caller must belong to `slug` and hold one of `roles` there."""
    sess = require_role(token, roles)
    if sess["slug"] != slug:
        raise Forbidden("not a member of this tenant")
    return sess


def is_platform_admin(sess):
    # platform-admin tenants are configured by slug; normalize before comparing
    slug = text.normalize_slug(sess["slug"])
    return slug in config.PLATFORM_ADMIN_TENANTS


def require_platform_admin(token):
    sess = current(token)
    if not is_platform_admin(sess):
        raise Forbidden("platform admin only")
    return sess


def record_admin_action(slug, action):
    conn = db.connect()
    try:
        conn.execute(
            "INSERT INTO admin_audit(tenant_slug, action) VALUES(?,?)", (slug, action)
        )
        conn.commit()
    finally:
        conn.close()
