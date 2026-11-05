"""HTTP routes for transfers."""
from flask import Blueprint, request, jsonify

from services import transfers
from utils.authn import require_account
from utils.errors import ApiError, as_response

bp = Blueprint("transfers", __name__)


def _approver():
    tok = request.headers.get("X-Approver", "")
    return tok.strip()


@bp.post("/accounts/<src_number>/transfers")
def create(src_number):
    raw = request.get_data()
    payload = request.get_json(force=True, silent=True) or {}
    try:
        require_account(src_number)
        result = transfers.create_transfer(src_number, payload, raw, _approver())
    except ApiError as err:
        body, status = as_response(err)
        return jsonify(body), status
    return jsonify(result), 201


@bp.get("/accounts/<src_number>/transfers")
def history(src_number):
    try:
        require_account(src_number)
        rows = transfers.recent(src_number, request.args.get("limit", 20))
    except ApiError as err:
        body, status = as_response(err)
        return jsonify(body), status
    return jsonify(rows)
