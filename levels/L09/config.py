"""Runtime configuration for the payflow transfer service.

Values are read from the environment with sensible defaults so the service
boots in local and CI environments without extra setup.
"""
import os


def _int(name, default):
    try:
        return int(os.environ.get(name, default))
    except ValueError:
        return default


class Config:
    DB_PATH = os.environ.get("PAYFLOW_DB", "payflow.db")
    DEFAULT_CURRENCY = os.environ.get("PAYFLOW_CCY", "JPY")

    # Transfers at or above this amount (in minor units) require a second
    # approver before they settle.
    REVIEW_THRESHOLD_MINOR = _int("PAYFLOW_REVIEW_THRESHOLD", 100_000)

    # Hard ceiling; transfers above this are always rejected.
    MAX_TRANSFER_MINOR = _int("PAYFLOW_MAX_TRANSFER", 50_000_000)

    # Fields the pre-settlement risk gate inspects on the raw request body.
    # Kept narrow so the gate stays cheap on the hot path.
    RISK_SCAN_FIELDS = ("amount", "amount_minor")

    # Known approver tokens issued by the back-office console.
    APPROVER_TOKENS = {"appr-6f2a", "appr-9d71"}

    # Daily per-account velocity limit (minor units).
    DAILY_LIMIT_MINOR = _int("PAYFLOW_DAILY_LIMIT", 200_000_000)

    # Per-account API tokens (issued at onboarding).
    ACCOUNT_TOKENS = {"JP-0001": "acct-tok-ops", "JP-0002": "acct-tok-treasury"}


config = Config()
