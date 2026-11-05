"""HTTP routes for accounts and beneficiaries."""
from flask import Blueprint, request, jsonify

from services import accounts
from utils.authn import require_account
from utils.errors import ApiError, as_response

bp = Blueprint("accounts", __name__)


@bp.get("/accounts/<number>/balance")
def balance(number):
    try:
        require_account(number)
        return jsonify(accounts.balance(number))
    except ApiError as err:
        body, status = as_response(err)
        return jsonify(body), status


@bp.post("/accounts/<number>/beneficiaries")
def add_beneficiary(number):
    data = request.get_json(force=True, silent=True) or {}
    try:
        require_account(number)
        # new beneficiaries always start unverified; verification is a separate,
        # out-of-band step and is never set from the request.
        res = accounts.add_beneficiary(
            number, data.get("name", ""), data.get("dest_number", ""),
            verified=False,
        )
    except ApiError as err:
        body, status = as_response(err)
        return jsonify(body), status
    return jsonify(res), 201
