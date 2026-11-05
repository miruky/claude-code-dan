"""Caller authentication.

Each account has an opaque API token issued at onboarding. Routes that act on
an account require a matching bearer token. (In production this is the gateway's
job; here it is enforced in-process.)
"""
from flask import request

from config import config
from utils.errors import Unauthorized, Forbidden


def bearer():
    a = request.headers.get("Authorization", "")
    return a[len("Bearer "):].strip() if a.startswith("Bearer ") else ""


def require_account(number):
    tok = bearer()
    if not tok:
        raise Unauthorized("missing bearer token")
    expected = config.ACCOUNT_TOKENS.get(number)
    if expected is None or tok != expected:
        raise Forbidden("token does not match account")
    return number
