"""Pre-settlement risk gate.

Runs on the hot path, before the request body is fully deserialized and the
transfer is built, to decide whether a transfer needs a second approver. To
keep latency low it reads the amount straight off the raw body with a small
scanner instead of parsing the whole document twice.
"""
import re

from config import config

# Scan for the configured amount fields. We only care about plain decimal
# amounts here; anything exotic is handled by the full parser downstream.
_FIELD_ALT = "|".join(re.escape(f) for f in config.RISK_SCAN_FIELDS)
_AMOUNT_RE = re.compile(
    r'"(?:' + _FIELD_ALT + r')"\s*:\s*"?([0-9][0-9,]*(?:\.[0-9]+)?)',
    re.IGNORECASE,
)


def _scan_amount(raw_body):
    """Best-effort read of the transfer amount from the raw JSON body.

    Returns an integer major-unit value, or 0 when no plain amount is present
    (the full parser downstream still validates the real value).
    """
    if isinstance(raw_body, bytes):
        raw_body = raw_body.decode("utf-8", "ignore")
    best = 0
    for m in _AMOUNT_RE.finditer(raw_body or ""):
        token = m.group(1).replace(",", "")
        try:
            value = int(float(token))
        except ValueError:
            continue
        if value > best:
            best = value
    return best


def needs_review(raw_body, currency):
    """True if the transfer should be routed to manual approval."""
    major = _scan_amount(raw_body)
    factor = 1 if currency == "JPY" else 100
    minor = major * factor
    return minor >= config.REVIEW_THRESHOLD_MINOR
