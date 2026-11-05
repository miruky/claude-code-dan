"""Generic request-shape validation helpers.

These check the *structure* of a request (required keys, string lengths,
currency codes). Numeric ranges and risk decisions live in the risk package.
"""
from utils.errors import ApiError

SUPPORTED_CURRENCIES = {"JPY", "USD", "EUR"}


def require_keys(payload, keys):
    missing = [k for k in keys if k not in payload or payload[k] in (None, "")]
    if missing:
        raise ApiError("missing fields: " + ", ".join(missing))


def check_currency(ccy):
    if ccy not in SUPPORTED_CURRENCIES:
        raise ApiError(f"unsupported currency: {ccy}")
    return ccy


def check_dest(number):
    n = str(number).strip()
    if not (3 <= len(n) <= 34):
        raise ApiError("invalid destination account")
    return n
