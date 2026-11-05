"""Tenant lookups and plan management."""
import db
from config import config
from utils.errors import NotFound, ApiError


def get(slug):
    conn = db.connect()
    try:
        row = conn.execute(
            "SELECT id, slug, display_name, plan FROM tenants WHERE slug = ?", (slug,)
        ).fetchone()
        if row is None:
            raise NotFound("tenant not found")
        return dict(row)
    finally:
        conn.close()


def list_all():
    conn = db.connect()
    try:
        return [dict(r) for r in conn.execute(
            "SELECT slug, display_name, plan FROM tenants ORDER BY slug")]
    finally:
        conn.close()


def set_plan(slug, plan):
    if plan not in config.PLAN_SEATS:
        raise ApiError("unknown plan")
    conn = db.connect()
    try:
        conn.execute("UPDATE tenants SET plan = ? WHERE slug = ?", (plan, slug))
        conn.commit()
    finally:
        conn.close()
    return {"slug": slug, "plan": plan}
