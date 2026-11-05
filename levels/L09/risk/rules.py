"""Secondary risk rules applied during settlement.

These run after the hot-path gate and on the fully-parsed transfer. They are
intentionally conservative and may add friction (a review flag) but never
settle a transfer on their own.
"""
import re

from config import config

# destination patterns that are always blocked outright
_BLOCKED_DEST = re.compile(r"(?:^|[^0-9])(0{6,}|9{8,})(?:$|[^0-9])")

# crude sanctioned-name screen on the beneficiary label
_SANCTION_TERMS = ("ofac-test", "blocked-entity", "frozen-party")


def destination_blocked(dest_number):
    return bool(_BLOCKED_DEST.search(str(dest_number)))


def name_screened(beneficiary_name):
    low = (beneficiary_name or "").lower()
    return any(term in low for term in _SANCTION_TERMS)


def over_daily_limit(used_minor, amount_minor):
    return (used_minor + amount_minor) > config.DAILY_LIMIT_MINOR


def unverified_large_beneficiary(verified, amount_minor):
    # new, unverified beneficiaries are capped lower
    return (not verified) and amount_minor >= (config.REVIEW_THRESHOLD_MINOR * 5)


def collect_flags(ctx):
    """ctx: dict with dest_number, beneficiary_name, verified, used_minor, amount_minor."""
    flags = []
    if destination_blocked(ctx["dest_number"]):
        flags.append("dest_blocked")
    if name_screened(ctx.get("beneficiary_name", "")):
        flags.append("name_screened")
    if over_daily_limit(ctx["used_minor"], ctx["amount_minor"]):
        flags.append("daily_limit")
    if unverified_large_beneficiary(ctx.get("verified", False), ctx["amount_minor"]):
        flags.append("unverified_large")
    return flags
