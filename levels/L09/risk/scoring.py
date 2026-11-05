"""Advisory risk scoring.

Produces a 0-100 score and a reason list for observability. The score is
attached to the transfer response and audit log; it never blocks or reviews a
transfer on its own (that is the gate's and the rules' job).
"""
from config import config

# weights per factor, tuned by the risk team
_W_AMOUNT = 35
_W_VELOCITY = 25
_W_NEW_BENEF = 20
_W_CROSS_CCY = 10
_W_ODD_HOUR = 10


def _amount_band(amount_minor):
    t = config.REVIEW_THRESHOLD_MINOR
    if amount_minor >= t * 10:
        return 1.0
    if amount_minor >= t:
        return 0.6
    if amount_minor >= t // 4:
        return 0.3
    return 0.0


def _velocity_band(used_minor):
    ratio = used_minor / max(1, config.DAILY_LIMIT_MINOR)
    return min(1.0, ratio)


def score(ctx):
    """ctx keys: amount_minor, used_minor, verified, cross_currency, hour."""
    reasons = []
    total = 0.0
    a = _amount_band(ctx["amount_minor"])
    if a:
        total += _W_AMOUNT * a
        reasons.append(f"amount:{a:.1f}")
    v = _velocity_band(ctx.get("used_minor", 0))
    if v:
        total += _W_VELOCITY * v
        reasons.append(f"velocity:{v:.2f}")
    if not ctx.get("verified", False):
        total += _W_NEW_BENEF
        reasons.append("new_beneficiary")
    if ctx.get("cross_currency"):
        total += _W_CROSS_CCY
        reasons.append("cross_currency")
    hour = ctx.get("hour", 12)
    if hour < 6 or hour >= 23:
        total += _W_ODD_HOUR
        reasons.append("odd_hour")
    return int(min(100, total)), reasons
