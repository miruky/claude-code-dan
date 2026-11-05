"""Identifier and token helpers."""
import secrets
import string

_ALPHA = string.ascii_lowercase + string.digits


def token(n=24):
    return secrets.token_urlsafe(n)


def key_prefix():
    return "gk_" + "".join(secrets.choice(_ALPHA) for _ in range(8))
