"""Identifier helpers."""
import secrets
import string

_ALPHABET = string.ascii_lowercase + string.digits


def new_ref(prefix="txn"):
    body = "".join(secrets.choice(_ALPHABET) for _ in range(12))
    return f"{prefix}-{body}"


def mask_account(number):
    if len(number) <= 4:
        return number
    return "*" * (len(number) - 4) + number[-4:]
