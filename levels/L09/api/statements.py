from flask import Blueprint, request, jsonify

from services import statements
from utils.authn import require_account
from utils.errors import ApiError, as_response

bp = Blueprint("statements", __name__)


@bp.get("/accounts/<number>/statement")
def statement(number):
    try:
        require_account(number)
        return jsonify(statements.monthly(number, request.args.get("month")))
    except ApiError as err:
        body, status = as_response(err)
        return jsonify(body), status
