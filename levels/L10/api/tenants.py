"""Tenant self-service routes."""
from flask import Blueprint, request, jsonify

from services import registration, tenants, authz
from utils.errors import ApiError, as_response

bp = Blueprint("tenants", __name__)


def _token():
    a = request.headers.get("Authorization", "")
    return a[7:] if a.startswith("Bearer ") else ""


@bp.post("/tenants")
def register():
    data = request.get_json(force=True, silent=True) or {}
    try:
        res = registration.register(
            data.get("slug", ""), data.get("display_name", ""), data.get("owner_email", ""))
    except ApiError as err:
        body, status = as_response(err)
        return jsonify(body), status
    return jsonify(res), 201


@bp.get("/me")
def me():
    try:
        sess = authz.current(_token())
    except ApiError as err:
        body, status = as_response(err)
        return jsonify(body), status
    return jsonify({"slug": sess["slug"], "role": sess["role"],
                    "platform_admin": authz.is_platform_admin(sess)})
