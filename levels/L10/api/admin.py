"""Platform-admin-only routes (operated by the platform team)."""
from flask import Blueprint, request, jsonify

from services import tenants, authz
from utils.errors import ApiError, as_response

bp = Blueprint("admin", __name__)


def _token():
    a = request.headers.get("Authorization", "")
    return a[7:] if a.startswith("Bearer ") else ""


@bp.get("/admin/tenants")
def all_tenants():
    try:
        sess = authz.require_platform_admin(_token())
    except ApiError as err:
        body, status = as_response(err)
        return jsonify(body), status
    authz.record_admin_action(sess["slug"], "list_tenants")
    return jsonify({"tenants": tenants.list_all()})


@bp.post("/admin/tenants/<slug>/plan")
def set_plan(slug):
    try:
        sess = authz.require_platform_admin(_token())
    except ApiError as err:
        body, status = as_response(err)
        return jsonify(body), status
    data = request.get_json(force=True, silent=True) or {}
    try:
        res = tenants.set_plan(slug, data.get("plan", ""))
    except ApiError as err:
        body, status = as_response(err)
        return jsonify(body), status
    authz.record_admin_action(sess["slug"], f"set_plan:{slug}:{res['plan']}")
    return jsonify(res)
