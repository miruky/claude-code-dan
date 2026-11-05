"""Membership and API-key routes (tenant owners/admins)."""
from flask import Blueprint, request, jsonify

from services import members, apikeys, authz
from utils.errors import ApiError, as_response

bp = Blueprint("members", __name__)


def _token():
    a = request.headers.get("Authorization", "")
    return a[7:] if a.startswith("Bearer ") else ""


@bp.get("/tenants/<slug>/members")
def list_members(slug):
    try:
        authz.require_tenant_role(_token(), slug, ("owner", "member", "billing"))
        return jsonify({"members": members.list_members(slug)})
    except ApiError as err:
        body, status = as_response(err)
        return jsonify(body), status


@bp.post("/tenants/<slug>/members")
def invite(slug):
    data = request.get_json(force=True, silent=True) or {}
    try:
        authz.require_tenant_role(_token(), slug, ("owner",))
        res = members.invite(slug, data.get("email", ""), data.get("role", "member"))
    except ApiError as err:
        body, status = as_response(err)
        return jsonify(body), status
    return jsonify(res), 201


@bp.post("/tenants/<slug>/keys")
def create_key(slug):
    data = request.get_json(force=True, silent=True) or {}
    try:
        authz.require_tenant_role(_token(), slug, ("owner",))
        res = apikeys.create(slug, data.get("label", "default"))
    except ApiError as err:
        body, status = as_response(err)
        return jsonify(body), status
    return jsonify(res), 201
