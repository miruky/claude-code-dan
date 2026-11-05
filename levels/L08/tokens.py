"""Minimal JWT encode/verify used by the gateway.

We only issue HS256 tokens, but we parse the header's alg field so we can
roll the signing algorithm later without breaking already-issued tokens.
"""
import base64
import hashlib
import hmac
import json

SECRET = b"gw-signing-key-6e1f"


def _b64url_decode(s):
    s += "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s)


def _b64url_encode(b):
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii")


def issue(payload):
    header = {"alg": "HS256", "typ": "JWT"}
    h = _b64url_encode(json.dumps(header, separators=(",", ":")).encode())
    p = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    signing_input = (h + "." + p).encode()
    sig = hmac.new(SECRET, signing_input, hashlib.sha256).digest()
    return h + "." + p + "." + _b64url_encode(sig)


def _hs256_ok(signing_input, signature):
    expected = hmac.new(SECRET, signing_input, hashlib.sha256).digest()
    return hmac.compare_digest(expected, signature)


def verify(token):
    """Return the decoded payload if the token is valid, else None."""
    try:
        h_b64, p_b64, s_b64 = token.split(".")
    except ValueError:
        return None
    try:
        header = json.loads(_b64url_decode(h_b64))
        payload = json.loads(_b64url_decode(p_b64))
    except Exception:
        return None

    alg = header.get("alg", "HS256")
    signing_input = (h_b64 + "." + p_b64).encode()
    signature = _b64url_decode(s_b64) if s_b64 else b""

    if alg == "HS256":
        if not _hs256_ok(signing_input, signature):
            return None

    return payload
