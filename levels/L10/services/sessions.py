"""In-memory session tokens (demo).

A token maps to the caller's tenant slug, email and tenant role. In production
this is backed by the session store; here a dict is enough to exercise the flow.
"""
from utils import ids

_SESSIONS = {}


def issue(slug, email, role):
    tok = ids.token()
    _SESSIONS[tok] = {"slug": slug, "email": email, "role": role}
    return tok


def resolve(token):
    if not token:
        return None
    return _SESSIONS.get(token)


def revoke(token):
    _SESSIONS.pop(token, None)
